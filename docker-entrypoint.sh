#!/bin/bash

# Print Python version
python --version

# Wait for MongoDB if we're using warehouse loading
if [[ "$*" == *"--warehouse"* ]]; then
    echo "Waiting for MongoDB connection..."
    python -c "
import time
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
conn_str = os.getenv('MONGO_CONNECTION_STRING')

max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        client = MongoClient(conn_str, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print('MongoDB connection successful')
        break
    except Exception as e:
        retry_count += 1
        print(f'MongoDB connection attempt {retry_count}/{max_retries} failed: {e}')
        if retry_count >= max_retries:
            print('Could not connect to MongoDB after maximum retries')
            exit(1)
        time.sleep(2)
"
fi

# Run the pipeline with the provided arguments
echo "Starting ETL pipeline..."
python run_pipeline.py "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "Pipeline completed successfully!"
else
    echo "Pipeline failed with exit code $exit_code"
fi

exit $exit_code
