import os
import subprocess
import sys
import time
from pathlib import Path
import argparse
import threading
from tqdm import tqdm

def stream_output(process, debug=False):
    """Stream output from subprocess while keeping it separate from progress bar"""
    for line in process.stdout:
        if debug:
            # Print the line above the progress bar (tqdm will restore the progress bar after)
            tqdm.write(line.strip())

def run_command(command, description, show_progress=False, debug=False):
    """Run a shell command and print output with optional progress bar"""
    print(f"\n{'='*80}\n{description}\n{'='*80}")
    
    if show_progress:
        # Start the process
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, text=True, 
                                  bufsize=1, universal_newlines=True)
        
        # Setup output streaming thread if debug is enabled
        if debug:
            output_thread = threading.Thread(target=stream_output, args=(process, debug))
            output_thread.daemon = True
            output_thread.start()
        
        # Show progress bar
        with tqdm(total=100, desc=f"Running {description}", 
                 bar_format='{l_bar}{bar}| {elapsed}<{remaining}', 
                 position=0, leave=True) as pbar:
            
            completed = False
            while not completed:
                if process.poll() is not None:  # Process has finished
                    pbar.n = 100
                    pbar.refresh()
                    completed = True
                else:
                    # Update progress bar
                    if pbar.n < 95:  # Leave room for completion
                        pbar.update(1)
                    time.sleep(0.2)
            
            # Process finished, get remaining output
            stdout, stderr = process.communicate()
            
            if not debug:  # If we weren't already streaming output
                if stdout:
                    print(f"\nOutput:\n{stdout}")
            
            if stderr:
                print(f"\nERRORS/WARNINGS:\n{stderr}")
                
            return process.returncode == 0
    else:
        # Original behavior without progress bar
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if debug and result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"ERRORS/WARNINGS:\n{result.stderr}")
        return result.returncode == 0  # True if command succeeded

def estimate_completion_time(file_count, avg_time_per_file=0.5):
    """Estimate pipeline completion time based on file count"""
    total_seconds = file_count * avg_time_per_file
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

def run_pipeline(process_all=False, debug=False):
    """Run the entire ETL pipeline, tests, and analysis with progress tracking
    
    Args:
        process_all: Whether to process all images or just 10
        debug: Whether to show debug output
    """
    start_time = time.time()
    
    # Ensure directories exist
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('data/analysis', exist_ok=True)
    os.makedirs('data/test_analysis', exist_ok=True)
    
    # Count images to provide estimate
    image_count = 0
    try:
        if os.path.exists('data/raw/images'):
            image_count = len(os.listdir('data/raw/images'))
            
            if not process_all:
                print(f"\n🔍 Found {image_count} images, but will only process 10 images.")
                image_count = 10
                est_time = estimate_completion_time(image_count)
                print(f"Estimated processing time: {est_time}")
            else:
                print(f"\n🔍 Processing all {image_count} images.")
                est_time = estimate_completion_time(image_count)
                print(f"Estimated processing time: {est_time}")
        else:
            print("⚠️ Image directory not found at data/raw/images")
    except Exception as e:
        print(f"Couldn't count images: {str(e)}")
    
    # Step 1: Run ETL pipeline with progress bar
    print("\n🔄 Running ETL pipeline...")
    etl_command = 'python -m src.etl_pipeline'
    
    # Add sample flag if not processing all images
    if not process_all:
        etl_command += ' --sample 10'
        
    if run_command(etl_command, 'ETL PIPELINE EXECUTION', show_progress=True, debug=debug):
        print("✅ ETL pipeline completed successfully")
    else:
        print("❌ ETL pipeline failed")
        return False
    
    # Step 2: Run tests
    print("\n🧪 Running tests...")
    test_success = run_command('python -m pytest', 'TEST EXECUTION', debug=debug)
    if test_success:
        print("✅ All tests passed")
    else:
        print("❌ Some tests failed")
        return False
    
    # Step 3: Analyze production data with progress bar
    print("\n📊 Analyzing production data...")
    if run_command('python -m src.analyze_data --data-path data/processed --output-path data/analysis', 
                  'PRODUCTION DATA ANALYSIS', show_progress=True, debug=debug):
        print("✅ Production data analysis completed")
    else:
        print("❌ Production data analysis failed")
    
    # Step 4: Create test data for analysis (small subset)
    print("\n📊 Creating and analyzing test data...")
    run_command('python -m src.etl_pipeline --test', 'TEST DATA CREATION', debug=debug)
    run_command('python -m src.analyze_data --data-path data/processed_test --output-path data/test_analysis', 
               'TEST DATA ANALYSIS', debug=debug)
    
    total_time = time.time() - start_time
    minutes, seconds = divmod(total_time, 60)
    
    print(f"\n✨ Pipeline completed in {int(minutes)} minutes and {int(seconds)} seconds")
    print("\nOutput locations:")
    print("- Processed data: data/processed/")
    print("- Analysis results: data/analysis/")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the ETL pipeline with options")
    parser.add_argument("--all", action="store_true", help="Process all images instead of just 10")
    parser.add_argument("--debug", action="store_true", help="Show debug output")
    args = parser.parse_args()
    
    run_pipeline(process_all=args.all, debug=args.debug)
