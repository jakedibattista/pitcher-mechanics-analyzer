import streamlit as st
import os
from google.oauth2 import service_account
from google.cloud import storage
import tempfile
from pitcher_analyzer.analyzer import PitcherAnalyzer
from pitcher_analyzer.config import PITCHER_PROFILES
import cv2
from dotenv import load_dotenv

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

def main():
    load_dotenv()  # Load environment variables
    if not check_credentials():
        return
    
    st.title("⚾ Pitcher Analysis Tool")
    
    try:
        # Initialize Google Cloud credentials
        credentials = initialize_google_credentials()
        project_id = st.secrets["gcp_service_account"]["project_id"]
        st.success(f"Successfully connected to project: {project_id}")
        
        # Create analyzer instance
        analyzer = PitcherAnalyzer(credentials)
        
    except Exception as e:
        st.error(f"Error initializing Google Cloud credentials: {str(e)}")
        st.stop()
    
    # Main interface
    st.subheader("Upload Pitch Video for Analysis")
    
    # Get available pitchers and their pitches
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
            help="Select a pitcher to analyze"
        )
        
        # Show pitcher's available data
        if pitcher_name:
            pitcher_data = available_pitchers[pitcher_name]
            mechanics = pitcher_data["mechanics"]
            st.caption(f"""Available data for {pitcher_name}:
• Arm slot: {mechanics.get('arm_slot', 'N/A')}
• Release height: {mechanics.get('release_height', 'N/A')}
• Stride length: {mechanics.get('stride_length', 'N/A')}""")
    
    with col2:
        # Only show available pitch types for selected pitcher
        available_pitches = available_pitchers[pitcher_name]["pitches"]
        pitch_type = st.selectbox(
            "Select Pitch Type",
            options=available_pitches,
            help=f"Select pitch type to analyze for {pitcher_name}"
        )
    
    # Before the file uploader, add video requirements info
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
        type=['mp4', 'mov'],
        help="Upload a video of a single pitch that meets the requirements above"
    )
    
    if uploaded_file:
        # Add file validation
        try:
            cap = cv2.VideoCapture(save_uploaded_file(uploaded_file))
            duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            cap.release()
            
            if duration < 5 or duration > 15:
                st.warning(f"Video duration ({duration}s) should be between 5-15 seconds")
            if width < 720 or height < 480:
                st.warning(f"Video resolution ({width}x{height}) is below recommended minimum (720x480)")
            if fps < 30:
                st.warning(f"Frame rate ({fps} FPS) is below recommended minimum (30 FPS)")
                
        except Exception as e:
            st.error("Error validating video file. Please ensure it meets the requirements.")
            
        # Show video preview
        st.video(uploaded_file)
        
        if st.button("Analyze Pitch"):
            try:
                # Save uploaded file
                video_path = save_uploaded_file(uploaded_file)
                
                with st.spinner('Analyzing pitch mechanics...'):
                    result = analyzer.analyze_pitch(
                        video_path=video_path,
                        pitcher_name=pitcher_name,
                        pitch_type=pitch_type
                    )
                    
                    if result:
                        st.success("Analysis complete!")
                        
                        # Create three columns for metrics
                        m1, m2, m3 = st.columns(3)
                        
                        with m1:
                            st.metric(
                                "Mechanics Score", 
                                f"{result['mechanics_score']}/10",
                                help="Overall quality of arm mechanics and balance"
                            )
                        
                        with m2:
                            st.metric(
                                "Match to Ideal",
                                f"{result['ideal_match']}/10",
                                help="How closely the mechanics match the ideal form for this pitch type"
                            )
                        
                        with m3:
                            score = result['fatigue_score']
                            color = "normal" if score <= 3 else "off" if score <= 6 else "inverse"
                            st.metric(
                                "Injury Risk", 
                                f"{score}/10",
                                help="Risk of injury based on mechanics (lower is better)",
                                delta="Low Risk" if score <= 3 else "Medium Risk" if score <= 6 else "High Risk",
                                delta_color=color
                            )
                        
                        # Display detailed analysis
                        st.subheader("Detailed Analysis")
                        st.markdown(result['analysis'])
                    else:
                        st.error("Analysis failed. Please try again.")
                        
                # Cleanup temporary file
                if video_path and os.path.exists(video_path):
                    os.unlink(video_path)
                    
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main() 