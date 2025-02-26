#!/bin/bash

# Build and run the Docker services
echo "Starting ETL pipeline in Docker..."

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Creating .env file from .env.example..."
        cp .env.example .env
        echo "Please update the .env file with your MongoDB connection string."
        echo "Press Enter to continue or Ctrl+C to exit and update .env first."
        read -p ""
    else
        echo "ERROR: .env.example file not found."
        exit 1
    fi
fi

# Build and run with docker-compose
docker-compose up --build

# Check exit status
if [ $? -eq 0 ]; then
    echo "Pipeline completed. View results in the ./data directory."
else
    echo "Pipeline failed. Check logs for errors."
fi
