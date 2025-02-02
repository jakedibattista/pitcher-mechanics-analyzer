import unittest
from pathlib import Path
import sys

# Add test suites
from .test_suite import TestPitcherAnalyzer
from .test_video import TestVideoManager
from .test_visualization import TestPitchVisualizer

def run_all_tests():
    """Run all test suites"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPitcherAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestVideoManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPitchVisualizer))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

# Remove ball tracking tests
# Add pose analysis tests
class TestPoseAnalysis(unittest.TestCase):
    def test_pose_detection(self):
        ...
    def test_mechanics_analysis(self):
        ...

if __name__ == '__main__':
    sys.exit(run_all_tests()) 