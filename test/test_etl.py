# tests/test_etl.py
import os
import pytest
import pandas as pd
from src.etl_pipeline import extract, transform, load

@pytest.fixture
def test_data():
    return {
        'image_dir': 'data/raw_test/images',
        'labels_path': 'data/raw_test/labels_test.csv'
    }

def test_extract(test_data):
    image_paths, labels = extract(test_data['image_dir'], test_data['labels_path'])
    
    # Check that we have data
    assert len(image_paths) > 0
    assert not labels.empty
    
    # Check that the image files exist
    for path in image_paths:
        assert os.path.exists(path)

def test_transform(test_data):
    image_paths, labels = extract(test_data['image_dir'], test_data['labels_path'])
    processed = transform(image_paths, labels)
    
    # Check that DataFrame was created with all rows
    assert len(processed) == len(image_paths)
    
    # Check expected columns (with clean names)
    expected_columns = ['image_path', 'text', 'image_size', 'histogram']
    for col in expected_columns:
        assert col in processed.columns
    
    # Check column names are cleaned (no extra spaces)
    for col in processed.columns:
        assert col == col.strip(), f"Column '{col}' has extra whitespace"

def test_load(test_data, tmpdir):
    image_paths, labels = extract(test_data['image_dir'], test_data['labels_path'])
    processed = transform(image_paths, labels)

    # Use pytest tmpdir for output
    output_path = str(tmpdir.mkdir("processed_test"))
    load(processed, output_path)
    
    # Check if either parquet or CSV file was created
    assert os.path.exists(os.path.join(output_path, 'processed_data.parquet')) or \
           os.path.exists(os.path.join(output_path, 'processed_data.csv'))
    assert os.path.exists(os.path.join(output_path, 'sentiment_distribution.png'))