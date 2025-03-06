from pathlib import Path
import os
from .data.pitcher_profiles import PITCHER_PROFILES

class Config:
    # Project settings
    PROJECT_ID = "baseball-pitcher-analyzer"
    PROJECT_NUMBER = "238493405692"
    LOCATION = "us-central1"  # Default Google Cloud region
    GCS_BUCKET = "baseball-pitcher-analyzer-videos"
    GCS_LOCATION = "US-CENTRAL1"
    
    # Directory paths
    BASE_DIR = Path(__file__).parent
    TEST_DATA_DIR = BASE_DIR / "tests/data"
    VIDEO_DIR = TEST_DATA_DIR / "videos"
    ANALYSIS_DIR = TEST_DATA_DIR / "analysis"
    DEBUG_DIR = BASE_DIR / "debug_frames"
    
    # Credentials
    CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Video processing settings
    VIDEO_SETTINGS = {
        "max_duration": 10,  # Maximum video length in seconds
        "required_fps": 30,  # Required frames per second
        "min_resolution": (640, 480)  # Minimum video resolution
    }
    
    # Analysis thresholds
    THRESHOLDS = {
        "min_velocity": 85.0,  # MPH
        "min_control": 70.0,  # percentage
        "max_pitch_duration": 0.45  # seconds
    }
    
    # Video settings
    VIDEO_REQUIREMENTS = {
        "max_duration": 15,     # Increased to allow full pitch sequence
        "min_duration": 5,      # Increased to ensure we capture wind-up
        "pitch_segment": {
            "pre_pitch": 3,     # Seconds before pitch release
            "post_pitch": 2,    # Seconds after pitch release
            "total": 5          # Total segment duration
        },
        "required_formats": [".mp4", ".mov"],
        "min_resolution": (720, 480),  # width, height
        "fps": 60  # Most baseball footage is 60fps
    }
    
    # Analysis settings
    ANALYSIS = {
        "timeout": 300,  # seconds
        "pitcher_velocity_threshold": 85,  # mph for pull decision
        "min_confidence": 0.5
    }
    
    # Visualization settings
    VISUALIZATION = {
        "output_fps": 30,
        "font_scale": 0.5,
        "colors": {
            "pose_landmarks": (0, 255, 0),  # green
            "connections": (255, 255, 0),   # yellow
            "text": (255, 255, 255)         # white
        },
        "line_thickness": 2
    }
    
    # Mechanics thresholds
    MECHANICS = {
        "max_arm_angle_variance": 5.0,  # degrees
        "min_stride_length": 0.85,  # % of height
        "min_hip_shoulder_separation": 30.0,  # degrees
        "max_balance_variation": 0.1,  # normalized
        "min_follow_through": 0.8,  # completion %
        
        # Key pose landmarks
        "landmarks": {
            "shoulder": ["LEFT_SHOULDER", "RIGHT_SHOULDER"],
            "hip": ["LEFT_HIP", "RIGHT_HIP"],
            "knee": ["LEFT_KNEE", "RIGHT_KNEE"],
            "ankle": ["LEFT_ANKLE", "RIGHT_ANKLE"],
            "elbow": ["LEFT_ELBOW", "RIGHT_ELBOW"],
            "wrist": ["LEFT_WRIST", "RIGHT_WRIST"]
        },
        "validation": {
            "min_visibility_threshold": 0.5,
            "min_valid_frames": 4,
            "max_angle_change": 45.0,  # degrees per frame
            "min_joint_distance": 0.05  # 5% of frame height
        }
    }
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.CREDENTIALS_PATH:
            raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS")
            
        if not os.path.exists(cls.CREDENTIALS_PATH):
            raise ValueError(f"Credentials file not found: {cls.CREDENTIALS_PATH}")
            
        # Ensure required directories exist
        directories = [
            cls.TEST_DATA_DIR,
            cls.VIDEO_DIR,
            cls.ANALYSIS_DIR,
            cls.DEBUG_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        return True 