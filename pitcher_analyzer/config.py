from pathlib import Path
import os

class Config:
    # Project settings
    PROJECT_ID = "baseball-pitcher-analyzer"
    LOCATION = "us-central1"
    BUCKET_NAME = "baseball-pitcher-analyzer-videos"
    
    # Directory paths
    BASE_DIR = Path(__file__).parent
    TEST_DATA_DIR = BASE_DIR / "tests/data"
    VIDEO_DIR = TEST_DATA_DIR / "videos"
    ANALYSIS_DIR = TEST_DATA_DIR / "analysis"
    DEBUG_DIR = BASE_DIR / "debug_frames"
    
    # Credentials
    CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
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
    
    # MLB Film Room Play IDs
    PLAY_IDS = {
        "FASTBALL": {
            "elite": "560a2f9b-9589-4e4b-95f5-2ef796334a94",
            "tired": "another-play-id-here",
            "normal": "another-play-id-here"
        },
        "CURVEBALL": {
            "elite": "play-id-here",
            "tired": "play-id-here",
            "normal": "play-id-here"
        },
        "SLIDER": {
            "elite": "play-id-here",
            "tired": "play-id-here",
            "normal": "play-id-here"
        }
    }
    
    # Pitching mechanics thresholds
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
    
    # Add to Config class
    PITCHER_PROFILES = {
        "KERSHAW": {
            "mechanics": {
                "arm_slot": "1 o'clock",
                "release_height": "6.4 feet",
                "stride_length": "87% of height",
                "hip_rotation_speed": "Elite",
                "curveball_specifics": {
                    "setup": {
                        "glove_height": "chest_level",
                        "foot_position": "third_base_side",
                        "hip_alignment": "closed"
                    },
                    "key_positions": {
                        "leg_lift": {
                            "knee_height": "belt",
                            "balance_point": "over_rubber",
                            "head_position": "centered"
                        },
                        "stride": {
                            "direction": "straight_to_plate",
                            "length": "87%_of_height",
                            "hip_shoulder_separation": "40_degrees"
                        },
                        "release": {
                            "arm_slot": "1_oclock",
                            "spine_tilt": "85_degrees",
                            "front_knee_flex": "45_degrees",
                            "head_position": "stable_centered"
                        }
                    },
                    "timing_sequence": {
                        "leg_lift_duration": "1.2_seconds",
                        "drive_to_plate": "0.4_seconds",
                        "arm_acceleration": "0.15_seconds"
                    }
                }
            },
            "pitches": {
                "CURVEBALL": {
                    "release_point": "High 3/4",
                    "arm_slot_variance": "± 0.5°",
                    "spine_angle": "85°",
                    "historical_data": {
                        "avg_spin_rate": "2650 RPM",
                        "vertical_break": "64 inches",
                        "release_height": "6.3-6.5 feet",
                        "arm_slot_consistency": "98%",
                        "signature_mechanics": [
                            "Extreme over-the-top arm slot",
                            "High elbow position at release",
                            "Strong front leg block",
                            "Maintained posture through release"
                        ],
                        "career_highlights": {
                            "best_curveball_season": "2016",
                            "whiff_rate": "52%",
                            "put_away_rate": "47%"
                        }
                    }
                },
                "SLIDER": {
                    # ... slider-specific data
                }
            },
            "career_stats": {
                "perfect_games": ["2014-06-18", "2022-04-13"]
            },
            "late_game_mechanics": {
                "arm_slot_consistency": "92%",
                "release_variance": "0.8 inches",
                "efficiency_rating": "88%"
            }
        },
        "CORTES": {
            "mechanics": {
                "typical_stride_length": 0.68,  # Shorter stride length
                "typical_arm_slots": {
                    "FASTBALL": 150,  # Higher arm slot
                    "SLIDER": 145,
                    "CUTTER": 145
                },
                "release_points": {
                    "FASTBALL": {"height": 5.9, "extension": 6.0},
                    "SLIDER": {"height": 5.8, "extension": 5.9},
                    "CUTTER": {"height": 5.8, "extension": 5.9}
                }
            },
            "career_stats": {
                "years_active": "2021-present",
                "typical_velocity": {
                    "FASTBALL": "92-94",
                    "SLIDER": "80-82",
                    "CUTTER": "86-88"
                }
            }
        },
        "WHEELER": {
            "mechanics": {
                "arm_slot": "High 3/4",
                "release_height": "6.2 feet",
                "stride_length": "90% of height",
                "hip_rotation_speed": "Elite+",
                "delivery_style": "Power/Athletic",
                "tempo": "Explosive",
                "slider_specifics": {
                    "setup": {
                        "glove_height": "chest_level",
                        "foot_position": "first_base_side",
                        "hip_alignment": "slightly_open",
                        "balance_point": "aggressive_coil"
                    },
                    "key_positions": {
                        "leg_lift": {
                            "knee_height": "waist",
                            "balance_point": "over_rubber",
                            "head_position": "centered",
                            "torso_tilt": "slight_first_base"
                        },
                        "stride": {
                            "direction": "direct_to_plate",
                            "length": "90%_of_height",
                            "hip_shoulder_separation": "45_degrees",
                            "front_foot_landing": "closed",
                            "timing": "explosive_from_gather"
                        },
                        "release": {
                            "arm_slot": "high_three_quarters",
                            "spine_tilt": "75_degrees",
                            "front_knee_flex": "45_degrees",
                            "head_position": "stable_centered",
                            "power_position": {
                                "front_hip_lock": "firm",
                                "torque_generation": "elite",
                                "shoulder_position": "uphill"
                            }
                        }
                    },
                    "unique_characteristics": {
                        "power_generation": "elite_lower_half",
                        "arm_speed": "explosive",
                        "front_side": "firm_and_closed",
                        "finish": "power_through_release"
                    }
                }
            },
            "pitches": {
                "SLIDER": {
                    "release_point": "High 3/4",
                    "arm_slot_variance": "± 0.4°",
                    "spine_angle": "75°",
                    "historical_data": {
                        "avg_spin_rate": "2450 RPM",
                        "horizontal_break": "6 inches",
                        "vertical_break": "-2 inches",
                        "release_height": "6.0-6.2 feet",
                        "arm_slot_consistency": "95%",
                        "velocity_band": "89-92 mph",
                        "signature_mechanics": [
                            "High three-quarters power slot",
                            "Explosive drive through release",
                            "Strong closed front side",
                            "Aggressive finish to first base",
                            "Elite hip-shoulder separation"
                        ],
                        "career_highlights": {
                            "best_slider_season": "2021",
                            "whiff_rate": "38%",
                            "put_away_rate": "35%",
                            "chase_rate": "42%"
                        },
                        "2021_specifics": {
                            "avg_velocity": "90.8 mph",
                            "max_velocity": "93.2 mph",
                            "horizontal_movement": "+4.2 inches",
                            "vertical_movement": "-1.8 inches",
                            "spin_efficiency": "85%"
                        }
                    }
                }
            },
            "mechanical_keys": {
                "power_position": "elite",
                "front_side": "firm",
                "direction": "inline",
                "tempo": "explosive",
                "arm_action": "clean_and_quick"
            }
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