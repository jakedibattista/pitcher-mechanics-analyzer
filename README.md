# Pitcher Analysis Tool ⚾

A machine learning-powered tool for analyzing baseball pitcher mechanics using video analysis and Vertex AI.

![Pitcher Analysis Demo](https://storage.googleapis.com/baseball-pitcher-analyzer-videos/demo_screenshot.png)

## Features

- **Video Analysis**: Upload and analyze pitch videos with advanced computer vision
- **Multiple Pitch Types**: Support for Fastball, Curveball, Slider, Changeup, and more
- **Detailed Mechanical Analysis**: Get comprehensive breakdown of pitching mechanics
- **Injury Risk Assessment**: Identify potential injury risks in pitching motion
- **Performance Optimization**: Receive actionable recommendations to improve mechanics
- **Game Context Awareness**: Analyze pitches in the context of specific games
- **Visual Feedback**: Clear visualizations of mechanical issues and improvements

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up credentials**:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials/service-account.json"
```

3. **Run the application**:
```bash
streamlit run pitcher_analyzer/streamlit_app.py
```

## Using the Application

1. **Select a Pitcher**: Choose from our database of MLB pitchers
2. **Select a Pitch Type**: Specify which pitch type you're analyzing
3. **Choose Game Context** (Optional): Select a specific game or "Unknown"
4. **Upload Video**: Upload a video of the pitch to analyze
5. **View Analysis**: Get detailed breakdown of mechanics, injury risks, and recommendations

## Game Context Analysis

The application can analyze pitches in the context of specific games, providing insights into:

- How mechanics change under game pressure
- Fatigue effects in late innings
- Performance patterns in different situations
- Historical comparisons across games

## Technical Details

### Architecture

- **Frontend**: Streamlit web application
- **Backend**: Python-based analysis pipeline
- **ML Models**: Vertex AI and custom computer vision models
- **Storage**: Google Cloud Storage for video processing
- **Deployment**: Docker containerization for easy deployment

### Key Components

- `streamlit_app.py`: Web interface for the application
- `analyzer.py`: Core analysis pipeline
- `game_state.py`: Game context management
- `utils.py`: Utility functions for cloud operations
- `data/pitcher_profiles.py`: MLB pitcher mechanics data

## Development

To contribute to the project:

1. **Set up development environment**:
```bash
pip install -r requirements-dev.txt
```

2. **Run tests**:
```bash
python -m pitcher_analyzer.tests.test_suite
```

3. **Format code**:
```bash
black pitcher_analyzer/
```

## Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t pitcher-analyzer .

# Run Docker container
docker run -p 8501:8501 -v $(pwd)/credentials:/app/credentials pitcher-analyzer
```

### Cloud Run Deployment

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

## Troubleshooting

If you encounter issues:

1. **Check credentials**: Ensure your Google Cloud credentials are properly set up
2. **Verify dependencies**: Make sure all required packages are installed
3. **Check logs**: Review application logs for error messages
4. **Video format**: Ensure your video meets the recommended specifications

## Requirements

- Python 3.8+
- Google Cloud account with Vertex AI enabled
- Gemini API key
- OpenCV and related dependencies

## License

This project is licensed under the MIT License - see the LICENSE file for details.# Updated on Thu Mar  6 10:12:39 EST 2025
