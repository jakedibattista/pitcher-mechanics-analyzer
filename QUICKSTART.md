# Pitcher Analyzer - Vertex AI Implementation

## Prerequisites
1. Python 3.8+
2. Google Cloud account with Vertex AI enabled
3. Sample video of Kershaw's slider

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download test video:
   - Download Kershaw slider: [Google Drive Link](https://drive.google.com/file/d/1HwdbaqdNIyEUVDLAbjt_6suJssyx6xgs/view?usp=sharing)

3. Set up Google Cloud:
   - Set environment variable for credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

## Run Analysis
```bash
python debug_analysis.py --video kershaw1 --pitch_type SLIDER --pitcher KERSHAW
```

## How It Works

The program uses Vertex AI's Gemini Pro Vision model to:
1. Extract key frames from the pitch video
2. Create a customized prompt based on:
   - Pitch type (e.g., SLIDER)
   - Pitcher profile (e.g., Kershaw's mechanics)
   - Game context (if provided)
3. Send multiple frames simultaneously for analysis
4. Generate detailed mechanics breakdown

Example prompt customization:
- Release point: 6.3 feet
- Spine angle: 45°
- Hip-shoulder separation: 40°
- Game situation context
- Comparison to ideal 2021 form

# Quick Start Guide

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials/service-account.json"
```

3. Run the application:
```bash
streamlit run pitcher_analyzer/streamlit_app.py
```

## Docker Deployment

### Standard Deployment

```bash
# Build Docker image
docker build -t pitcher-analyzer .

# Run Docker container
docker run -p 8501:8501 -v $(pwd)/credentials:/app/credentials pitcher-analyzer
```

### Corporate Network Deployment

If you're on a corporate network (like Walmart), use these commands:

```bash
# Set proxy environment variables
export HTTP_PROXY="http://proxy.wal-mart.com:8080"
export HTTPS_PROXY="http://proxy.wal-mart.com:8080"
export NO_PROXY="localhost,127.0.0.1"

# Build with proxy settings
docker build \
  --build-arg HTTP_PROXY=$HTTP_PROXY \
  --build-arg HTTPS_PROXY=$HTTPS_PROXY \
  --build-arg NO_PROXY=$NO_PROXY \
  -t pitcher-analyzer .

# Run with proxy settings
docker run -p 8501:8501 \
  -v $(pwd)/credentials:/app/credentials \
  -e HTTP_PROXY=$HTTP_PROXY \
  -e HTTPS_PROXY=$HTTPS_PROXY \
  -e NO_PROXY=$NO_PROXY \
  pitcher-analyzer
```

Alternatively, use the provided script:
```bash
./scripts/build_docker.sh
```

## Cloud Run Deployment

```bash
# Build and push Docker image
docker build --platform linux/amd64 -t gcr.io/baseball-pitcher-analyzer/pitcher-analyzer .
docker push gcr.io/baseball-pitcher-analyzer/pitcher-analyzer

# Deploy to Cloud Run
gcloud run deploy pitcher-analyzer \
  --project baseball-pitcher-analyzer \
  --image gcr.io/baseball-pitcher-analyzer/pitcher-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```
