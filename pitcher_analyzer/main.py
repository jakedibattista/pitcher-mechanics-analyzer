import logging
from pitcher_analyzer.video_processor import VideoProcessor
from pitcher_analyzer.mechanics_analyzer import MechanicsAnalyzer
from pitcher_analyzer.visualization import create_analysis_visualization
from pitcher_analyzer.game_state import GameStateManager

class PitcherAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.video_processor = VideoProcessor()
        self.mechanics_analyzer = MechanicsAnalyzer()
        self.game_state = GameStateManager()

    def analyze_pitch(self, video_path, pitch_type, game_pk=None, pitcher_id=None, pitcher_name='KERSHAW'):
        """Complete pitch analysis pipeline"""
        try:
            # Get game state if IDs provided, but don't fail if unavailable
            game_state = None
            if game_pk and pitcher_id:
                try:
                    game_state = self.game_state.get_game_context(game_pk, pitcher_id)
                except Exception as e:
                    self.logger.warning(f"Could not get game context: {str(e)}")
                    game_state = {
                        'inning': 6,
                        'outs': 2,
                        'runners': {'first': False, 'second': False, 'third': False},
                        'score': {'home': 3, 'away': 0},
                        'pitch_count': 67,
                        'previous_pitches': []
                    }

            # Determine game context from state
            game_context = self._determine_game_context(game_state, pitcher_name, pitch_type)

            # Extract frames
            try:
                frames = self.video_processor.extract_frames(video_path, pitch_type)
                if not frames:
                    raise ValueError("No frames extracted from video")
                self.logger.info(f"Successfully extracted {len(frames)} frames")
            except Exception as e:
                self.logger.error(f"Frame extraction failed: {str(e)}")
                raise

            # Analyze mechanics
            try:
                analysis = self.mechanics_analyzer.analyze_mechanics(
                    frames, pitch_type, pitcher_name, game_context, game_state)
                if not analysis:
                    raise ValueError("Mechanics analysis failed")
                self.logger.info("Mechanics analysis completed")
            except Exception as e:
                self.logger.error(f"Mechanics analysis failed: {str(e)}")
                raise

            # Create visualization
            try:
                output_path = create_analysis_visualization(
                    video_path, analysis, pitch_type)
                self.logger.info(f"Visualization created at: {output_path}")
                return output_path
            except Exception as e:
                self.logger.error(f"Visualization failed: {str(e)}")
                raise

        except Exception as e:
            self.logger.error(f"Analysis pipeline failed: {str(e)}")
            return None

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