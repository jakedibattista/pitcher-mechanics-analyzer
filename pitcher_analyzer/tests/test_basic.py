"""Basic test suite for pitcher analyzer functionality."""

import unittest
from pathlib import Path
from pitcher_analyzer import PitcherAnalyzer
import pytest
from pitcher_analyzer.mechanics_analyzer import MechanicsAnalyzer
from pitcher_analyzer.video_processor import VideoProcessor

class TestBasicFunctionality(unittest.TestCase):
    def setUp(self):
        self.analyzer = PitcherAnalyzer()
        # Using a short sample video for testing
        self.test_video_path = Path(__file__).parent / "data" / "sample_pitch.mp4"
        
    def test_video_exists(self):
        """Test if our test video exists"""
        self.assertTrue(self.test_video_path.exists(), 
                       f"Test video not found at {self.test_video_path}")
        
    def test_basic_analysis(self):
        """Test basic video analysis functionality"""
        metrics = self.analyzer.analyze_new_pitch(str(self.test_video_path))
        self.assertIsNotNone(metrics)
        self.assertIsInstance(metrics, dict)
        # Check for expected metrics
        expected_metrics = ['arm_angle', 'release_point', 'velocity', 'spin_rate', 'control']
        for metric in expected_metrics:
            self.assertIn(metric, metrics)

def test_video_processor_init():
    processor = VideoProcessor()
    assert processor is not None

def test_mechanics_analyzer_validation():
    analyzer = MechanicsAnalyzer()
    valid_response = """
    Signs of Fatigue:
    - Strong leg drive maintained through delivery

    Arm:
    - Perfect over-the-top slot with high elbow

    Balance:
    - Stable head position with controlled landing

    Overall Variance:
    - Mechanics Assessment: None
    """
    assert analyzer._validate_response(valid_response) == True

if __name__ == "__main__":
    unittest.main() 