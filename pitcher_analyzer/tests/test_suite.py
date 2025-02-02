import unittest
from pathlib import Path
import cv2
import numpy as np
from pitcher_analyzer import PitcherAnalyzer
from pitcher_analyzer.config import Config
from pitcher_analyzer.pose_analyzer import PoseAnalyzer

class TestPitcherAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        Config.validate()
        cls.analyzer = PitcherAnalyzer()
        cls.test_video = cls._create_test_video()
        
    @classmethod
    def _create_test_video(cls):
        """Create a test video with known pitch characteristics"""
        output_path = Config.TEST_DATA_DIR / "test_pitch.mp4"
        width, height = Config.VIDEO_REQUIREMENTS["min_resolution"]
        fps = Config.VIDEO_REQUIREMENTS["fps"]
        duration = 5  # seconds
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        try:
            # Create frames with simulated pitch
            ball_x = width * 0.2  # Start at 20% from left
            ball_y = height * 0.6  # 60% from top
            velocity_x = (width * 0.6) / (fps * 0.4)  # Move 60% of width in 0.4 seconds
            
            for frame_num in range(int(fps * duration)):
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Draw background
                cv2.rectangle(frame, (0, 0), (width, height), (100, 150, 100), -1)
                
                # Draw pitcher's mound
                cv2.circle(frame, (int(width * 0.2), int(height * 0.6)), 50, (150, 150, 150), -1)
                
                # Draw home plate
                cv2.circle(frame, (int(width * 0.8), int(height * 0.6)), 30, (255, 255, 255), -1)
                
                # Draw ball for first 0.5 seconds
                if frame_num < int(fps * 0.5):
                    ball_x += velocity_x
                    cv2.circle(frame, (int(ball_x), int(ball_y)), 5, (255, 255, 255), -1)
                
                out.write(frame)
                
            return output_path
            
        finally:
            out.release()
    
    def test_config_validation(self):
        """Test configuration validation"""
        self.assertTrue(Config.validate())
        self.assertTrue(Config.TEST_DATA_DIR.exists())
        self.assertTrue(Config.VIDEO_DIR.exists())
        self.assertTrue(Config.ANALYSIS_DIR.exists())
        
    def test_pitch_analysis(self):
        """Test full pitch analysis pipeline"""
        result = self.analyzer.analyze_new_pitch(str(self.test_video))
        
        self.assertIsNotNone(result)
        self.assertIn('velocity', result)
        self.assertIn('release_point', result)
        self.assertIn('confidence', result)
        
        # Check velocity range
        velocity = result['velocity']
        self.assertTrue(Config.BALL_TRACKING["velocity_range"][0] <= velocity <= Config.BALL_TRACKING["velocity_range"][1])
        
        # Check release point
        release_point = result['release_point']
        self.assertIn('x', release_point)
        self.assertIn('y', release_point)
        self.assertTrue(0 <= release_point['x'] <= 100)
        self.assertTrue(0 <= release_point['y'] <= 100)
        
    def test_pitcher_decision(self):
        """Test pitcher pull decision"""
        should_pull = self.analyzer.should_pull_pitcher(str(self.test_video))
        self.assertIsInstance(should_pull, bool)

class TestPoseAnalysis(unittest.TestCase):
    def setUp(self):
        self.analyzer = PoseAnalyzer()
        self.test_video = "test_data/sample_pitch.mp4"
        
    def test_pose_detection(self):
        metrics = self.analyzer.analyze_mechanics(self.test_video)
        self.assertIsNotNone(metrics)
        self.assertIn('arm_slot_consistency', metrics)
        self.assertIn('stride_length', metrics)
        
    def test_fatigue_detection(self):
        metrics = self.analyzer.analyze_mechanics(self.test_video)
        fatigue = self.analyzer.detect_fatigue(metrics)
        self.assertIsNotNone(fatigue)
        self.assertIn('fatigue_score', fatigue)
        
    def test_form_comparison(self):
        metrics = self.analyzer.analyze_mechanics(self.test_video)
        comparison = self.analyzer.compare_to_ideal(metrics)
        self.assertIsNotNone(comparison)
        self.assertIn('overall_score', comparison)

def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests() 