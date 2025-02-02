import unittest
from unittest.mock import Mock, patch
import numpy as np
from pitcher_analyzer import PitcherAnalyzer

class TestPitchMetrics(unittest.TestCase):
    def setUp(self):
        self.analyzer = PitcherAnalyzer()
        self.mock_frame = self._create_mock_frame()
        
    def _create_mock_frame(self):
        """Create a mock video frame with ball tracking data"""
        frame = Mock()
        frame.normalized_bounding_box.left = 0.4
        frame.normalized_bounding_box.top = 0.5
        frame.time_offset.seconds = 0
        frame.time_offset.microseconds = 0
        return frame
        
    def test_velocity_calculation(self):
        """Test velocity calculation from ball tracking"""
        # Create mock frames simulating 90mph pitch
        start_frame = self._create_mock_frame()
        end_frame = Mock()
        end_frame.normalized_bounding_box.left = 0.8
        end_frame.normalized_bounding_box.top = 0.5
        end_frame.time_offset.seconds = 0
        end_frame.time_offset.microseconds = 500000  # 0.5 seconds
        
        ball_track = Mock()
        ball_track.frames = [start_frame, end_frame]
        
        metrics = self.analyzer._calculate_ball_metrics(ball_track)
        self.assertIsNotNone(metrics.get('velocity'))
        self.assertTrue(80 <= metrics['velocity'] <= 100)
        
    def test_spin_rate_estimation(self):
        """Test spin rate calculation"""
        frames = [self._create_mock_frame() for _ in range(5)]
        # Simulate ball rotation
        for i, frame in enumerate(frames):
            frame.normalized_bounding_box.left = 0.4 + (i * 0.1)
            frame.normalized_bounding_box.top = 0.5 + (np.sin(i * np.pi/4) * 0.05)
            
        ball_track = Mock()
        ball_track.frames = frames
        
        metrics = self.analyzer._estimate_spin_rate(ball_track)
        self.assertIsNotNone(metrics.get('spin_rate'))
        self.assertTrue(1000 <= metrics['spin_rate'] <= 3500)
        
    def test_arm_angle_calculation(self):
        """Test arm angle calculation from pose data"""
        pose_annotation = Mock()
        pose_annotation.landmarks = []
        
        # Create mock landmarks for shoulder, elbow, wrist
        landmarks = {
            'right_shoulder': (0.5, 0.3, 0.0),
            'right_elbow': (0.6, 0.4, 0.0),
            'right_wrist': (0.7, 0.5, 0.0)
        }
        
        for name, (x, y, z) in landmarks.items():
            landmark = Mock()
            landmark.name = name
            landmark.x = x
            landmark.y = y
            landmark.z = z
            pose_annotation.landmarks.append(landmark)
            
        angle = self.analyzer._calculate_arm_angle([pose_annotation])
        self.assertIsNotNone(angle)
        self.assertTrue(0 <= angle <= 180)

if __name__ == '__main__':
    unittest.main() 