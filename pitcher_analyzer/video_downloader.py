import os
import cv2
import requests
from pathlib import Path
from config import PLAY_IDS, TEST_DATA_DIR, VIDEO_DIR, VIDEO_REQUIREMENTS

class MLBVideoDownloader:
    def __init__(self):
        self.base_url = "https://www.mlb.com/video/search"
        
        # Create directory structure
        self._setup_directories()
        
    def _setup_directories(self):
        """Create necessary directory structure"""
        directories = [TEST_DATA_DIR, VIDEO_DIR]
        for pitch_type in PLAY_IDS.keys():
            directories.append(VIDEO_DIR / pitch_type.lower())
            
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate_video(self, video_path):
        """Validate downloaded video meets requirements"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            # Check if video opened successfully
            if not cap.isOpened():
                return False, "Could not open video file"
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps
            
            # Validate requirements
            if duration > VIDEO_REQUIREMENTS["max_duration"]:
                return False, f"Video too long: {duration:.1f}s"
            if duration < VIDEO_REQUIREMENTS["min_duration"]:
                return False, f"Video too short: {duration:.1f}s"
            if width < VIDEO_REQUIREMENTS["min_resolution"][0] or \
               height < VIDEO_REQUIREMENTS["min_resolution"][1]:
                return False, f"Resolution too low: {width}x{height}"
                
            return True, "Video meets requirements"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
        finally:
            if 'cap' in locals():
                cap.release()
    
    def setup_for_play(self, pitch_type, condition, play_id):
        """Setup directory and generate URL for a specific play"""
        # Create specific directory path
        output_dir = VIDEO_DIR / pitch_type.lower()
        output_path = output_dir / f"{condition}_{play_id}.mp4"
        
        url = f"{self.base_url}?q=playid=\"{play_id}\""
        
        print(f"\nFor {pitch_type} - {condition}:")
        print(f"1. Open this URL: {url}")
        print(f"2. Download the video")
        print(f"3. Save it to: {output_path}")
        
        return url, output_path

def download_video(url: str, save_path: str) -> str:
    """
    Download video from URL and save to specified path
    """
    save_dir = Path(save_path).parent
    save_dir.mkdir(parents=True, exist_ok=True)
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    return save_path

# Example usage
if __name__ == "__main__":
    downloader = MLBVideoDownloader()
    
    # Process each pitch type and condition
    for pitch_type, conditions in PLAY_IDS.items():
        for condition, play_id in conditions.items():
            url, path = downloader.setup_for_play(pitch_type, condition, play_id)
            
            # If video exists, validate it
            if path.exists():
                is_valid, message = downloader.validate_video(path)
                print(f"Validation: {message}") 