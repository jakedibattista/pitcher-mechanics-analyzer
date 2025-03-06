import requests
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class GameStateManager:
    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1.1"
        self.logger = logging.getLogger(__name__)
        
    def get_game_context(self, game_pk, pitcher_id):
        """Get game state data for specific pitcher"""
        try:
            # For development/testing, return mock data if game_pk isn't numeric
            if not str(game_pk).isdigit():
                self.logger.info("Using mock game data for development")
                return self._get_mock_game_state()

            url = f"{self.base_url}/game/{game_pk}/feed/live"
            self.logger.info(f"Fetching game data from: {url}")
            response = requests.get(url)
            data = response.json()
            
            if 'liveData' not in data:
                self.logger.warning("No live data available, using mock data")
                return self._get_mock_game_state()
                
            game_state = {
                'inning': data['liveData']['linescore']['currentInning'],
                'outs': data['liveData']['linescore']['outs'],
                'runners': self._get_runner_situation(data),
                'score': self._get_score(data),
                'pitch_count': self._get_pitcher_stats(data, pitcher_id),
                'previous_pitches': self._get_previous_pitches(data, pitcher_id)
            }
            
            self.logger.info(f"Retrieved game state: inning={game_state['inning']}, outs={game_state['outs']}")
            return game_state
            
        except Exception as e:
            self.logger.error(f"Error getting game context: {str(e)}")
            return self._get_mock_game_state()

    def _get_mock_game_state(self):
        """Return mock game state for development/testing"""
        self.logger.info("Using mock game state data")
        return {
            'inning': 6,
            'outs': 2,
            'runners': {'first': False, 'second': False, 'third': False},
            'score': {'home': 3, 'away': 0},
            'pitch_count': 67,
            'previous_pitches': []
        }
        
    def _get_runner_situation(self, data):
        """Get current runners on base"""
        try:
            bases = data['liveData']['linescore']['offense']
            return {
                'first': bases.get('first', None) is not None,
                'second': bases.get('second', None) is not None,
                'third': bases.get('third', None) is not None
            }
        except Exception as e:
            self.logger.error(f"Error getting runner situation: {str(e)}")
            return {'first': False, 'second': False, 'third': False}
        
    def _get_score(self, data):
        """Get current game score"""
        try:
            return {
                'home': data['liveData']['linescore']['teams']['home']['runs'],
                'away': data['liveData']['linescore']['teams']['away']['runs']
            }
        except Exception as e:
            self.logger.error(f"Error getting score: {str(e)}")
            return {'home': 0, 'away': 0}
        
    def _get_pitcher_stats(self, data, pitcher_id):
        """Get current pitcher stats"""
        try:
            boxscore = data['liveData']['boxscore']
            pitcher_stats = None
            
            # Search both teams' pitchers
            for team in ['home', 'away']:
                pitchers = boxscore['teams'][team]['players']
                pitcher_key = f'ID{pitcher_id}'
                if pitcher_key in pitchers:
                    pitcher_stats = pitchers[pitcher_key]['stats']['pitching']
                    break
                    
            return pitcher_stats['numberOfPitches'] if pitcher_stats else 0
        except Exception as e:
            self.logger.error(f"Error getting pitcher stats: {str(e)}")
            return 0
        
    def _get_previous_pitches(self, data, pitcher_id):
        """Get sequence of previous pitches"""
        try:
            plays = data['liveData']['plays']['allPlays']
            return [
                pitch for play in plays 
                for pitch in play.get('playEvents', [])
                if pitch.get('details', {}).get('type') == 'pitch'
                and pitch.get('matchup', {}).get('pitcher', {}).get('id') == pitcher_id
            ][-3:]  # Return last 3 pitches
        except Exception as e:
            self.logger.error(f"Error getting previous pitches: {str(e)}")
            return [] 