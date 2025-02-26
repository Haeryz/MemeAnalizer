import os
import subprocess
import sys
import time
from pathlib import Path
import argparse
import threading
from tqdm import tqdm

def stream_output(process, description, debug=False):
    """Stream output from subprocess while keeping it separate from progress bar"""
    for line in process.stdout:
        if not line.strip():
            continue
            
        # Always print processing updates (more inclusive matching)
        if any(keyword in line for keyword in ["Processing", "Processed", "image", "images", "%"]):
            tqdm.write(f"[{description}] {line.strip()}")
        elif debug:
            # Print other debug lines
            tqdm.write(f"[{description}] {line.strip()}")
        else:
            # Print any other output that might be important
            tqdm.write(f"[{description}] {line.strip()}")

def run_command(command, description, show_progress=False, debug=False, long_running=False):
    """Run a shell command and print output with optional progress bar
    
    Args:
        command: The command to run
        description: Description of the command
        show_progress: Whether to show a progress bar
        debug: Whether to show debug output
        long_running: Whether this is a long-running command (slower progress bar)
    """
    print(f"\n{'='*80}\n{description}\n{'='*80}")
    
    if show_progress:
        # Start the process with unbuffered output
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout
            text=True,
            bufsize=0,  # Unbuffered
            universal_newlines=True
        )
        
        # Setup output streaming thread to show real progress
        output_thread = threading.Thread(target=stream_output, args=(process, description, debug))
        output_thread.daemon = True
        output_thread.start()
        
        # Adjust timing based on expected duration
        update_interval = 1.0 if long_running else 0.2
        max_progress = 85 if long_running else 95  # Leave more room for completion on long-running tasks
        
        # Show progress bar
        with tqdm(total=100, desc=f"Running {description}", 
                 bar_format='{l_bar}{bar}| {elapsed}<{remaining} {postfix}', 
                 position=0, leave=True) as pbar:
            
            # Set initial postfix
            pbar.set_postfix_str("Starting...")
            
            start_time = time.time()
            completed = False
            last_progress = 0
            
            while not completed:
                if process.poll() is not None:  # Process has finished
                    pbar.n = 100
                    pbar.set_postfix_str("Complete!")
                    pbar.refresh()
                    completed = True
                else:
                    # Calculate progress differently for long-running processes
                    # Use elapsed time to estimate progress
                    elapsed = time.time() - start_time
                    
                    if long_running:
                        # For long-running processes, progress more slowly
                        # Estimate based on expected duration (roughly 0.5s per image for 7000 images = ~1 hour)
                        estimated_total = 3600  # 1 hour in seconds (adjust for your dataset)
                        progress = min(max_progress, int((elapsed / estimated_total) * max_progress))
                    else:
                        # For shorter processes, progress more quickly
                        progress = min(max_progress, int(elapsed / update_interval) + last_progress)
                    
                    # Only update if progress has changed
                    if progress > pbar.n:
                        pbar.update(progress - pbar.n)
                        last_progress = progress
                        
                    # Update the postfix to show activity even when progress bar doesn't move
                    if elapsed > 10 and long_running:
                        minutes, seconds = divmod(elapsed, 60)
                        pbar.set_postfix_str(f"Running for {int(minutes)}m {int(seconds)}s")
                    
                    time.sleep(update_interval)
            
            # Process finished, get remaining output
            stdout, stderr = process.communicate()
            
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
        process_all: Whether to process 1000 images or just 10
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
            total_images = len(os.listdir('data/raw/images'))
            
            if not process_all:
                print(f"\n🔍 Found {total_images} images, but will only process 10 images.")
                image_count = 10
                est_time = estimate_completion_time(image_count)
                print(f"Estimated processing time: {est_time}")
            else:
                # Cap at 1000 images
                image_count = min(1000, total_images)
                print(f"\n🔍 Processing {image_count} images out of {total_images} total images.")
                est_time = estimate_completion_time(image_count)
                print(f"Estimated processing time: {est_time}")
        else:
            print("⚠️ Image directory not found at data/raw/images")
    except Exception as e:
        print(f"Couldn't count images: {str(e)}")
    
    # Step 1: Run ETL pipeline with progress bar
    print("\n🔄 Running ETL pipeline...")
    etl_command = 'python -m src.etl_pipeline'
    
    # Add sample flag based on processing mode
    if not process_all:
        etl_command += ' --sample 10'
        long_running = False
    else:
        etl_command += f' --sample {image_count}'
        long_running = True
        
    if run_command(etl_command, 'ETL PIPELINE EXECUTION', show_progress=True, debug=debug, long_running=long_running):
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
