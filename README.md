# Baseball Pitcher Mechanics Analyzer

An AI-powered tool for analyzing baseball pitcher mechanics using computer vision and machine learning.

## Overview

This project uses Vertex AI (Gemini Pro Vision) to analyze baseball pitcher mechanics from video footage. It can:
- Analyze different pitch types (Curveball, Slider)
- Compare mechanics to pitcher-specific ideal forms
- Detect mechanical deviations and fatigue signs
- Generate visual analysis overlays

## Features

- **Multi-Pitcher Support**: Currently supports analysis of:
  - Clayton Kershaw (Curveball, Slider)
  - Zack Wheeler (Slider)

- **Mechanical Analysis**:
  - Power Generation
  - Arm Action
  - Balance/Direction
  - Fatigue Detection

- **Visual Output**:
  - Annotated video analysis
  - Pitcher scorecard generation
  - Mechanical variance assessment

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pitcher-mechanics-analyzer.git
cd pitcher-mechanics-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud credentials for Vertex AI:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

## Usage

Basic analysis:
```bash
python -m pitcher_analyzer.debug_analysis [video_name] [pitch_type] [pitcher_name]
```

Example:
```bash
python -m pitcher_analyzer.debug_analysis kershaw2 CURVEBALL KERSHAW
```

## Project Structure

```
pitcher_analyzer/
├── __init__.py
├── main.py                 # Main analysis pipeline
├── mechanics_analyzer.py   # Mechanical analysis logic
├── video_processor.py      # Video frame extraction
├── visualization.py        # Analysis visualization
├── config.py              # Configuration and profiles
├── pose_analyzer.py        # Pose detection analysis
├── debug_analysis.py      # Debug utilities
├── video_downloader.py    # Video management
└── tests/                 # Test suite
```

## Data Sources

This project uses video data from MLB broadcasts. All MLB content is the property of MLB and its teams. Video content is used for educational and research purposes only.

## Dependencies

- OpenCV for video processing and visualization
- Google Cloud Vertex AI for computer vision analysis
- Additional dependencies listed in requirements.txt

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
