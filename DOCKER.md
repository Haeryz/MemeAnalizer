# 🐳 Docker Deployment Guide

This guide explains how to run the ETL pipeline using Docker containers, which provides an isolated environment with all dependencies pre-installed.

## 📋 Requirements

- [Docker](https://www.docker.com/get-started) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0+)
- At least 4GB of free RAM
- At least 10GB of free disk space

## 🚀 Quick Start

1. Place your data in the correct locations:
   - Images in `./data/raw/images/`
   - Labels CSV file at `./data/raw/labels.csv`

2. Set up your MongoDB connection by creating a `.env` file:
   ```
   MONGO_CONNECTION_STRING=mongodb://root:example@mongodb:27017/
   ```

3. Run the Docker Compose stack:
   ```bash
   docker-compose up
   ```
   
4. Access MongoDB Express web interface at [http://localhost:8081](http://localhost:8081)

## 🔧 Configuration Options

You can customize the Docker deployment by modifying the `docker-compose.yml` file or by passing different command arguments:

### Running with Different Options

```bash
# Process all images and load to warehouse (default)
docker-compose up

# Only process 10 sample images
docker-compose run --rm etl-pipeline

# Run with debug output
docker-compose run --rm etl-pipeline --debug

# Run without loading to warehouse
docker-compose run --rm etl-pipeline --all --no-warehouse
```

### Scaling MongoDB Resources

For larger datasets, you might want to allocate more resources to MongoDB:

```yaml
mongodb:
  # Add these lines to docker-compose.yml under the mongodb service
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

## 📊 Data Persistence

Data is persisted through Docker volumes:

- MongoDB data is stored in the `mongodb_data` volume
- Your local `./data` directory is mounted inside the container

To reset all data and start from scratch:

```bash
docker-compose down -v
```

## 🔄 Development Workflow

For development, you can mount your code directories as volumes to reflect changes without rebuilding:

```bash
# Start MongoDB and Mongo Express only
docker-compose up mongodb mongo-express

# Run the ETL pipeline in development mode
docker-compose run --rm \
  -v ./src:/app/src \
  -v ./test:/app/test \
  etl-pipeline --debug
```

## 🔍 Troubleshooting

### Container Exits Immediately

Check the logs for errors:

```bash
docker-compose logs etl-pipeline
```

### MongoDB Connection Issues

1. Verify your `.env` file has the correct connection string
2. Ensure MongoDB container is running:
   ```bash
   docker-compose ps
   ```
3. Try connecting manually:
   ```bash
   docker-compose exec mongodb mongo -u root -p example
   ```

### Resource Constraints

If the container is crashing due to memory limits:

1. Increase Docker's memory allocation in Docker Desktop settings
2. Modify the deployment resources in docker-compose.yml:
   ```yaml
   etl-pipeline:
     deploy:
       resources:
         limits:
           memory: 4G
   ```

### Missing Data Directories

The entrypoint script creates necessary directories, but if you're still having issues:

```bash
docker-compose run --rm etl-pipeline bash -c "mkdir -p /app/data/raw /app/data/processed"
```

## 📜 Complete Example

Full example of running the pipeline with Docker:

```bash
# Clone repository
git clone <repository-url>
cd Data_Information_Knowledge/Tugas_1

# Prepare data directory
mkdir -p data/raw/images data/processed

# Copy your image files to data/raw/images/
# Copy your labels.csv to data/raw/labels.csv

# Create .env file
echo "MONGO_CONNECTION_STRING=mongodb://root:example@mongodb:27017/" > .env

# Start the stack
docker-compose up -d

# Check progress
docker-compose logs -f etl-pipeline

# Access MongoDB Express UI
# Open http://localhost:8081 in your browser

# Stop when finished
docker-compose down
```
