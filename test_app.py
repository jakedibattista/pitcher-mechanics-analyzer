from pitcher_analyzer import PitcherAnalyzer
import logging
from pathlib import Path

def test_analysis():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create analyzer instance
    analyzer = PitcherAnalyzer()
    
    # Use the test video we created earlier
    video_path = Path("pitcher_analyzer/tests/data/sample_pitch.mp4")
    
    if not video_path.exists():
        logger.error(f"Test video not found at {video_path}")
        logger.info("Creating test video first...")
        from pitcher_analyzer.tests.create_test_video import create_test_pitch_video
        video_path = Path(create_test_pitch_video())
    
    logger.info(f"Analyzing video: {video_path}")
    
    try:
        # Run analysis
        metrics = analyzer.analyze_new_pitch(str(video_path))
        
        # Print results
        print("\nAnalysis Results:")
        print("================")
        for metric, value in metrics.items():
            print(f"{metric}: {value}")
            
        print("\nVisualization outputs can be found in the 'analysis_output' directory")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_analysis() 