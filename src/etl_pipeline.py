# src/etl_pipeline.py
import os
import pandas as pd
import cv2
import pytesseract
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract(image_dir, labels_path):
    # Load labels
    labels = pd.read_csv(labels_path)
    
    # Get image paths
    image_paths = [os.path.join(image_dir, fname) for fname in os.listdir(image_dir)]
    
    return image_paths, labels

def transform(image_paths, labels):
    processed_data = []
    
    for idx, path in enumerate(image_paths):
        try:
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
            
        except Exception as e:
            print(f"Error processing {path}: {str(e)}")
    
    # Create DataFrame and clean column names
    df = pd.DataFrame(processed_data)
    # Clean column names by stripping whitespace
    df.columns = df.columns.str.strip()
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
    image_paths, labels = extract('data/raw/images', 'data/raw/labels.csv')
    processed_data = transform(image_paths, labels)
    load(processed_data)