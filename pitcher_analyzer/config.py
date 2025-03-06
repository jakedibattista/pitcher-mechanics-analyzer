from pathlib import Path
import os
from pitcher_analyzer.data.pitcher_profiles import PITCHER_PROFILES

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
    
    # Complete pitcher profiles configuration
    PITCHER_PROFILES = {
        "AMATEUR": {
            "pitches": {
                "FASTBALL": {
                    "ideal_mechanics": {
                        "arm_slot": 70.0,  # More forgiving baseline
                        "stride_length": 0.85,  # Slightly shorter stride
                        "hip_shoulder_separation": 35.0,
                        "front_knee_flex": 43.0,
                        "trunk_tilt": 28.0
                    },
                    "velocity_range": (75, 85),  # Lower velocity expectations
                    "release_point": (5.5, 6.0),
                    "spin_rate": (1800, 2200)
                },
                "CURVEBALL": {
                    "ideal_mechanics": {
                        "arm_slot": 72.0,
                        "stride_length": 0.85,
                        "hip_shoulder_separation": 35.0,
                        "front_knee_flex": 45.0,
                        "trunk_tilt": 30.0
                    },
                    "velocity_range": (65, 75),
                    "release_point": (5.5, 6.0),
                    "spin_rate": (2000, 2400)
                },
                "SLIDER": {
                    "ideal_mechanics": {
                        "arm_slot": 70.0,
                        "stride_length": 0.85,
                        "hip_shoulder_separation": 35.0,
                        "front_knee_flex": 43.0,
                        "trunk_tilt": 28.0
                    },
                    "velocity_range": (70, 80),
                    "release_point": (5.5, 6.0),
                    "spin_rate": (2000, 2400)
                },
                "CHANGEUP": {
                    "ideal_mechanics": {
                        "arm_slot": 70.0,
                        "stride_length": 0.85,
                        "hip_shoulder_separation": 35.0,
                        "front_knee_flex": 43.0,
                        "trunk_tilt": 28.0
                    },
                    "velocity_range": (65, 75),
                    "release_point": (5.5, 6.0),
                    "spin_rate": (1600, 1800)
                }
            },
            "height": 72,  # Average height
            "handedness": "RIGHT",  # Default
            "signature_pitch": "FASTBALL",
            "is_amateur": True  # Flag for amateur analysis
        },
        "KERSHAW": {
            "pitches": {
                "FASTBALL": {
                    "ideal_mechanics": {
                        "arm_slot": 75.0,
                        "stride_length": 0.90,
                        "hip_shoulder_separation": 35.0,
                        "front_knee_flex": 45.0,
                        "trunk_tilt": 30.0
                    },
                    "velocity_range": (90, 93),
                    "release_point": (5.8, 6.2),
                    "spin_rate": (2200, 2400)
                },
                "CURVEBALL": {
                    "ideal_mechanics": {
                        "arm_slot": 80.0,
                        "stride_length": 0.88,
                        "hip_shoulder_separation": 38.0,
                        "front_knee_flex": 48.0,
                        "trunk_tilt": 32.0
                    },
                    "velocity_range": (72, 75),
                    "release_point": (5.9, 6.3),
                    "spin_rate": (2500, 2700)
                },
                "SLIDER": {
                    "ideal_mechanics": {
                        "arm_slot": 77.0,
                        "stride_length": 0.89,
                        "hip_shoulder_separation": 36.0,
                        "front_knee_flex": 46.0,
                        "trunk_tilt": 31.0
                    },
                    "velocity_range": (84, 87),
                    "release_point": (5.8, 6.2),
                    "spin_rate": (2700, 2900)
                },
                "CHANGEUP": {
                    "ideal_mechanics": {
                        "arm_slot": 75.0,
                        "stride_length": 0.90,
                        "hip_shoulder_separation": 35.0,
                        "front_knee_flex": 45.0,
                        "trunk_tilt": 30.0
                    },
                    "velocity_range": (83, 86),
                    "release_point": (5.8, 6.2),
                    "spin_rate": (1800, 2000)
                }
            },
            "height": 75,
            "handedness": "LEFT",
            "signature_pitch": "CURVEBALL"
        },
        "CORTES": {
            "pitches": {
                "FASTBALL": {
                    "ideal_mechanics": {
                        "arm_slot": 68.0,
                        "stride_length": 0.85,
                        "hip_shoulder_separation": 33.0,
                        "front_knee_flex": 40.0,
                        "trunk_tilt": 25.0
                    },
                    "velocity_range": (89, 92),
                    "release_point": (5.5, 5.9),
                    "spin_rate": (2100, 2300)
                },
                "SLIDER": {
                    "ideal_mechanics": {
                        "arm_slot": 65.0,
                        "stride_length": 0.84,
                        "hip_shoulder_separation": 32.0,
                        "front_knee_flex": 42.0,
                        "trunk_tilt": 26.0
                    },
                    "velocity_range": (78, 82),
                    "release_point": (5.4, 5.8),
                    "spin_rate": (2400, 2600)
                },
                "CHANGEUP": {
                    "ideal_mechanics": {
                        "arm_slot": 67.0,
                        "stride_length": 0.85,
                        "hip_shoulder_separation": 33.0,
                        "front_knee_flex": 41.0,
                        "trunk_tilt": 25.0
                    },
                    "velocity_range": (81, 84),
                    "release_point": (5.5, 5.9),
                    "spin_rate": (1700, 1900)
                },
                "CURVEBALL": {
                    "ideal_mechanics": {
                        "arm_slot": 70.0,
                        "stride_length": 0.86,
                        "hip_shoulder_separation": 34.0,
                        "front_knee_flex": 43.0,
                        "trunk_tilt": 27.0
                    },
                    "velocity_range": (72, 75),
                    "release_point": (5.6, 6.0),
                    "spin_rate": (2300, 2500)
                }
            },
            "height": 71,
            "handedness": "LEFT",
            "signature_pitch": "SLIDER"
        },
        "DEGROM": {
            "pitches": {
                "FASTBALL": {
                    "ideal_mechanics": {
                        "arm_slot": 73.0,
                        "stride_length": 0.95,
                        "hip_shoulder_separation": 42.0,
                        "front_knee_flex": 45.0,
                        "trunk_tilt": 32.0
                    },
                    "velocity_range": (98, 102),
                    "release_point": (6.2, 6.6),
                    "spin_rate": (2400, 2600)
                },
                "SLIDER": {
                    "ideal_mechanics": {
                        "arm_slot": 72.0,
                        "stride_length": 0.94,
                        "hip_shoulder_separation": 41.0,
                        "front_knee_flex": 44.0,
                        "trunk_tilt": 31.0
                    },
                    "velocity_range": (91, 94),
                    "release_point": (6.1, 6.5),
                    "spin_rate": (2800, 3000)
                },
                "CHANGEUP": {
                    "ideal_mechanics": {
                        "arm_slot": 73.0,
                        "stride_length": 0.95,
                        "hip_shoulder_separation": 42.0,
                        "front_knee_flex": 45.0,
                        "trunk_tilt": 32.0
                    },
                    "velocity_range": (88, 91),
                    "release_point": (6.2, 6.6),
                    "spin_rate": (1900, 2100)
                },
                "CURVEBALL": {
                    "ideal_mechanics": {
                        "arm_slot": 75.0,
                        "stride_length": 0.96,
                        "hip_shoulder_separation": 43.0,
                        "front_knee_flex": 46.0,
                        "trunk_tilt": 33.0
                    },
                    "velocity_range": (82, 85),
                    "release_point": (6.3, 6.7),
                    "spin_rate": (2600, 2800)
                }
            },
            "height": 76,
            "handedness": "RIGHT",
            "signature_pitch": "FASTBALL"
        },
        "OHTANI": {
            "pitches": {
                "FASTBALL": {
                    "ideal_mechanics": {
                        "arm_slot": 72.0,
                        "stride_length": 0.95,
                        "hip_shoulder_separation": 40.0,
                        "front_knee_flex": 42.0,
                        "trunk_tilt": 28.0
                    },
                    "velocity_range": (96, 101),
                    "release_point": (6.0, 6.4),
                    "spin_rate": (2300, 2500)
                },
                "SLIDER": {
                    "ideal_mechanics": {
                        "arm_slot": 73.0,
                        "stride_length": 0.94,
                        "hip_shoulder_separation": 39.0,
                        "front_knee_flex": 43.0,
                        "trunk_tilt": 29.0
                    },
                    "velocity_range": (82, 85),
                    "release_point": (6.1, 6.5),
                    "spin_rate": (2600, 2800)
                },
                "CHANGEUP": {
                    "ideal_mechanics": {
                        "arm_slot": 72.0,
                        "stride_length": 0.95,
                        "hip_shoulder_separation": 40.0,
                        "front_knee_flex": 42.0,
                        "trunk_tilt": 28.0
                    },
                    "velocity_range": (88, 91),
                    "release_point": (6.0, 6.4),
                    "spin_rate": (1800, 2000)
                },
                "CURVEBALL": {
                    "ideal_mechanics": {
                        "arm_slot": 74.0,
                        "stride_length": 0.96,
                        "hip_shoulder_separation": 41.0,
                        "front_knee_flex": 44.0,
                        "trunk_tilt": 30.0
                    },
                    "velocity_range": (75, 78),
                    "release_point": (6.2, 6.6),
                    "spin_rate": (2500, 2700)
                }
            },
            "height": 77,
            "handedness": "RIGHT",
            "signature_pitch": "SPLITTER"
        }
    }

    # Game context configurations
    GAME_CONTEXTS = {
        "REGULAR SEASON": {
            "mechanics_tolerance": 1.0,
            "velocity_adjustment": 0,
            "control_emphasis": 1.0
        },
        "HIGH PRESSURE": {
            "mechanics_tolerance": 0.8,
            "velocity_adjustment": 1,
            "control_emphasis": 1.2
        },
        "PERFECT GAME": {
            "mechanics_tolerance": 0.7,
            "velocity_adjustment": 2,
            "control_emphasis": 1.5
        },
        "UNKNOWN": {
            "mechanics_tolerance": 1.0,
            "velocity_adjustment": 0,
            "control_emphasis": 1.0
        }
    }
    
    # Vertex AI settings
    VERTEX_AI = {
        "project_id": "baseball-pitcher-analyzer",
        "location": "us-central1",
        "model_id": "pitcher-mechanics-model",  # Your model ID
        "endpoint_id": None,  # If using a specific endpoint
    }
    
    # Google API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # Get from environment variable instead
    
    # Vertex AI Configuration - Development defaults
    PROJECT_ID = "pitcher-analysis-dev"  # Default development project
    LOCATION = "us-central1"
    MODEL_ID = "pitcher-mechanics-model-v1"
    ENDPOINT_ID = "pitcher-mechanics-endpoint-1"
    
    # Analysis Configuration
    MIN_CONFIDENCE_THRESHOLD = 0.7
    FRAME_SAMPLE_RATE = 5
    
    # Analysis Settings
    FRAME_SAMPLE_COUNT = 5  # Number of key frames to analyze
    MIN_FRAME_QUALITY = 0.7  # Minimum quality threshold for frame analysis
    
    # Mechanics Thresholds
    MECHANICS_THRESHOLDS = {
        'AMATEUR': {
            'score_multiplier': 1.2,  # More forgiving scoring
            'deviation_threshold': 15  # Larger acceptable deviation range
        },
        'PRO': {
            'score_multiplier': 1.0,
            'deviation_threshold': 10
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
            
        cls.validate_config()
            
        return True 

    @classmethod
    def validate_config(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        if not cls.PROJECT_ID:
            raise ValueError("PROJECT_ID is not set")
        if not cls.MODEL_ID:
            raise ValueError("VERTEX_MODEL_ID environment variable is not set")
        if not cls.ENDPOINT_ID:
            raise ValueError("VERTEX_ENDPOINT_ID environment variable is not set") 