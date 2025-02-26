# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-eng \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements files and install dependencies
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN if [ -f requirements_warehouse.txt ]; then pip install --no-cache-dir -r requirements_warehouse.txt; fi

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/processed /app/data/analysis /app/test

# Copy source code
COPY src/ /app/src/
COPY test/ /app/test/
COPY run_pipeline.py /app/
COPY .env /app/.env

# Set the entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["--all", "--warehouse"]