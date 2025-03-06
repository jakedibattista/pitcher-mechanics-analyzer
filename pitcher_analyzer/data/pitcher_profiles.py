"""
Pitcher profiles containing detailed mechanics data for analysis.
This module is separated from the main config to improve maintainability.
"""

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
    # Other pitchers...
} 