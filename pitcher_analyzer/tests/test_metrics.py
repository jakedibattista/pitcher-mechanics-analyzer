"""Test metrics calculation and parsing."""
import unittest
import sys
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pitcher_analyzer.analyzer import PitcherAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMetricsCalculation(unittest.TestCase):
    """Test metrics calculation and parsing."""
    
    def test_parse_scores(self):
        """Test parsing scores from analysis text."""
        # Create a mock analyzer without credentials
        analyzer = PitcherAnalyzer(None)
        
        # Sample analysis text with scores
        analysis_text = """
        Mechanics Score: 8/10
        • Excellent arm slot consistency throughout delivery
        • Strong hip-shoulder separation at release
        • Balanced follow-through with good deceleration

        Match to Ideal Form: 7/10
        • Closely matches Kershaw's ideal curveball mechanics
        • Slight variation in release point compared to ideal
        • Good spine angle maintained through release

        Injury Risk Score: 3/10 (lower is better)
        • Low stress on elbow during delivery
        • Good shoulder positioning throughout motion
        • Proper weight transfer reduces strain on lower body

        Recommendations:
        • Focus on maintaining consistent release point
        • Slightly increase hip rotation for better velocity
        """
        
        # Parse scores
        scores = analyzer._parse_scores(analysis_text)
        
        # Log the actual keys for debugging
        logger.info(f"Score keys: {list(scores.keys())}")
        
        # Verify parsed scores
        self.assertEqual(scores['mechanics_score'], 8)
        
        # Check for the ideal form score with different possible key names
        if 'ideal_form_score' in scores:
            self.assertEqual(scores['ideal_form_score'], 7)
        elif 'match_to_ideal_score' in scores:
            self.assertEqual(scores['match_to_ideal_score'], 7)
        elif 'ideal_match_score' in scores:
            self.assertEqual(scores['ideal_match_score'], 7)
        else:
            # If none of the expected keys are found, print all keys and fail
            self.fail(f"No ideal form score key found. Available keys: {list(scores.keys())}")
        
        self.assertEqual(scores['injury_risk_score'], 3)
        self.assertIn('recommendations', scores)
        self.assertTrue(isinstance(scores['recommendations'], list))
        self.assertEqual(len(scores['recommendations']), 2)

if __name__ == '__main__':
    unittest.main() 