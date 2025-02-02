import argparse
import time
from pathlib import Path
from .video_manager import VideoManager
from .main import PitcherAnalysis
from . import create_analysis_visualization
import logging
import sys

# Set up logging at the top of the file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Get video name and pitch type from command line args, with defaults
    video_name = sys.argv[1] if len(sys.argv) > 1 else 'kershaw2'
    pitch_type = sys.argv[2] if len(sys.argv) > 2 else 'CURVEBALL'
    pitcher_name = sys.argv[3] if len(sys.argv) > 3 else 'KERSHAW'
    
    logger.info(f"Starting {pitcher_name} {pitch_type.lower()} analysis...")
    
    try:
        # Initialize video manager and get video
        video_manager = VideoManager()
        logger.info(f"Attempting to get video '{video_name}'...")
        video_path = video_manager.get_video(video_name)
        
        if not video_path:
            logger.error(f"Failed to get video: {video_name}")
            return
            
        logger.info(f"Successfully got video at path: {video_path}")
        
        # Run analysis
        analyzer = PitcherAnalysis()
        result = analyzer.analyze_pitch(
            video_path=video_path,
            pitch_type=pitch_type,
            pitcher_name=pitcher_name
        )
        
        if result:
            logger.info("\n" + "="*50)
            logger.info("ANALYSIS RESULTS")
            logger.info("="*50)
            logger.info(result)
            logger.info("\n" + "="*50)
            logger.info(f"Visualization saved to: {result}")
            logger.info("="*50)
        else:
            logger.error("Analysis failed")
            
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise

def analyze_video(video_name, pitch_type='AUTO', pitcher_name='KERSHAW'):
    try:
        start_time = time.time()
        
        logger.info(f"Starting {pitcher_name} {pitch_type.lower()} analysis...")
        
        # Find video
        video_manager = VideoManager()
        video_path, location = video_manager.find_video(video_name)
        if not video_path:
            logger.error(f"Video not found: {video_name}")
            return
            
        logger.info(f"Successfully got video at path: {video_path}")
        logger.info("Initializing analysis...")
        
        # Run analysis with error handling for each step
        try:
            analyzer = PitcherAnalysis()
            logger.info("Running pitch analysis...")
            
            analysis = analyzer.analyze_mechanics(
                video_path, 
                pitch_type=pitch_type,
                pitcher_name=pitcher_name
            )
            
            if analysis:
                logger.info("\nAnalysis Results:")
                logger.info(analysis)
                return analysis
            else:
                logger.error("Analysis produced no results")
                return None
                
        except IndexError as e:
            logger.error(f"Frame processing error: {str(e)}")
            logger.error("This might be due to insufficient video length or missing frames")
            return None
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return None

def analyze_kershaw_slider():
    """Analyze Kershaw's slider from April 13, 2022 Dodgers vs. Twins game"""
    try:
        logger.info("Starting Kershaw slider analysis...")
        
        # Get video from cloud
        video_manager = VideoManager()
        logger.info("Attempting to get video 'kershaw1'...")
        video_path = video_manager.get_video("kershaw1")
        if not video_path:
            logger.error("Failed to download video")
            return
        logger.info(f"Successfully got video at path: {video_path}")

        # Run analysis with actual game data
        logger.info("Initializing analysis...")
        analyzer = PitcherAnalysis()
        logger.info("Running pitch analysis...")
        result = analyzer.analyze_pitch(
            video_path=video_path,
            pitch_type="SLIDER",
            pitcher_name="KERSHAW",
            game_pk="661413",  # April 13, 2022 Dodgers vs. Twins
            pitcher_id="477132"  # Kershaw's MLB ID
        )
        
        if result:
            logger.info("\n" + "="*50)
            logger.info("ANALYSIS RESULTS")
            logger.info("="*50)
            
            # Parse the analysis text if it's in the expected format
            if isinstance(result, str):
                lines = result.split('\n')
                for line in lines:
                    logger.info(line.strip())
            else:
                logger.info(result)
                
            logger.info("\n" + "="*50)
            logger.info(f"Visualization saved to: {result}")
            logger.info("="*50 + "\n")
        else:
            logger.error("Analysis failed")
            
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        logger.error(f"Stack trace:", exc_info=True)

if __name__ == "__main__":
    main() 