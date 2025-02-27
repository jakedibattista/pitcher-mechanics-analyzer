# Pitcher Analysis Tool ⚾

A machine learning-powered tool for analyzing baseball pitcher mechanics using video analysis and Vertex AI.

## Features
- Upload and analyze pitch videos
- Support for multiple pitch types (Fastball, Curveball, Slider, Changeup)
- Detailed mechanical analysis
- Visual feedback and annotations
- Game context awareness

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open the web application in your browser:
```bash
http://localhost:8000
```

## Quick Start with Docker

1. Set up credentials:
   ```bash
   mkdir -p credentials
   # Copy your service account JSON to credentials/service-account.json
   ```

2. Run with Docker:
   ```bash
   docker-compose up --build
   ```

3. Access the app:
   ```
   http://localhost:8503
   ```

## Production Deployment

The app is deployed to Google Cloud Run:

```
https://pitcher-analyzer-238493405692.us-central1.run.app
```

To deploy updates:
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
  --allow-unauthenticated \
  --set-secrets "/app/credentials/service-account.json=pitcher-credentials:latest" \
  --set-env-vars "GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account.json"
```

## Usage

## Expected Output
The analyzer will generate:
1. Mechanical analysis in real-time
2. Visualization with annotated video in the web interface

## Deployment
To deploy to Google Cloud Run:
```bash
gcloud run deploy pitcher-analysis --image gcr.io/YOUR_PROJECT_ID/pitcher-analysis --platform managed
```

## Setting Up Google Cloud Credentials

1. Create a Google Cloud Project
   ```bash
   # Visit https://console.cloud.google.com/
   # Click "New Project" and note your Project ID
   ```

2. Enable Required APIs
   - Go to APIs & Services > Library
   - Enable these APIs:
     - Cloud Storage API
     - Vertex AI API
     - Cloud Vision API

3. Create Service Account
   ```bash
   # Navigate to IAM & Admin > Service Accounts
   # Click "Create Service Account"
   # Name: pitcher-analyzer-sa
   # Role: Add these roles:
     - Vertex AI User
     - Storage Object Viewer
   ```

4. Generate Credentials File
   ```bash
   # In the Service Account details:
   # 1. Go to "Keys" tab
   # 2. Click "Add Key" > "Create New Key"
   # 3. Choose JSON format
   # 4. Download the key file
   ```

5. Set Up Credentials in Project
   ```bash
   # Create credentials directory
   mkdir credentials
   
   # Copy your downloaded JSON key to credentials/
   cp path/to/downloaded/key.json credentials/service-account.json
   
   # Create .env file
   echo "GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json" > .env
   ```

6. Verify Setup
   ```bash
   # Run verification script
   python verify_environment.py
   ```

## Running with Docker

1. Build the container:
   ```bash
   docker-compose build
   ```

2. Start the application:
   ```bash
   docker-compose up
   ```

3. Access the app at:
   ```
   http://localhost:8502
   ```

## Security Notes

- Never commit credentials to version control
- Keep your service account key secure
- Restrict service account permissions to only what's needed
- Regularly rotate service account keys

## Troubleshooting

If you see credential errors:
1. Check that credentials/service-account.json exists
2. Verify the file path in .env matches docker-compose.yml
3. Ensure all required APIs are enabled
4. Verify service account has correct permissions

## Development
To contribute:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Requirements
- Python 3.8+
- Google Cloud account with Vertex AI enabled
- Gemini API key