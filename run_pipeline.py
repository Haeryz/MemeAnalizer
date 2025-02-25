import os
import subprocess
import sys
import time
from pathlib import Path
from tqdm import tqdm

def run_command(command, description, show_progress=False):
    """Run a shell command and print output with optional progress bar"""
    print(f"\n{'='*80}\n{description}\n{'='*80}")
    
    if show_progress:
        # Create a progress bar that pulses to show activity
        with tqdm(total=100, desc=f"Running {description}", bar_format='{l_bar}{bar}| {elapsed}/{remaining}') as pbar:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                      text=True, bufsize=1, universal_newlines=True)
            
            # Simulate progress since we can't easily track actual progress
            for i in range(100):
                time.sleep(0.1)  # Update progress bar every 0.1 seconds
                pbar.update(1)
                
                # Check if process has completed
                if process.poll() is not None:
                    # Process finished, fill the bar to 100%
                    pbar.n = 100
                    pbar.refresh()
                    break
            
            stdout, stderr = process.communicate()
            
            # Print output after progress bar completes
            print(stdout)
            if stderr:
                print(f"ERRORS/WARNINGS:\n{stderr}")
                
            return process.returncode == 0
    else:
        # Original behavior without progress bar
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
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

def run_pipeline():
    """Run the entire ETL pipeline, tests, and analysis with progress tracking"""
    start_time = time.time()
    
    # Ensure directories exist
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('data/analysis', exist_ok=True)
    os.makedirs('data/test_analysis', exist_ok=True)
    
    # Count images to provide estimate
    image_count = 0
    try:
        image_count = len(os.listdir('data/raw/images'))
        est_time = estimate_completion_time(image_count)
        print(f"\n🔍 Found {image_count} images. Estimated processing time: {est_time}")
    except Exception as e:
        print(f"Couldn't count images: {str(e)}")
    
    # Step 1: Run ETL pipeline with progress bar
    print("\n🔄 Running ETL pipeline...")
    if run_command('python -m src.etl_pipeline', 'ETL PIPELINE EXECUTION', show_progress=True):
        print("✅ ETL pipeline completed successfully")
    else:
        print("❌ ETL pipeline failed")
        return False
    
    # Step 2: Run tests
    print("\n🧪 Running tests...")
    test_success = run_command('python -m pytest', 'TEST EXECUTION')
    if test_success:
        print("✅ All tests passed")
    else:
        print("❌ Some tests failed")
        return False
    
    # Step 3: Analyze production data with progress bar
    print("\n📊 Analyzing production data...")
    if run_command('python -m src.analyze_data --data-path data/processed --output-path data/analysis', 
                   'PRODUCTION DATA ANALYSIS', show_progress=True):
        print("✅ Production data analysis completed")
    else:
        print("❌ Production data analysis failed")
    
    # Step 4: Create test data for analysis (small subset)
    print("\n📊 Creating and analyzing test data...")
    run_command('python -m src.etl_pipeline --test', 'TEST DATA CREATION')
    run_command('python -m src.analyze_data --data-path data/processed_test --output-path data/test_analysis', 
                'TEST DATA ANALYSIS')
    
    total_time = time.time() - start_time
    minutes, seconds = divmod(total_time, 60)
    
    print(f"\n✨ Pipeline completed in {int(minutes)} minutes and {int(seconds)} seconds")
    print("\nOutput locations:")
    print("- Processed data: data/processed/")
    print("- Analysis results: data/analysis/")
    
    return True

if __name__ == "__main__":
    run_pipeline()
