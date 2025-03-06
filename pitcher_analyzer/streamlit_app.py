import streamlit as st
import os
from google.oauth2 import service_account
from google.cloud import storage
import tempfile
from pitcher_analyzer.main import PitcherAnalysis
from pitcher_analyzer.config import Config
import cv2
from dotenv import load_dotenv
from pitcher_analyzer.game_state import GameStateManager
import datetime
from pitcher_analyzer.data.pitcher_profiles import PITCHER_PROFILES
import logging
import asyncio
import traceback
import inspect
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            "Select Pitcher Profile",
            options=Config.PITCHER_PROFILES.keys(),
            index=0
        )
    
    with col2:
        st.markdown("""
        ##### Game Context
        Different situations require different mechanical focuses:
        - **REGULAR SEASON**: Standard mechanical analysis
        - **HIGH PRESSURE**: Focus on mechanical stability
        - **PERFECT GAME**: Emphasis on control and consistency
        - **UNKNOWN**: General analysis without context
        """)
        
        game_context = st.selectbox(
            "Game Context",
            options=["Regular Season", "Playoff Game", "High Leverage", "Low Leverage"],
            index=0
        )

    # Dynamic pitch type options based on selected pitcher
    pitch_type = st.selectbox(
        "Pitch Type",
        options=["Fastball", "Curveball", "Slider", "Changeup"],
        index=0
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
        type=["mp4", "mov"],
        accept_multiple_files=False,
        help="Upload a video of a single pitch (MP4 or MOV format)"
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

def save_uploaded_video(uploaded_file):
    try:
        # Create a temporary file with the correct extension
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            # Write the uploaded file to disk
            tmp_file.write(uploaded_file.getvalue())
            logger.info(f"Video saved to temporary file: {tmp_file.name}")
            return tmp_file.name
    except Exception as e:
        logger.error(f"Error saving uploaded video: {str(e)}")
        return None

def main():
    """Main function to run the Streamlit app"""
    st.set_page_config(
        page_title="Pitcher Mechanics Analyzer",
        page_icon="⚾",
        layout="wide"
    )
    
    st.title("Pitcher Mechanics Analyzer")
    
    # Configuration section
    st.subheader("Analysis Configuration")
    
    # Pitcher Selection
    st.subheader("Pitcher Selection")
    st.write("Choose who you want to compare mechanics against:")
    selected_pitcher = st.selectbox(
        "Select Pitcher Profile",
        options=Config.PITCHER_PROFILES,
        key="pitcher_select"
    )
    
    # Game Context
    st.subheader("Game Context")
    st.write("Different situations require different mechanical focuses:")
    selected_context = st.selectbox(
        "Game Context",
        options=["Regular Season", "High Pressure", "Training"],
        key="context_select"
    )
    
    # Pitch Type
    st.subheader("Pitch Type Selection")
    st.write("Each pitch type has unique mechanical requirements:")
    selected_pitch = st.selectbox(
        "Pitch Type",
        options=["Fastball", "Curveball", "Slider", "Changeup"],
        key="pitch_select"
    )
    
    # Video Upload
    st.subheader("Upload Your Pitch")
    uploaded_file = st.file_uploader(
        "Upload Pitch Video",
        type=["mp4", "mov", "mpeg4"],
        help="Upload a video of the pitch (MP4 or MOV format)"
    )

    # Store the uploaded file path in session state
    if uploaded_file is not None:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            video_path = tmp_file.name
            st.session_state['video_path'] = video_path
    
    # Analysis Button and Results
    if uploaded_file is not None and st.button("Analyze Pitch"):
        try:
            with st.spinner("Analyzing pitch mechanics..."):
                analyzer = PitcherAnalysis()
                result = analyzer.analyze_pitch_sync(
                    video_path=st.session_state['video_path'],
                    pitcher=selected_pitcher,
                    pitch=selected_pitch,
                    context=selected_context
                )

                if isinstance(result, tuple):
                    analyzed_video_path, analysis_data = result
                    
                    # Now show the video after analysis
                    st.subheader("Analysis Video")
                    st.video(st.session_state['video_path'])

                    # Display analysis results
                    st.subheader("Mechanics Analysis")
                    
                    # Display mechanics score
                    st.metric(
                        "Overall Score",
                        f"{analysis_data.get('mechanics_score', 0):.1f}%"
                    )

                    # Display deviations
                    st.subheader("Mechanical Deviations")
                    deviations = analysis_data.get('deviations', [])
                    if deviations:
                        for dev in deviations:
                            st.write(f"• {dev}")
                    else:
                        st.write("No specific deviations identified")

                    # Display risk factors
                    st.subheader("Risk Factors")
                    risk_factors = analysis_data.get('risk_factors', [])
                    for risk in risk_factors:
                        st.write(f"• {risk}")

                    # Display recommendations
                    st.subheader("Recommendations")
                    recommendations = analysis_data.get('recommendations', [])
                    for rec in recommendations:
                        st.write(f"• {rec}")

        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")

    # Tool Information
    st.markdown("---")
    st.markdown("""
    ## How to Use This Tool
    
    This tool uses advanced computer vision to analyze pitching mechanics. Here's how to get started:
    
    1. Select a pitcher profile from the dropdown
    2. Choose the game context and pitch type
    3. Upload a video of the pitch to analyze
    
    **Video Requirements:**
    - Format: MP4 or MOV
    - Duration: 5-15 seconds
    - Camera Angle: Side view
    - Frame Rate: 30fps or higher
    - Resolution: 720p or higher
    """)

if __name__ == "__main__":
    main() 