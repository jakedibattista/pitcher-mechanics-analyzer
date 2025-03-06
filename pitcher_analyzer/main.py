import logging
import os
from pitcher_analyzer.video_processor import VideoProcessor
from pitcher_analyzer.mechanics_analyzer import MechanicsAnalyzer
from pitcher_analyzer.visualization import create_analysis_visualization
from pitcher_analyzer.game_state import GameStateManager

logger = logging.getLogger(__name__)

class PitcherAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.video_processor = VideoProcessor()
        self.mechanics_analyzer = MechanicsAnalyzer()
        self.game_state = GameStateManager()

    async def analyze_pitch(self, video_path=None, frames=None, pitch_type=None, 
                           game_context=None, pitcher_name=None, game_state=None):
        """
        Analyze a pitch from video or frames.
        
        Args:
            video_path: Path to video file (optional)
            frames: Pre-loaded video frames (optional)
            pitch_type: Type of pitch being thrown
            game_context: Context of the game situation
            pitcher_name: Name of the pitcher profile to compare against
            game_state: Alternative name for game_context
        """
        try:
            self.logger.info(f"Starting analysis for {pitcher_name} throwing {pitch_type} in {game_context} context")
            
            # Get game state if IDs provided
            game_state = None
            if game_state:
                game_state = self.game_state.get_game_context(game_state['game_pk'], game_state['pitcher_id'])
            else:
                game_state = {
                    'inning': 6,
                    'outs': 2,
                    'runners': {'first': False, 'second': False, 'third': False},
                    'score': {'home': 3, 'away': 0},
                    'pitch_count': 67,
                    'previous_pitches': []
                }

            # Use either video_path or frames
            if frames is not None:
                video_frames = frames
            elif video_path is not None:
                video_frames = self.video_processor.extract_frames(video_path, pitch_type)
            else:
                raise ValueError("Either video_path or frames must be provided")
            
            # Perform mechanics analysis
            self.logger.debug("Starting mechanics analysis")
            mechanics_analysis = await self.mechanics_analyzer.analyze_mechanics(
                frames=video_frames,
                pitch_type=pitch_type,
                game_context=game_context,
                pitcher_name=pitcher_name
            )
            
            if not mechanics_analysis:
                raise ValueError("Mechanics analysis returned no results")
            self.logger.info("Mechanics analysis completed")

            # Create visualization
            self.logger.debug("Creating visualization")
            output_path = create_analysis_visualization(
                video_frames, 
                mechanics_analysis, 
                pitch_type
            )
            self.logger.info(f"Visualization created at: {output_path}")
            
            # Return both the output path and analysis results
            return output_path, mechanics_analysis

        except Exception as e:
            self.logger.exception("Analysis pipeline failed")
            # Return a tuple with empty/default values
            return None, {
                'mechanics_score': 0.0,
                'risk_factors': ['Analysis failed'],
                'recommendations': ['Please try again with a clearer video'],
                'deviations': {}
            }

    def _determine_game_context(self, game_state, pitcher_name, pitch_type):
        """Determine game context based on game state and pitcher"""
        if not game_state:
            return None
            
        if pitcher_name == 'KERSHAW' and (pitch_type in ['CURVEBALL', 'SLIDER']):
            return 'PERFECT_GAME'
        elif pitcher_name == 'CORTES' and pitch_type == 'FASTBALL':
            return 'RELIEF_PRESSURE'
        else:
            return game_state.get('inning')

    def analyze_pitch_sync(self, video_path, pitcher, pitch, context):
        try:
            logger.info(f"Starting analysis for video: {video_path}")
            
            # Verify video file exists and is readable
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Verify file size
            file_size = os.path.getsize(video_path)
            logger.info(f"Video file size: {file_size / (1024*1024):.1f} MB")

            # Analyze mechanics
            analysis_result = self.mechanics_analyzer.analyze_mechanics(
                video_path=video_path,
                pitcher_profile=pitcher,
                pitch=pitch,
                context=context
            )
            logger.info("Mechanics analysis completed")

            # Create visualization
            analyzed_video_path = create_analysis_visualization(
                video_path,
                analysis_result
            )
            logger.info(f"Analysis visualization created: {analyzed_video_path}")

            return analyzed_video_path, analysis_result

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise

    def analyze_mechanics_sync(self, video_frames=None, frames=None, pitch_type=None,
                              game_context=None, pitcher_name=None, game_state=None):
        """
        Synchronous wrapper for analyze_mechanics
        """
        import asyncio
        return asyncio.run(self.mechanics_analyzer.analyze_mechanics(
            video_frames=video_frames,
            frames=frames,
            pitch_type=pitch_type,
            game_context=game_context,
            pitcher_name=pitcher_name,
            game_state=game_state
        )) 