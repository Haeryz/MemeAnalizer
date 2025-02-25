import os
import shutil
import pandas as pd

def prepare_test_data():
    # Create test directories
    os.makedirs('data/raw_test/images', exist_ok=True)
    
    # Copy first 10 images
    src_images = 'data/raw/images'
    dest_images = 'data/raw_test/images'
    
    for img in os.listdir(src_images)[:10]:
        shutil.copy(os.path.join(src_images, img), dest_images)
    
    # Create test labels
    labels = pd.read_csv('data/raw/labels.csv').head(10)
    labels.to_csv('data/raw_test/labels_test.csv', index=False)

if __name__ == '__main__':
    prepare_test_data()