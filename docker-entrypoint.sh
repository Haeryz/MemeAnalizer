#!/bin/bash
set -e

# Print Python and Tesseract versions for debugging
echo "Python version:"
python --version
echo "Tesseract version:"
tesseract --version

# Create necessary directories
mkdir -p /app/data/raw /app/data/processed /app/data/analysis /app/data/raw_test

# Check if MongoDB connection is configured (if warehouse flag is passed)
if [[ "$*" == *"--warehouse"* ]]; then
    echo "Checking MongoDB connection..."
    if [ -z "${MONGO_CONNECTION_STRING}" ]; then
        echo "WARNING: MONGO_CONNECTION_STRING environment variable not set."
        echo "Data will not be loaded to warehouse."
        # Remove warehouse flag from arguments
        set -- ${@/--warehouse/}
    else
        echo "MongoDB connection string detected."
        # Wait for MongoDB to be ready if using docker-compose
        if ping -c 1 mongodb &> /dev/null; then
            echo "Waiting for MongoDB to be ready..."
            for i in {1..30}; do
                if mongo --host mongodb --eval "print('connected')" &> /dev/null; then
                    echo "MongoDB is ready!"
                    break
                fi
                echo "Waiting... ($i/30)"
                sleep 1
            done
        fi
    fi
fi

# Run the pipeline script with the provided arguments
echo "Starting ETL pipeline with arguments: $@"
python run_pipeline.py "$@"

# Keep container running if in interactive mode
if [ -t 0 ]; then
    echo "Pipeline complete. Container kept alive for debugging."
    tail -f /dev/null
fi
