# src/etl_pipeline.py
import os
import pandas as pd
import cv2
import pytesseract
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys
import platform

# Only set the tesseract path on Windows
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract(image_dir, labels_path):
    # Load labels
    labels = pd.read_csv(labels_path)
    
    # Get image paths
    image_paths = [os.path.join(image_dir, fname) for fname in os.listdir(image_dir)]
    
    return image_paths, labels

def transform(image_paths, labels):
    processed_data = []
    total_images = len(image_paths)
    
    # Use tqdm to show real progress for each image
    for idx, path in enumerate(tqdm(image_paths, desc="Processing images", unit="img")):
        try:
            # Print progress for EACH image with explicit formatting for better visibility
            progress_msg = f"Processing image {idx+1}/{total_images} ({(idx+1)/total_images*100:.1f}%)"
            print(progress_msg, flush=True)  # Use print instead of tqdm.write with flush=True
            sys.stdout.flush()  # Force flush stdout to ensure immediate display
                
            # Image processing
            img = cv2.imread(path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # OCR text extraction
            text = pytesseract.image_to_string(Image.open(path))
            
            # Basic image metrics
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            
            processed_data.append({
                'image_path': path,
                'text': text.strip(),
                'image_size': img.shape,
                'histogram': hist.flatten().tolist(),
                **labels.iloc[idx].to_dict()
            })
            
            # Print completion message for this image - replaced Unicode checkmark with ASCII
            print(f"[OK] Completed image {idx+1}/{total_images}", flush=True)
            sys.stdout.flush()
            
        except Exception as e:
            print(f"Error processing {path} ({idx+1}/{total_images}): {str(e)}", flush=True)
            sys.stdout.flush()
    
    # Create DataFrame and clean column names
    df = pd.DataFrame(processed_data)
    # Clean column names by stripping whitespace
    df.columns = df.columns.str.strip()
    print(f"Processed {len(processed_data)}/{total_images} images successfully", flush=True)
    return df

def load(data, output_dir='data/processed'):
    os.makedirs(output_dir, exist_ok=True)
    
    # Try to save as parquet, fall back to CSV if necessary
    try:
        data.to_parquet(os.path.join(output_dir, 'processed_data.parquet'))
    except ImportError:
        print("Warning: pyarrow or fastparquet not available. Saving as CSV instead.")
        data.to_csv(os.path.join(output_dir, 'processed_data.csv'), index=False)
    
    # Visualization - find appropriate sentiment column
    plt.figure(figsize=(10, 6))
    
    # Look for sentiment columns with flexible matching
    sentiment_column = None
    for col in ['sentiment', 'overall_sentiment', 'sarcasm', 'offensive', 'motivational']:
        if col in data.columns:
            sentiment_column = col
            break
    
    if sentiment_column:
        data[sentiment_column].value_counts().plot(kind='bar')
        plt.title(f'{sentiment_column.capitalize()} Distribution')
    else:
        # Create a simple plot if no sentiment column is found
        plt.bar(['No sentiment data'], [1])
        plt.title('No sentiment data available')
    
    plt.savefig(os.path.join(output_dir, 'sentiment_distribution.png'))
    plt.close()  # Close the figure to free memory

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ETL Pipeline for Image Processing')
    parser.add_argument('--test', action='store_true', help='Run in test mode with small dataset')
    parser.add_argument('--sample', type=int, help='Only process specified number of images')
    args = parser.parse_args()
    
    if args.test:
        # Use test data
        print("Running ETL pipeline in test mode")
        image_dir = 'data/raw_test/images'
        labels_path = 'data/raw_test/labels_test.csv'
        output_dir = 'data/processed_test'
    else:
        # Use full data
        image_dir = 'data/raw/images'
        labels_path = 'data/raw/labels.csv'
        output_dir = 'data/processed'
    
    image_paths, labels = extract(image_dir, labels_path)
    
    # Apply sampling if requested
    if args.sample and len(image_paths) > args.sample:
        print(f"Sampling {args.sample} images from {len(image_paths)} total images")
        image_paths = image_paths[:args.sample]
        if len(labels) > args.sample:
            labels = labels.iloc[:args.sample]
    
    print(f"Processing {len(image_paths)} images...")
    processed_data = transform(image_paths, labels)
    print(f"Processed {len(processed_data)} images successfully")
    load(processed_data, output_dir)
    print("ETL pipeline completed")