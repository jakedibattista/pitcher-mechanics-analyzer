import time
from google.cloud import storage
from pathlib import Path
import logging
import shutil
import os
import subprocess
import tempfile
import requests
import cv2
import re
from google.cloud import vision

class VideoManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.storage_client = storage.Client()
        self.bucket_name = "baseball-pitcher-analyzer-videos"
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.temp_dir = Path(tempfile.gettempdir()) / "pitcher_analyzer"
        self.temp_dir.mkdir(exist_ok=True)
        self.vision_client = vision.ImageAnnotatorClient()
        
    def get_gcs_uri(self, video_path: str) -> str:
        """Get GCS URI for video, uploading if needed"""
        if video_path.startswith('gs://'):
            return video_path
            
        try:
            # Upload to GCS
            blob_name = f"videos/{Path(video_path).name}"
            blob = self.bucket.blob(blob_name)
            
            self.logger.info(f"Uploading video to GCS: {blob_name}")
            blob.upload_from_filename(video_path)
            
            return f"gs://{self.bucket_name}/{blob_name}"
            
        except Exception as e:
            self.logger.error(f"Upload failed: {str(e)}")
            return None

    def download_from_gcs(self, gcs_path):
        """Download video from GCS to local temp directory"""
        try:
            # Parse GCS path
            if gcs_path.startswith('gs://'):
                gcs_path = gcs_path.replace(f'gs://{self.bucket_name}/', '')
            
            # Create local path
            local_path = self.temp_dir / Path(gcs_path).name
            
            # Download blob
            blob = self.bucket.blob(gcs_path)
            blob.download_to_filename(str(local_path))
            
            self.logger.info(f"Downloaded video to: {local_path}")
            return str(local_path)
            
        except Exception as e:
            self.logger.error(f"Download failed: {str(e)}")
            return None

    def trim_video(self, video_path: str, duration: int = 5) -> str:
        """Trim video to specified duration"""
        try:
            # Ensure we have a local path
            if video_path.startswith('gs://'):
                video_path = self.download_from_gcs(video_path.replace(f'gs://{self.bucket_name}/', ''))
                if not video_path:
                    return None

            output_path = str(self.temp_dir / f"pitch_{Path(video_path).name}")
            
            # Use ffmpeg to trim
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-t', str(duration),
                '-c:v', 'copy',
                '-c:a', 'copy',
                output_path
            ]
            
            self.logger.info(f"Trimming video to {duration} seconds")
            subprocess.run(cmd, check=True, capture_output=True)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error trimming video: {str(e)}")
            return video_path  # Return original video if trim fails

    def find_video(self, video_name):
        """Find video locally or in cloud"""
        # Check local first
        local_videos = self.list_local_videos()
        for video in local_videos:
            if video_name in str(video):
                self.logger.info(f"Found local video: {video}")
                return str(video), "local"
        
        # Check cloud
        cloud_videos = self.list_cloud_videos()
        for video in cloud_videos:
            if video_name in video.name:
                self.logger.info(f"Found cloud video: gs://{self.bucket_name}/{video.name}")
                # Download the video
                local_path = self.download_from_gcs(video.name)
                if local_path:
                    return local_path, "local"
        
        return None, None

    def _check_ffmpeg(self):
        """Check if ffmpeg is available"""
        try:
            # Try both 'which' (Unix) and 'where' (Windows)
            if os.name == 'nt':  # Windows
                result = subprocess.run(['where', 'ffmpeg'], capture_output=True)
            else:  # Unix
                result = subprocess.run(['which', 'ffmpeg'], capture_output=True)
            return result.returncode == 0
        except:
            return False

    def list_local_videos(self):
        """List all videos in local directories"""
        video_locations = [
            Path.cwd(),  # Current directory
            Path.cwd() / "videos",  # videos subdirectory
            Path(__file__).parent / "tests/data",  # Test data directory
        ]
        
        videos = []
        for location in video_locations:
            if location.exists():
                videos.extend(list(location.glob("*dodgers*")))
                videos.extend(list(location.glob("*.mp4")))
                videos.extend(list(location.glob("*.mov")))
        
        return videos
        
    def list_cloud_videos(self):
        """List all videos in GCS bucket"""
        return list(self.bucket.list_blobs(prefix="videos/"))
        
    def get_gcs_uri(self, video_path: str) -> str:
        """Get GCS URI for video, uploading if needed"""
        if video_path.startswith('gs://'):
            return video_path
            
        try:
            # Upload to GCS
            blob_name = f"videos/{Path(video_path).name}"
            blob = self.bucket.blob(blob_name)
            
            self.logger.info(f"Uploading video to GCS: {blob_name}")
            blob.upload_from_filename(video_path)
            
            return f"gs://{self.bucket_name}/{blob_name}"
            
        except Exception as e:
            self.logger.error(f"Upload failed: {str(e)}")
            return None

    def detect_velocity(self, video_path):
        """Detect pitch velocity from broadcast overlay"""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Skip to frames after pitch (where velocity typically appears)
        # Usually 15-20 frames after release
        for _ in range(20):
            cap.read()
        
        # Region where velocity typically appears in broadcast
        # Usually top-right or bottom-right corner
        velocity = None
        
        # Check next 30 frames for velocity display
        for _ in range(30):
            ret, frame = cap.read()
            if not ret:
                break
            
            # Extract text from velocity regions using OCR
            # Common broadcast locations:
            regions = [
                frame[50:100, -150:-50],    # Top right
                frame[-100:-50, -150:-50],  # Bottom right
            ]
            
            for region in regions:
                # Use OCR to find velocity number
                text = self._ocr_text(region)
                if text:
                    # Look for pattern: number followed by MPH
                    match = re.search(r'(\d{2,3})\s*MPH', text, re.IGNORECASE)
                    if match:
                        velocity = int(match.group(1))
                        break
            
            if velocity:
                break
        
        cap.release()
        return velocity

    def _ocr_text(self, image):
        """Extract text from image using Google Cloud Vision"""
        # Convert image to bytes
        success, encoded = cv2.imencode('.jpg', image)
        if not success:
            return None
        
        content = encoded.tobytes()
        
        # Create image object
        image = vision.Image(content=content)
        
        # Perform text detection
        response = self.vision_client.text_detection(image=image)
        if response.error.message:
            return None
        
        texts = response.text_annotations
        if texts:
            return texts[0].description
        
        return None

    def get_video(self, video_name):
        """Download video from Google Cloud Storage"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            # Don't append .mp4 to the filename
            blob = bucket.blob(f"videos/{video_name}")
            
            # Create temp file
            temp_dir = tempfile.gettempdir()
            local_path = os.path.join(temp_dir, video_name)  # Removed .mp4 extension
            
            self.logger.info(f"Attempting to download {blob.name} from {self.bucket_name}")
            blob.download_to_filename(local_path)
            return local_path
            
        except Exception as e:
            self.logger.error(f"Error downloading video: {str(e)}")
            # List available files to help debug
            blobs = bucket.list_blobs(prefix="videos/")
            self.logger.info("Available files in bucket:")
            for blob in blobs:
                self.logger.info(f"- {blob.name}")
            return None 