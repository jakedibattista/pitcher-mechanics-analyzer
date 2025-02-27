from google.cloud import storage
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import logging
import os
from pathlib import Path
import cv2
import base64
import tempfile
from .pitcher_data import PITCHER_PROFILES

class PitcherAnalyzer:
    def __init__(self, credentials):
        """Initialize with Google Cloud credentials"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize Google Cloud clients
        self.storage_client = storage.Client(
            project="baseball-pitcher-analyzer",
            credentials=credentials
        )
        
        # Initialize Vertex AI
        vertexai.init(
            project="baseball-pitcher-analyzer",
            location="us-central1",
            credentials=credentials
        )
        self.multimodal_model = GenerativeModel("gemini-pro-vision")  # Changed back to vision model
        
        # Set up Cloud Storage bucket
        self.bucket_name = "baseball-pitcher-analyzer-videos"
        self.ensure_bucket_exists()
        
        # Use verified pitcher profiles
        self.pitcher_profiles = PITCHER_PROFILES
        
    def ensure_bucket_exists(self):
        """Ensure the Cloud Storage bucket exists"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                # Create bucket in us-central1 to match Vertex AI location
                bucket = self.storage_client.create_bucket(
                    self.bucket_name, 
                    location="us-central1"
                )
                self.logger.info(f"Created new bucket: {self.bucket_name}")
            else:
                self.logger.info(f"Using existing bucket: {self.bucket_name}")
            return bucket
        except Exception as e:
            self.logger.error(f"Error ensuring bucket exists: {str(e)}")
            raise
            
    def analyze_pitch(self, video_path, pitcher_name, pitch_type):
        """Main analysis function"""
        try:
            # Extract frames from video
            frames = self._extract_frames(video_path)
            if not frames:
                raise ValueError("No frames could be extracted from video")

            # Get analysis from Vertex AI
            analysis = self._analyze_mechanics(frames, pitcher_name, pitch_type)
            if not analysis:
                raise ValueError("Mechanics analysis failed")

            # Parse scores from analysis
            scores = self._parse_scores(analysis)
            
            return {
                **scores,
                'analysis': analysis
            }
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return None

    def _extract_frames(self, video_path, num_frames=8):
        """Extract key frames from video for analysis"""
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Get frames at key points of pitch
            indices = [int(i * total_frames / (num_frames + 1)) for i in range(1, num_frames + 1)]
            
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # Convert frame to base64 for Vertex AI
                    _, buffer = cv2.imencode('.jpg', frame)
                    frames.append({
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(buffer).decode('utf-8')
                    })
            
            cap.release()
            return frames
            
        except Exception as e:
            self.logger.error(f"Frame extraction failed: {str(e)}", exc_info=True)
            if 'cap' in locals():
                cap.release()
            return None

    def _analyze_mechanics(self, frames, pitcher_name, pitch_type):
        """Analyze mechanics using Vertex AI Vision"""
        try:
            prompt = self._get_analysis_prompt(pitcher_name, pitch_type)
            
            # Prepare content for Vertex AI
            content = [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        *[{"inline_data": frame} for frame in frames]
                    ]
                }
            ]
            
            # Get response from model
            response = self.multimodal_model.generate_content(
                content,
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": 0.4,
                    "top_p": 0.8,
                    "top_k": 40
                }
            )
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Mechanics analysis failed: {str(e)}", exc_info=True)
            return None

    def _get_analysis_prompt(self, pitcher_name, pitch_type):
        """Get analysis prompt based on pitcher and pitch type"""
        profile = self.pitcher_profiles.get(pitcher_name, {})
        pitch_data = profile.get("pitches", {}).get(pitch_type, {})
        mechanics = profile.get("mechanics", {})
        
        # Get pitch-specific mechanics
        pitch_mechanics = mechanics.get(f"{pitch_type.lower()}_specifics", {})
        release_data = pitch_data.get("release_point", "")
        arm_slot = pitch_data.get("arm_slot_variance", "")
        spine_angle = pitch_data.get("spine_angle", "")
        
        base_prompt = f"""You are a professional baseball pitching coach analyzing {pitcher_name}'s {pitch_type.lower()} pitch sequence.

Reference Profile for {pitch_type}:
• Expected Release Point: {release_data}
• Arm Slot Variance: {arm_slot}
• Spine Angle: {spine_angle}
• Base Mechanics:
  - Arm Slot: {mechanics.get('arm_slot')}
  - Release Height: {mechanics.get('release_height')}
  - Stride Length: {mechanics.get('stride_length')}

Analyze the mechanics and provide scores and bullet points in exactly this format:

Mechanics Score: [X]/10
• [First point about mechanics, specifically for {pitch_type.lower()}]
• [Second point about mechanics]
• [Third point about mechanics]

Match to Ideal Form: [X]/10
• [First comparison to {pitcher_name}'s ideal {pitch_type.lower()} mechanics]
• [Second comparison point focusing on {pitch_type.lower()}-specific form]
• [Third comparison point]

Injury Risk Score: [X]/10 (lower is better)
• [First risk factor specific to {pitch_type.lower()} mechanics]
• [Second risk factor]
• [Third risk factor]

Recommendations:
• [First specific improvement for {pitch_type.lower()} mechanics]
• [Second specific improvement]

Remember to replace [X] with actual scores between 0-10."""

        return base_prompt

    def _parse_scores(self, analysis):
        """Parse scores from analysis text"""
        try:
            import re
            
            # Initialize scores
            mechanics_score = 0
            ideal_score = 0
            injury_score = 0
            
            # Extract scores using regex patterns
            # Look for "Score: X/10" patterns
            mechanics_match = re.search(r'Mechanics Score:\s*(\d+)/10', analysis)
            if mechanics_match:
                mechanics_score = int(mechanics_match.group(1))
                
            ideal_match = re.search(r'Match to Ideal.*?:\s*(\d+)/10', analysis)
            if ideal_match:
                ideal_score = int(ideal_match.group(1))
                
            injury_match = re.search(r'Injury Risk Score:\s*(\d+)/10', analysis)
            if injury_match:
                injury_score = int(injury_match.group(1))
                
            # Log extracted scores
            self.logger.info(f"Parsed scores - Mechanics: {mechanics_score}, "
                            f"Ideal Match: {ideal_score}, Injury Risk: {injury_score}")
            
            # Validate scores are in range 0-10
            for score_name, score in [("Mechanics", mechanics_score), 
                                    ("Ideal Match", ideal_score), 
                                    ("Injury Risk", injury_score)]:
                if not 0 <= score <= 10:
                    self.logger.warning(f"Invalid {score_name} score: {score}, defaulting to 0")
                    if score_name == "Mechanics":
                        mechanics_score = 0
                    elif score_name == "Ideal Match":
                        ideal_score = 0
                    else:
                        injury_score = 0
            
            return {
                'mechanics_score': mechanics_score,
                'ideal_match': ideal_score,
                'fatigue_score': injury_score  # Keeping fatigue_score for consistency
            }
            
        except Exception as e:
            self.logger.error(f"Score parsing failed: {str(e)}", exc_info=True)
            return {
                'mechanics_score': 0,
                'ideal_match': 0,
                'fatigue_score': 0
            }

def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Uploads a file to Google Cloud Storage.
    
    Args:
        bucket_name (str): Your GCS bucket name
        source_file_path (str): Path to your local video file
        destination_blob_name (str): Name to give the file in GCS
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)
    print(f"File {source_file_path} uploaded to gs://{bucket_name}/{destination_blob_name}")

def check_and_create_bucket(project_id, bucket_name, location="us-central1"):
    """
    Checks if a bucket exists and creates it if it doesn't.
    
    Args:
        project_id (str): Your Google Cloud project ID
        bucket_name (str): Name for your bucket
        location (str): Location for the bucket
    """
    storage_client = storage.Client()
    
    # Check if bucket exists
    bucket = storage_client.lookup_bucket(bucket_name)
    
    if bucket is None:
        print(f"Bucket {bucket_name} does not exist. Creating...")
        bucket = storage_client.create_bucket(bucket_name, location=location)
        print(f"Bucket {bucket_name} created in {location}")
    else:
        print(f"Bucket {bucket_name} already exists")
    
    return bucket

# List all existing buckets
def list_buckets(project_id):
    """Lists all buckets in the project."""
    storage_client = storage.Client(project_id)
    buckets = storage_client.list_buckets()
    
    print("Existing buckets:")
    for bucket in buckets:
        print(f"- {bucket.name}")

# Example usage:
# upload_to_gcs(
#     "your-bucket-name",
#     "path/to/your/local/video.mp4",
#     "pitcher_videos/video.mp4"
# )

# Your project ID
project_id = "baseball-pitcher-analyzer"

# First, let's see what buckets you already have
list_buckets(project_id)

# Let's create a bucket if needed (bucket names must be globally unique)
bucket_name = "baseball-pitcher-analyzer-videos"
bucket = check_and_create_bucket(project_id, bucket_name)
