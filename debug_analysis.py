import logging
from pitcher_analyzer.video_manager import VideoManager
from pitcher_analyzer.pose_analyzer import PoseAnalyzer
from pitcher_analyzer.utils.debug import create_analysis_visualization
import time
import argparse
from pathlib import Path
from pitcher_analyzer.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_video(video_name, pitch_type='AUTO', pitcher_name='KERSHAW'):
    try:
        start_time = time.time()
        
        # Create output directory in current folder
        output_dir = Path.cwd() / "analysis_output"
        output_dir.mkdir(exist_ok=True)
        
        # Find video
        video_manager = VideoManager()
        video_path, location = video_manager.find_video(video_name)
        if not video_path:
            logger.error(f"Video not found: {video_name}")
            return
            
        # First detect velocity
        velocity = video_manager.detect_velocity(video_path)
        logger.info(f"Detected velocity: {velocity} mph")
        
        if pitch_type == 'AUTO' and velocity is None:
            logger.error(f"Could not detect pitch velocity. Please specify pitch type manually using --pitch_type:")
            logger.error(f"For {pitcher_name}:")
            profile = Config.PITCHER_PROFILES.get(pitcher_name)
            for pitch, vel_range in profile['career_stats']['typical_velocity'].items():
                logger.error(f"  --pitch_type {pitch:<8} ({vel_range} mph)")
            logger.error(f"\nExample: python debug_analysis.py --video {video_name} --pitch_type FASTBALL --pitcher {pitcher_name}")
            return
        
        # Run analysis with detected pitch type
        analyzer = PoseAnalyzer()
        analysis = analyzer.analyze_mechanics(
            video_path, 
            pitch_type=pitch_type,
            detected_velocity=velocity,
            pitcher_name=pitcher_name
        )
        
        if not analysis:
            logger.error("Analysis failed to produce results")
            return
            
        # Create visualization with velocity info
        viz_path = create_analysis_visualization(
            video_path=video_path,
            analysis_text=analysis,
            detected_velocity=velocity,
            pitch_type=pitch_type,
            pitcher_name=pitcher_name
        )
        
        # Only log analysis results
        logger.info("\nAnalysis Results:")
        logger.info(analysis)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', default='kershaw1', help='Name of video to analyze')
    parser.add_argument('--pitch_type', default='AUTO', 
                       help='Type of pitch: FASTBALL, SLIDER, CURVEBALL, CUTTER, or AUTO')
    parser.add_argument('--pitcher', default='KERSHAW',
                       help='Pitcher name: KERSHAW, CORTES')
    args = parser.parse_args()
    
    analyze_video(args.video, args.pitch_type, args.pitcher)