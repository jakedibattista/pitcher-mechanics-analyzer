"""Basic test suite for pitcher analyzer functionality."""

import unittest
import os
import sys
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pitcher_analyzer.analyzer import PitcherAnalyzer
from pitcher_analyzer.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality of the PitcherAnalyzer."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Skip tests if credentials not available
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            logger.warning("Skipping tests: No credentials available")
            sys.exit(0)
    
    def test_initialization(self):
        """Test that the analyzer can be initialized."""
        try:
            from google.oauth2 import service_account
            with open(os.getenv('GOOGLE_APPLICATION_CREDENTIALS')) as f:
                import json
                creds_dict = json.load(f)
            credentials = service_account.Credentials.from_service_account_info(creds_dict)
            analyzer = PitcherAnalyzer(credentials)
            self.assertIsNotNone(analyzer)
        except ImportError:
            self.skipTest("Google Cloud libraries not available")
    
    def test_config_validation(self):
        """Test that the configuration can be validated."""
        # Temporarily set credentials path for testing
        old_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials/service-account.json'
        
        try:
            # This should not raise an exception if directories exist
            result = Config.validate()
            self.assertTrue(result)
        except Exception as e:
            self.fail(f"Config validation raised exception: {e}")
        finally:
            # Restore original credentials path
            if old_creds:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = old_creds
            else:
                del os.environ['GOOGLE_APPLICATION_CREDENTIALS']

if __name__ == '__main__':
    unittest.main() 