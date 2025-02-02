import logging
from pathlib import Path
import json
from ..video_manager import VideoManager
from ..analyzer import PitcherAnalyzer
import cv2
import numpy as np
from ..config import Config
from datetime import datetime  # Add at the top

class DebugUtility:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path('analysis_output')
        self.output_dir.mkdir(exist_ok=True)
        
    def debug_analysis(self, video_uri):
        """Run analysis with detailed debugging"""
        try:
            # Save input parameters
            with open(self.output_dir / 'input_params.json', 'w') as f:
                json.dump({'video_uri': video_uri}, f, indent=2)
            
            # Initialize components
            analyzer = PitcherAnalyzer()
            
            # Run analysis
            self.logger.info(f"Starting analysis of: {video_uri}")
            metrics, fatigue, comparison = analyzer.analyze_pitch(video_uri)
            
            # Save results
            with open(self.output_dir / 'analysis_results.json', 'w') as f:
                json.dump({
                    'metrics': metrics,
                    'fatigue': fatigue,
                    'comparison': comparison
                }, f, indent=2)
                
            return metrics, fatigue, comparison
            
        except Exception as e:
            self.logger.error(f"Debug analysis failed: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None, None, None

    def debug_pose_detection(self, pose_data, output_dir):
        """Debug utility for pose detection results"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save pose data
        with open(output_dir / 'pose_data.json', 'w') as f:
            json.dump(pose_data, f, indent=2)
        
        # Save debug visualizations
        if pose_data.get('poses'):
            for i, pose in enumerate(pose_data['poses']):
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                # Draw pose landmarks
                for landmark in pose['landmarks']:
                    x = int(landmark['x'] * 640)
                    y = int(landmark['y'] * 480)
                    cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
                cv2.imwrite(str(output_dir / f'pose_{i:03d}.jpg'), frame)

def determine_pitch_type(velocity, pitcher_name='KERSHAW'):
    """Determine pitch type based on velocity and pitcher profile"""
    # Get pitcher's velocity ranges from profile
    profile = Config.PITCHER_PROFILES.get(pitcher_name)
    velocity_ranges = profile['career_stats']['typical_velocity']
    
    # Define velocity windows with some tolerance (+/- 2 mph)
    for pitch_type, vel_range in velocity_ranges.items():
        min_vel, max_vel = map(int, vel_range.split('-'))
        # Add tolerance
        if min_vel - 2 <= velocity <= max_vel + 2:
            return pitch_type
            
    return None  # Unknown pitch type

def create_analysis_visualization(video_path, analysis_text, pitch_type, pitcher_name='KERSHAW', output_path=None):
    """Create visualization with mechanical analysis overlay"""
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = Path(video_path).stem
        output_path = str(Path.cwd() / "analysis_output" / f"{video_name}_analysis_{timestamp}.mp4")
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Overlay dimensions
    overlay_width = int(width * 0.25)
    overlay_height = int(height * 0.20)
    overlay_x = 20
    overlay_y = int(height * 0.75)
    header_height = int(overlay_height * 0.25)
    
    # Font sizes
    TITLE_SIZE = 1.8
    STATUS_SIZE = 1.4
    DATA_SIZE = 1.4

    # Colors (BGR)
    NAVY = (64, 35, 12)
    BLUE = (135, 48, 0)
    WHITE = (255, 255, 255)
    
    def parse_analysis_text(text):
        """Parse analysis text into scores and deviations"""
        result = {
            'power': {'score': 0, 'deviation': 0, 'match': 0},
            'arm': {'score': 0, 'deviation': 0, 'match': 0},
            'balance': {'score': 0, 'deviation': 0, 'match': 0},
            'total_deviation': 0
        }
        
        for line in text.split('\n'):
            if 'Power:' in line:
                result['power']['score'] = int(line.split('/')[0].split(':')[1].strip())
            elif 'Arm:' in line:
                result['arm']['score'] = int(line.split('/')[0].split(':')[1].strip())
            elif 'Balance:' in line:
                result['balance']['score'] = int(line.split('/')[0].split(':')[1].strip())
            elif 'Total deviation' in line:
                result['total_deviation'] = float(line.split(':')[1].strip().replace('%', ''))
                
        return result

    def get_score_color(score, deviation):
        """Get color based on score and deviation from ideal"""
        if score >= 8 and deviation < 10:  # Close to ideal
            return (0, 255, 0)  # Green
        elif score >= 6 and deviation < 20:  # Acceptable
            return (255, 165, 0)  # Orange
        else:
            return (0, 0, 255)  # Red

    analysis = parse_analysis_text(analysis_text)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        overlay = frame.copy()
        
        # Background
        cv2.rectangle(overlay, 
                     (overlay_x, overlay_y), 
                     (overlay_x + overlay_width, overlay_y + overlay_height),
                     NAVY, -1)
        
        # Header
        cv2.rectangle(overlay,
                     (overlay_x, overlay_y),
                     (overlay_x + overlay_width, overlay_y + header_height),
                     BLUE, -1)

        # Header text
        header_text = "PULL THE PITCHER"
        text_size = cv2.getTextSize(header_text, cv2.FONT_HERSHEY_COMPLEX_SMALL, TITLE_SIZE, 2)[0]
        header_x = int(overlay_x + (overlay_width - text_size[0]) // 2)
        header_y = int(overlay_y + (header_height / 2) + text_size[1]/2)
        cv2.putText(overlay, header_text,
                   (header_x, header_y),
                   cv2.FONT_HERSHEY_COMPLEX_SMALL, TITLE_SIZE, WHITE, 1)

        # Content spacing
        line_spacing = (overlay_height - header_height - 30) / 5
        content_x = int(overlay_x + 15)
        y = overlay_y + header_height + line_spacing

        # Pitch type
        status_text = pitch_type.upper()
        desc_width = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, STATUS_SIZE, 2)[0][0]
        desc_x = int(overlay_x + (overlay_width - desc_width) // 2)
        cv2.putText(overlay, status_text,
                   (desc_x, int(y)),
                   cv2.FONT_HERSHEY_SIMPLEX, STATUS_SIZE, WHITE, 1)

        # Categories with deviation indicators
        y += line_spacing
        categories = [
            ("POWER", analysis['power']['score'], analysis['power']['deviation']),
            ("ARM", analysis['arm']['score'], analysis['arm']['deviation']),
            ("BALANCE", analysis['balance']['score'], analysis['balance']['deviation'])
        ]
        
        for cat, value, deviation in categories:
            color = get_score_color(value, deviation)
            display_text = f"{cat}: {value}/10 ({deviation:+.1f}°)"
            cv2.putText(overlay, display_text,
                      (content_x, int(y)),
                      cv2.FONT_HERSHEY_SIMPLEX, DATA_SIZE, color, 1)
            y += line_spacing

        # Add total deviation
        deviation_text = f"Deviation from ideal: {analysis['total_deviation']}%"
        cv2.putText(overlay, deviation_text,
                  (content_x, int(y + line_spacing)),
                  cv2.FONT_HERSHEY_SIMPLEX, DATA_SIZE * 0.8, WHITE, 1)

        # Blend overlay
        frame = cv2.addWeighted(overlay, 0.95, frame, 0.05, 0)
        out.write(frame)
    
    cap.release()
    out.release()
    return output_path 