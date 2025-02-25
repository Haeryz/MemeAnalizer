import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter

def load_processed_data(data_path):
    """Load processed data from parquet or csv file"""
    if os.path.exists(os.path.join(data_path, 'processed_data.parquet')):
        return pd.read_parquet(os.path.join(data_path, 'processed_data.parquet'))
    elif os.path.exists(os.path.join(data_path, 'processed_data.csv')):
        return pd.read_csv(os.path.join(data_path, 'processed_data.csv'))
    else:
        raise FileNotFoundError(f"No processed data found in {data_path}")

def analyze_data(data_path, output_path):
    """Analyze processed data and create visualizations"""
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Load data
    try:
        df = load_processed_data(data_path)
        print(f"Loaded data with {len(df)} records")
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return
    
    # Save data summary stats
    with open(os.path.join(output_path, 'data_summary.txt'), 'w') as f:
        f.write(f"Dataset Overview:\n")
        f.write(f"Total records: {len(df)}\n")
        f.write(f"Columns: {', '.join(df.columns)}\n\n")
        
        f.write("Data Types:\n")
        f.write(str(df.dtypes))
        f.write("\n\n")
        
        # If sentiment exists, capture distribution
        if 'sentiment' in df.columns:
            f.write("Sentiment Distribution:\n")
            f.write(str(df['sentiment'].value_counts()))
            f.write("\n\n")
    
    # Create visualizations
    # 1. Sentiment distribution if available
    if 'sentiment' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.countplot(x='sentiment', data=df)
        plt.title('Sentiment Distribution')
        plt.savefig(os.path.join(output_path, 'sentiment_distribution.png'))
        plt.close()
    
    # 2. Word count distribution from text
    if 'text' in df.columns:
        word_counts = df['text'].str.split().apply(lambda x: len(x) if isinstance(x, list) else 0)
        plt.figure(figsize=(10, 6))
        sns.histplot(word_counts, bins=30)
        plt.title('Word Count Distribution')
        plt.xlabel('Number of Words')
        plt.savefig(os.path.join(output_path, 'word_count_distribution.png'))
        plt.close()
        
        # 3. Most common words
        try:
            # Remove rows with empty text
            text_data = df['text'].dropna()
            vectorizer = CountVectorizer(stop_words='english')
            X = vectorizer.fit_transform(text_data)
            words = vectorizer.get_feature_names_out()
            word_counts = X.sum(axis=0).A1
            word_freq = pd.DataFrame({'word': words, 'count': word_counts})
            top_words = word_freq.sort_values('count', ascending=False).head(20)
            
            plt.figure(figsize=(12, 8))
            sns.barplot(x='count', y='word', data=top_words)
            plt.title('Top 20 Words')
            plt.tight_layout()
            plt.savefig(os.path.join(output_path, 'top_words.png'))
            plt.close()
        except Exception as e:
            print(f"Error creating word frequency chart: {str(e)}")
    
    # 4. Image size distribution if available
    if 'image_size' in df.columns:
        try:
            # Extract height and width from image_size
            heights = []
            widths = []
            
            for size in df['image_size']:
                if isinstance(size, str):
                    # Handle string representation of tuple
                    size = eval(size)
                if isinstance(size, tuple) and len(size) >= 2:
                    heights.append(size[0])
                    widths.append(size[1])
            
            if heights and widths:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
                ax1.hist(heights, bins=20)
                ax1.set_title('Image Height Distribution')
                ax1.set_xlabel('Height (pixels)')
                
                ax2.hist(widths, bins=20)
                ax2.set_title('Image Width Distribution')
                ax2.set_xlabel('Width (pixels)')
                
                plt.tight_layout()
                plt.savefig(os.path.join(output_path, 'image_size_distribution.png'))
                plt.close()
        except Exception as e:
            print(f"Error creating image size distribution: {str(e)}")
    
    print(f"Analysis complete. Results saved to {output_path}")
    return df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Analyze processed data')
    parser.add_argument('--data-path', type=str, default='data/processed', 
                        help='Path to processed data directory')
    parser.add_argument('--output-path', type=str, default='data/analysis', 
                        help='Path to save analysis results')
    args = parser.parse_args()
    
    analyze_data(args.data_path, args.output_path)
