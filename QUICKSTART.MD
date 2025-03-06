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
