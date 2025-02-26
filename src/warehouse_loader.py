import pandas as pd
import pymongo
import os
import json
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_to_mongodb():
    """Connect to MongoDB Atlas using credentials from environment variables"""
    connection_string = os.getenv('MONGO_CONNECTION_STRING')
    if not connection_string:
        raise ValueError("MongoDB connection string not found in environment variables")
    
    client = pymongo.MongoClient(connection_string)
    return client

def load_to_warehouse(data_path, collection_name='processed_data'):
    """Load processed data into MongoDB data warehouse
    
    Args:
        data_path: Path to the processed data directory
        collection_name: Name of the collection to store data in
    """
    try:
        # Load data from parquet or csv
        if os.path.exists(os.path.join(data_path, 'processed_data.parquet')):
            df = pd.read_parquet(os.path.join(data_path, 'processed_data.parquet'))
            print(f"Loaded {len(df)} records from parquet file")
        elif os.path.exists(os.path.join(data_path, 'processed_data.csv')):
            df = pd.read_csv(os.path.join(data_path, 'processed_data.csv'))
            print(f"Loaded {len(df)} records from CSV file")
        else:
            raise FileNotFoundError(f"No processed data found in {data_path}")
        
        # Connect to MongoDB
        client = connect_to_mongodb()
        db = client.get_database('meme_data_warehouse')
        collection = db[collection_name]
        
        # Convert DataFrame to list of dictionaries for MongoDB
        # Handle complex data types like numpy arrays or lists
        records = json.loads(df.to_json(orient='records', date_format='iso'))
        
        # MongoDB insert operation
        print(f"Uploading {len(records)} records to MongoDB collection '{collection_name}'...")
        
        # Use bulk insert for better performance
        try:
            result = collection.insert_many(records)
            print(f"Successfully uploaded {len(result.inserted_ids)} records")
        except BulkWriteError as bwe:
            print(f"Error during bulk write: {bwe.details}")
            successful = bwe.details['nInserted']
            print(f"Successfully inserted {successful} records before the error")
        
        # Create indexes for common query fields
        collection.create_index('sentiment')
        print("Created index on 'sentiment' field")
        
        return True
        
    except Exception as e:
        print(f"Error loading data to warehouse: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Load processed data into data warehouse')
    parser.add_argument('--data-path', type=str, default='data/processed', 
                        help='Path to processed data directory')
    parser.add_argument('--collection', type=str, default='processed_data',
                        help='MongoDB collection name')
    args = parser.parse_args()
    
    load_to_warehouse(args.data_path, args.collection)
