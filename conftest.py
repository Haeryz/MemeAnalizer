import os
import sys
import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now we can import from the test package
from test.prepare_test_data import prepare_test_data

@pytest.fixture(scope="session", autouse=True)
def setup_test_data():
    """Set up test data before any tests run."""
    # Check if source data exists
    if not os.path.exists('data/raw/images') or not os.path.exists('data/raw/labels.csv'):
        pytest.skip("Source data not found. Make sure data/raw/images and data/raw/labels.csv exist.")
    
    # Prepare test data
    prepare_test_data()
    
    # Verify test data was created
    if not os.path.exists('data/raw_test/labels_test.csv'):
        pytest.fail("Failed to create test data.")