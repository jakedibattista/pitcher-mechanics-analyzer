import streamlit as st
import os
from google.oauth2 import service_account
from google.cloud import storage
import tempfile
from pitcher_analyzer.analyzer import PitcherAnalyzer
from pitcher_analyzer.config import PITCHER_PROFILES
import cv2
from dotenv import load_dotenv
from pitcher_analyzer.game_state import GameStateManager
import datetime

# Add pitcher ID mapping
PITCHER_ID_MAPPING = {
    "KERSHAW": "477132",  # Clayton Kershaw's MLB ID
    "CORTES": "641482",   # Nestor Cortes' MLB ID
    # Add more pitchers as needed
}

# Add team mapping for pitchers
PITCHER_TEAM_MAPPING = {
    "KERSHAW": "LAD",
    "CORTES": "NYY",
    # Add more pitchers as needed
}

# Add sample game data
SAMPLE_GAMES = {
    "LAD": [
        {"date": "2023-04-01", "opponent": "ARI", "game_pk": "661413", "description": "vs Diamondbacks (Home)"},
        {"date": "2023-04-02", "opponent": "ARI", "game_pk": "661414", "description": "vs Diamondbacks (Home)"},
        {"date": "2023-04-05", "opponent": "COL", "game_pk": "661419", "description": "vs Rockies (Home)"},
        {"date": "2023-04-07", "opponent": "SF", "game_pk": "661425", "description": "@ Giants (Away)"},
        {"date": "2023-04-10", "opponent": "SF", "game_pk": "661430", "description": "@ Giants (Away)"},
    ],
    "NYY": [
        {"date": "2023-04-01", "opponent": "BOS", "game_pk": "661240", "description": "vs Red Sox (Home)"},
        {"date": "2023-04-02", "opponent": "BOS", "game_pk": "661241", "description": "vs Red Sox (Home)"},
        {"date": "2023-04-04", "opponent": "PHI", "game_pk": "661245", "description": "vs Phillies (Home)"},
        {"date": "2023-04-07", "opponent": "BAL", "game_pk": "661250", "description": "@ Orioles (Away)"},
        {"date": "2023-04-09", "opponent": "BAL", "game_pk": "661255", "description": "@ Orioles (Away)"},
    ]
}

# Add notable games data
NOTABLE_GAMES = {
    "KERSHAW": [
        {"date": "2014-06-18", "opponent": "COL", "game_pk": "382456", "description": "No-Hitter vs Rockies"},
        {"date": "2017-10-06", "opponent": "ARI", "game_pk": "526476", "description": "NLDS Game 1"},
        {"date": "2022-04-13", "opponent": "MIN", "game_pk": "661333", "description": "Perfect Game (7 innings)"}
    ],
    "CORTES": [
        {"date": "2022-04-21", "opponent": "DET", "game_pk": "661328", "description": "15 Strikeout Game"},
        {"date": "2022-10-09", "opponent": "CLE", "game_pk": "715769", "description": "ALDS Game 3"}
    ]
}

def initialize_google_credentials():
    """Initialize Google Cloud credentials from Streamlit secrets"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        return credentials
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Google Cloud credentials: {str(e)}")

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary location and return path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving uploaded file: {str(e)}")
        return None

def get_available_pitchers_and_pitches():
    """Get available pitchers and their pitch types from config"""
    available_pitchers = {}
    for pitcher, data in PITCHER_PROFILES.items():
        if "pitches" in data:
            available_pitchers[pitcher] = {
                "pitches": list(data["pitches"].keys()),
                "mechanics": data.get("mechanics", {}),
                "stats": data.get("career_stats", {})
            }
    return available_pitchers

def check_credentials():
    """Check if credentials file exists and is accessible"""
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path:
        st.error("🚫 Google Cloud credentials path not set")
        st.stop()
    if not os.path.exists(creds_path):
        st.error(f"🚫 Credentials file not found at: {creds_path}")
        st.stop()
    return True

def render_pitcher_selection():
    """Render the pitcher selection UI components"""
    available_pitchers = get_available_pitchers_and_pitches()
    
    # Add explanation about available pitchers
    st.info("""
        This tool analyzes pitches by comparing them to verified MLB mechanics data.
        Currently, we have detailed mechanics profiles for select elite pitchers and their signature pitches.
        More pitchers will be added as verified data becomes available.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        pitcher_name = st.selectbox(
            "Select Pitcher",
            options=list(available_pitchers.keys()),
            index=0,
            key="pitcher_selector"
        )
    
    with col2:
        pitch_type = st.selectbox(
            "Select Pitch Type",
            options=available_pitchers[pitcher_name]["pitches"],
            index=0,
            key="pitch_type_selector"
        )
        
    return pitcher_name, pitch_type

def render_game_selection(pitcher_name):
    """Render improved game selection dropdown"""
    st.subheader("Select Game Context")
    
    # Add explanation about game context
    with st.expander("How does game context affect analysis?"):
        st.markdown("""
        ### Impact of Game Context on Analysis
        
        Selecting a specific game provides additional context that enhances our analysis:
        
        - **Fatigue Analysis**: Late-inning or high pitch count situations may reveal how mechanics change under fatigue
        - **Pressure Situations**: High-leverage situations often show different mechanical patterns
        - **Game Conditions**: Weather, stadium, and game importance can affect mechanics
        - **Historical Comparison**: Compare mechanics across different games to identify patterns
        
        When "Unknown" is selected, the analysis focuses purely on mechanical efficiency without contextual factors.
        """)
    
    # Get team for the selected pitcher
    team = PITCHER_TEAM_MAPPING.get(pitcher_name)
    
    # Create game selection categories
    selection_type = st.radio(
        "Game Selection",
        ["Unknown", "Recent Games", "Notable Games", "Search by Date"],
        horizontal=True
    )
    
    if selection_type == "Unknown":
        st.info("Unknown game context - analysis will focus on mechanics only")
        return None
        
    elif selection_type == "Recent Games":
        # Get recent games (limited to 5)
        recent_games = SAMPLE_GAMES.get(team, [])[:5]
        
        if not recent_games:
            st.warning(f"No recent games found for {pitcher_name}")
            return None
            
        # Create display options
        display_options = [f"{game['date']} - {game['description']}" for game in recent_games]
        
        selected_index = st.selectbox(
            "Select Recent Game",
            options=display_options,
            key="recent_game_selector"
        )
        
        # Get selected game
        selected_game = recent_games[display_options.index(selected_index)]
        
    elif selection_type == "Notable Games":
        # Notable games like no-hitters, perfect games, playoff games
        notable_games = NOTABLE_GAMES.get(pitcher_name, [])
        
        if not notable_games:
            st.warning(f"No notable games found for {pitcher_name}")
            return None
            
        display_options = [f"{game['date']} - {game['description']}" for game in notable_games]
        
        selected_index = st.selectbox(
            "Select Notable Game",
            options=display_options,
            key="notable_game_selector"
        )
        
        selected_game = notable_games[display_options.index(selected_index)]
        
    elif selection_type == "Search by Date":
        # Allow selecting by date
        selected_date = st.date_input(
            "Select Date",
            value=datetime.date.today() - datetime.timedelta(days=30)
        )
        
        # In a real implementation, we would search the MLB API for games on this date
        st.info(f"Searching for games on {selected_date}")
        
        # Mock implementation - just return None for now
        return None
    
    # Display selected game info and return
    if 'selected_game' in locals():
        st.info(f"Selected game: {selected_game['date']} - {selected_game['description']}")
        
        # Get pitcher ID
        pitcher_id = PITCHER_ID_MAPPING.get(pitcher_name, "")
        
        # Return game info
        return {
            "game_pk": selected_game['game_pk'],
            "pitcher_id": pitcher_id,
            "date": selected_game['date'],
            "opponent": selected_game['opponent'],
            "description": selected_game['description']
        }
    
    return None

def render_video_uploader():
    """Render the video upload component"""
    st.subheader("Upload Pitch Video")
    
    # Add video requirements info
    st.info("""
        **Video Requirements:**
        • Duration: 5-15 seconds
        • Format: MP4 or MOV
        • Minimum resolution: 720x480
        • Recommended: 60 FPS
        
        Best Practices:
        • Include 3 seconds before pitch release
        • Include 2 seconds after release
        • Film from side view
        • Ensure good lighting
        • Keep camera stable
    """)
    
    uploaded_file = st.file_uploader(
        "Upload Pitch Video", 
        type=["mp4", "mov", "avi"],
        help="Upload a video of a single pitch. For best results, video should start before wind-up and end after follow-through."
    )
    return uploaded_file

def validate_video(video_path):
    """Validate the uploaded video file"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"valid": False, "error": "Could not open video file"}
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        # Release the video capture
        cap.release()
        
        # Check video properties
        warnings = []
        if duration < 3:
            warnings.append("⚠️ Video is very short. For best results, include the entire pitch sequence.")
        if duration > 15:
            warnings.append("⚠️ Video is quite long. Analysis may take more time.")
        if width < 640 or height < 480:
            warnings.append("⚠️ Video resolution is low. This may affect analysis accuracy.")
        if fps < 24:
            warnings.append("⚠️ Video frame rate is low. This may affect motion analysis.")
            
        return {
            "valid": True,
            "properties": {
                "fps": fps,
                "duration": duration,
                "resolution": f"{width}x{height}"
            },
            "warnings": warnings
        }
        
    except Exception as e:
        return {"valid": False, "error": str(e)}

def display_analysis_results(result):
    """Display the analysis results in the UI with enhanced details"""
    st.success("Analysis complete!")
    
    # Create three columns for metrics
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric(
            "Mechanics Score", 
            f"{result.get('mechanics_score', 'N/A')}/10",
            help="Overall quality of arm mechanics and balance"
        )
    
    with m2:
        # Use the correct key name
        ideal_score = result.get('ideal_match_score', result.get('ideal_form_score', 'N/A'))
        st.metric(
            "Match to Ideal",
            f"{ideal_score}/10",
            help="How closely the mechanics match the ideal form for this pitch type"
        )
    
    with m3:
        # Use the correct key name
        score = result.get('injury_risk_score', result.get('fatigue_score', 'N/A'))
        if isinstance(score, int):
            color = "normal" if score <= 3 else "off" if score <= 6 else "inverse"
            st.metric(
                "Injury Risk", 
                f"{score}/10",
                help="Risk of injury based on mechanics (lower is better)",
                delta="Low Risk" if score <= 3 else "Medium Risk" if score <= 6 else "High Risk",
                delta_color=color
            )
        else:
            st.metric("Injury Risk", "N/A", help="Risk of injury based on mechanics (lower is better)")
    
    # Display detailed mechanical analysis
    if 'mechanical_analysis' in result:
        st.subheader("Mechanical Analysis")
        st.markdown(result['mechanical_analysis'])
        
    # Display injury risk assessment
    if 'injury_analysis' in result:
        st.subheader("Injury Risk Assessment")
        st.markdown(result['injury_analysis'])
        
    # Display performance impact
    if 'performance_impact' in result:
        st.subheader("Performance Impact")
        st.markdown(result['performance_impact'])
    
    # Display recommendations if available
    if 'recommendations' in result and result['recommendations']:
        st.subheader("Recommendations")
        for rec in result['recommendations']:
            st.markdown(f"• {rec}")
            
    # Add option to view full analysis
    with st.expander("View Full Analysis"):
        if 'analysis' in result:
            st.markdown(result['analysis'])

def main():
    """Main function to run the Streamlit app"""
    st.set_page_config(
        page_title="Pitcher Mechanics Analyzer",
        page_icon="⚾",
        layout="wide"
    )
    
    st.title("⚾ Pitcher Mechanics Analyzer")
    st.markdown("""
        Upload a video of a pitcher's delivery to analyze mechanics, compare to ideal form,
        and get recommendations for improvement.
    """)
    
    # Initialize analyzer
    try:
        credentials = initialize_google_credentials()
        analyzer = PitcherAnalyzer(credentials)
    except Exception as e:
        st.error(f"Error initializing Google Cloud credentials: {str(e)}")
        st.stop()
    
    # Step 1: Select pitcher and pitch type
    pitcher_name, pitch_type = render_pitcher_selection()
    
    # Step 2: Select game context
    game_info = render_game_selection(pitcher_name)
    
    # Step 3: Upload video
    uploaded_file = render_video_uploader()
    
    if uploaded_file:
        # Save and validate video
        video_path = save_uploaded_file(uploaded_file)
        
        if video_path:
            validation = validate_video(video_path)
            
            if not validation["valid"]:
                st.error(f"Error validating video file: {validation.get('error', 'Unknown error')}")
            else:
                # Show warnings if any
                for warning in validation.get("warnings", []):
                    st.warning(warning)
                
                # Show video preview
                st.video(uploaded_file)
                
                if st.button("Analyze Pitch"):
                    try:
                        with st.spinner('Analyzing pitch mechanics...'):
                            # Extract game info if available
                            game_pk = None
                            pitcher_id = None
                            if game_info:
                                game_pk = game_info.get("game_pk")
                                pitcher_id = game_info.get("pitcher_id")
                            
                            results = analyzer.analyze_pitch(
                                video_path=video_path,
                                pitcher_name=pitcher_name,
                                pitch_type=pitch_type,
                                game_pk=game_pk,
                                pitcher_id=pitcher_id
                            )
                            
                            if results:
                                display_analysis_results(results)
                                
                                # Display game context if available
                                if 'game_context' in results:
                                    st.subheader("Game Context")
                                    st.write(f"Context: {results['game_context']}")
                                
                            else:
                                st.error("Analysis failed. Please try again.")
                                
                        # Cleanup temporary file
                        if video_path and os.path.exists(video_path):
                            os.unlink(video_path)
                            
                    except Exception as e:
                        st.error(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main() 