# 📊 Image Data ETL Pipeline & Analysis

![Pipeline Status](https://img.shields.io/badge/status-operational-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A comprehensive ETL (Extract, Transform, Load) pipeline for processing image data with text extraction, sentiment analysis, and data warehousing capabilities.

## 🔍 Table of Contents

- [Overview](#-overview)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Data Setup](#data-setup)
  - [MongoDB Configuration](#mongodb-configuration)
- [Usage](#-usage)
  - [Running the Pipeline](#running-the-pipeline)
  - [Docker Deployment](#docker-deployment)
  - [Command Options](#command-options)
- [Pipeline Workflow](#-pipeline-workflow)
- [Output & Analysis](#-output--analysis)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 📋 Overview

This project implements a complete ETL pipeline for processing image data with text content (e.g., memes). It extracts text using OCR, processes image metadata, and performs various analyses. The pipeline includes options to load processed data into a MongoDB database for data warehousing.

**Key Features:**
- Image processing with OpenCV
- Text extraction from images using Tesseract OCR
- Data transformation and cleaning
- Sentiment analysis visualization
- MongoDB data warehouse integration
- Progress tracking with real-time updates
- Comprehensive testing framework
- Docker containerization for easy deployment

## 🗂 Repository Structure

```
Data_Information_Knowledge/Tugas_1/
├── src/                      # Source code
│   ├── etl_pipeline.py       # Main ETL pipeline implementation
│   ├── warehouse_loader.py   # MongoDB data warehouse integration
│   ├── analyze_data.py       # Data analysis and visualization
│   └── visualization.py      # Additional visualization utilities
├── test/                     # Test suite
│   └── test_etl.py           # ETL pipeline tests
├── data/                     # Data directory (gitignored)
│   ├── raw/                  # Raw input data
│   ├── processed/            # Processed output data
│   └── analysis/             # Analysis results and visualizations
├── Dockerfile                # Docker container definition
├── docker-compose.yml        # Multi-container Docker definition
├── docker-entrypoint.sh      # Docker container startup script
├── DOCKER.md                 # Docker-specific documentation
├── run_pipeline.py           # Pipeline execution script
├── requirements.txt          # Dependencies
├── .env                      # Environment variables (gitignored)
└── README.md                 # This documentation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR ([Installation Guide](https://github.com/tesseract-ocr/tesseract))
- MongoDB account (for data warehousing)
- Docker and Docker Compose (optional, for containerized deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Data_Information_Knowledge/Tugas_1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Tesseract path:
   - For Windows, set the path in `src/etl_pipeline.py` if it differs from `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - For Linux/Mac, ensure Tesseract is in your system PATH

### Data Setup

The data folder is excluded from version control due to size constraints. You'll need to create your own data structure:

1. Create the required directories:
   ```bash
   mkdir -p data/raw/images data/processed data/analysis data/raw_test/images
   ```

2. **Raw data requirements:**
   - Place your images in `data/raw/images/`
   - Create a CSV file `data/raw/labels.csv` with columns mapping to your images

   Example labels.csv format:
   ```csv
   image_file,sentiment,category
   image1.jpg,positive,funny
   image2.jpg,negative,political
   ```

3. **Test data setup:**
   - Copy a small subset of images to `data/raw_test/images/` 
   - Create a corresponding `data/raw_test/labels_test.csv`

### MongoDB Configuration

For data warehouse functionality:

1. Create a MongoDB Atlas account (free tier available)
2. Create a new cluster and get your connection string
3. Create a `.env` file in the project root with:
   ```
   MONGO_CONNECTION_STRING=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
   ```

## 💻 Usage

### Running the Pipeline

The main entry point is the `run_pipeline.py` script, which orchestrates the ETL process:

```bash
# Basic usage - processes 10 sample images
python run_pipeline.py

# Process up to 1000 images
python run_pipeline.py --all

# Show detailed debug output
python run_pipeline.py --debug

# Load processed data to MongoDB
python run_pipeline.py --warehouse

# Combine options
python run_pipeline.py --all --warehouse
```

### Docker Deployment

For a containerized deployment with all dependencies pre-installed:

```bash
# Start the full stack (ETL + MongoDB + Mongo Express)
docker-compose up

# Run only the pipeline with specific options
docker-compose run --rm etl-pipeline --all --debug
```

See [DOCKER.md](DOCKER.md) for detailed containerization instructions.

### Command Options

| Option | Description |
|--------|-------------|
| `--all` | Process up to 1000 images (instead of 10) |
| `--debug` | Show detailed debug output |
| `--warehouse` | Load processed data to MongoDB |

## 🔄 Pipeline Workflow

The ETL pipeline follows these steps:

1. **Extract**: 
   - Reads images from the specified directory
   - Loads corresponding labels from CSV

2. **Transform**:
   - Processes images using OpenCV
   - Extracts text using Tesseract OCR
   - Computes image histograms and metrics
   - Cleans and standardizes data

3. **Load**:
   - Saves processed data as parquet/CSV files
   - Generates initial visualizations
   - Optionally loads data to MongoDB warehouse

4. **Analysis**:
   - Performs detailed analysis on processed data
   - Creates visualizations for text and image attributes
   - Saves analysis results to output directory

## 📈 Output & Analysis

After running the pipeline, you'll find:

1. **Processed Data**:
   - `data/processed/processed_data.parquet` - Main processed dataset
   - `data/processed/sentiment_distribution.png` - Initial sentiment visualization

2. **Analysis Results**:
   - `data/analysis/data_summary.txt` - Dataset statistics
   - `data/analysis/sentiment_distribution.png` - Sentiment distribution chart
   - `data/analysis/word_count_distribution.png` - Text length analysis
   - `data/analysis/top_words.png` - Common word frequency chart
   - `data/analysis/image_size_distribution.png` - Image dimensions analysis

3. **MongoDB Warehouse**:
   - Access your processed data in the `meme_data_warehouse` database
   - Data indexed by sentiment for efficient querying

## 🧪 Testing

Run the automated test suite:

```bash
python -m pytest
```

Or run tests through the pipeline:

```bash
python run_pipeline.py
```

Test data will be processed and saved to `data/processed_test/` with analysis in `data/test_analysis/`.

## ⚠️ Troubleshooting

**Common Issues:**

1. **Tesseract not found**:
   - Ensure Tesseract is installed
   - Update the path in `src/etl_pipeline.py`

2. **MongoDB connection error**:
   - Verify your connection string in `.env`
   - Check network/firewall settings

3. **Image processing errors**:
   - Ensure image files are valid and not corrupted
   - Check sufficient disk space for processed data

4. **Memory issues with large datasets**:
   - Use the `--sample` option to process fewer images
   - Increase available memory or process in batches

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Created by Hariz | Data & Information Knowledge Engineering | 2025