# src/visualization.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze():
    data = pd.read_parquet('/app/data/processed/processed_data.parquet')
    
    # Sentiment analysis
    plt.figure(figsize=(12, 8))
    sns.countplot(data=data, x='sentiment')
    plt.title('Meme Sentiment Analysis')
    
    # Text analysis
    word_counts = data['text'].str.split().apply(len)
    plt.figure(figsize=(10, 6))
    sns.histplot(word_counts, bins=30)
    plt.title('Text Length Distribution')
    
    # Save visualizations
    plt.savefig('/app/data/processed/analysis_results.png')

if __name__ == '__main__':
    analyze()