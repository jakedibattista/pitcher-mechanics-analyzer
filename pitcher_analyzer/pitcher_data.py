from .config import PITCHER_PROFILES as CONFIG_PROFILES

PITCHER_PROFILES = {}

for pitcher, data in CONFIG_PROFILES.items():
    PITCHER_PROFILES[pitcher] = {
        "mechanics": data["mechanics"],
        "pitches": {}
    }
    
    # Add pitch-specific data
    if "pitches" in data:
        for pitch_type, pitch_data in data["pitches"].items():
            PITCHER_PROFILES[pitcher]["pitches"][pitch_type] = {
                "source": "MLB Config Data",
                "mechanics": data["mechanics"].get(f"{pitch_type.lower()}_specifics", {}),
                "release_data": {
                    "point": pitch_data.get("release_point"),
                    "arm_slot_variance": pitch_data.get("arm_slot_variance"),
                    "spine_angle": pitch_data.get("spine_angle")
                },
                "historical_data": pitch_data.get("historical_data", {})
            }
    
    # Add additional profile data
    if "career_stats" in data:
        PITCHER_PROFILES[pitcher]["career_stats"] = data["career_stats"]
    if "mechanical_keys" in data:
        PITCHER_PROFILES[pitcher]["mechanical_keys"] = data["mechanical_keys"]
    if "late_game_mechanics" in data:
        PITCHER_PROFILES[pitcher]["late_game_mechanics"] = data["late_game_mechanics"] 