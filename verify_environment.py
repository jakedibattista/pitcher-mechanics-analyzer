import os
from google.cloud import storage
import logging
from pathlib import Path

class EnvironmentVerifier:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.required_dirs = [
            'analysis_output',
            'pitcher_analyzer/tests/data',
            'sample_videos'
        ]
        
    def verify_all(self):
        """Run all verification checks"""
        try:
            checks = [
                self.check_credentials(),
                self.check_gcs_setup(),
                self.check_directories(),
                self.check_dependencies()
            ]
            
            if all(checks):
                self.logger.info("All environment checks passed!")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Environment verification failed: {str(e)}")
            return False
            
    def check_credentials(self):
        """Check Google Cloud credentials"""
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path:
            self.logger.error("GOOGLE_APPLICATION_CREDENTIALS not set")
            return False
            
        if not os.path.exists(creds_path):
            self.logger.error(f"Credentials file not found: {creds_path}")
            return False
            
        self.logger.info(f"Found credentials at: {creds_path}")
        return True
        
    def check_gcs_setup(self):
        """Verify Google Cloud Storage setup"""
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket("baseball-pitcher-analyzer-videos")
            
            if not bucket.exists():
                self.logger.warning("Main storage bucket does not exist")
                return False
                
            self.logger.info("GCS setup verified")
            return True
            
        except Exception as e:
            self.logger.error(f"GCS setup check failed: {str(e)}")
            return False
            
    def check_directories(self):
        """Verify required directories exist"""
        for dir_path in self.required_dirs:
            path = Path(dir_path)
            if not path.exists():
                self.logger.info(f"Creating directory: {path}")
                path.mkdir(parents=True, exist_ok=True)
                
        return True
        
    def check_dependencies(self):
        """Verify required Python packages"""
        required_packages = [
            'google-cloud-storage',
            'google-cloud-videointelligence',
            'opencv-python',
            'numpy',
            'vertexai'
        ]
        
        import pkg_resources
        installed = [pkg.key for pkg in pkg_resources.working_set]
        
        missing = [pkg for pkg in required_packages if pkg not in installed]
        
        if missing:
            self.logger.error(f"Missing packages: {missing}")
            return False
            
        return True

    def check_ffmpeg(self):
        """Verify ffmpeg installation"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                 capture_output=True, 
                                 text=True)
            return result.returncode == 0
        except:
            return False

def verify_environment():
    checks = {
        'ffmpeg': check_ffmpeg(),
        'google_cloud': check_google_cloud(),
        'opencv': check_opencv(),
        'numpy': check_numpy(),
        'credentials': check_credentials()
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    verifier = EnvironmentVerifier()
    verifier.verify_all() 