"""
Pitcher profiles containing detailed mechanics data for analysis.
This module is separated from the main config to improve maintainability.
"""

PITCHER_PROFILES = {
    "KERSHAW": {
        "pitches": {
            "FASTBALL": {
                "ideal_mechanics": {
                    "arm_slot": 75.0,  # degrees
                    "stride_length": 0.90,  # % of height
                    "hip_shoulder_separation": 35.0,  # degrees
                    "front_knee_flex": 45.0,  # degrees
                    "trunk_tilt": 30.0  # degrees
                },
                "velocity_range": (90, 93),
                "release_point": (5.8, 6.2),  # feet
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
        "height": 75,  # inches
        "handedness": "LEFT",
        "signature_pitch": "CURVEBALL",
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

# Game context adjustments
GAME_CONTEXT_ADJUSTMENTS = {
    "Regular Season": {
        "mechanics_tolerance": 1.0,  # baseline
        "velocity_adjustment": 0,
        "control_emphasis": 1.0
    },
    "High Pressure": {
        "mechanics_tolerance": 0.8,  # stricter mechanics requirements
        "velocity_adjustment": 1,    # slight velocity boost expected
        "control_emphasis": 1.2      # more emphasis on control
    },
    "Perfect Game": {
        "mechanics_tolerance": 0.7,  # very strict mechanics requirements
        "velocity_adjustment": 2,    # higher velocity expected
        "control_emphasis": 1.5      # heavy emphasis on control
    },
    "Unknown": {
        "mechanics_tolerance": 1.0,
        "velocity_adjustment": 0,
        "control_emphasis": 1.0
    }
} 