# Baseball Pitcher Mechanics Analyzer

An AI-powered tool for analyzing baseball pitcher mechanics using computer vision and machine learning.

See a demo of the product in action here: https://www.youtube.com/watch?v=nHqDvu8WAPM

Production URL: https://pitcher-analyzer-238493405692.us-central1.run.app/

Updated Github for GoogleCloud Next 2025: https://github.com/jakedibattista/GoogleCloud-PitcherAnalyzer

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

- **Multi-frame mechanics analysis**
- **Pitcher-specific customization**
- **Game context integration**
- **Detailed mechanical breakdown**
- **Real-time analysis**

## Requirements

- Python 3.8+
- Google Cloud account
- Vertex AI API enabled
- Sample video data

## Installation

Follow QUICKSTART.MD for setup instructions.

## License

[MIT License]

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


