import cv2
from pathlib import Path
from datetime import datetime
import numpy as np

__all__ = ['create_analysis_visualization']

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
    
    # Adjust overlay dimensions
    overlay_width = int(width * 0.25)  # Reduce from 0.35 to 0.25
    overlay_height = int(height * 0.45)  # Keep height the same
    overlay_x = 20
    overlay_y = int(height * 0.50)
    header_height = int(overlay_height * 0.20)
    
    # Font sizes
    TITLE_SIZE = 2.2  # Increased from 1.8 to 2.2
    STATUS_SIZE = 1.4  # Keep pitch type size the same
    DATA_SIZE = 1.2   # Keep category size
    EXPLANATION_SIZE = 0.9  # Keep explanation size

    # Colors (BGR) - just using white for all text now
    NAVY = (64, 35, 12)
    BLUE = (135, 48, 0)
    WHITE = (255, 255, 255)
    
    def parse_analysis_text(text):
        """Parse analysis text into explanations and assessment"""
        try:
            result = {
                'fatigue': '',
                'arm': '',
                'balance': '',
                'assessment': 'N/A'
            }
            
            current_category = None
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if 'Signs of Fatigue:' in line:
                    current_category = 'fatigue'
                elif 'Arm:' in line:
                    current_category = 'arm'
                elif 'Balance:' in line:
                    current_category = 'balance'
                elif 'Mechanics Assessment:' in line:
                    result['assessment'] = line.split('Mechanics Assessment:')[1].strip()
                elif line.startswith('-'):
                    if current_category:
                        result[current_category] = line[1:].strip()
            
            return result
            
        except Exception as e:
            print(f"Error parsing analysis text: {str(e)}")
            return {
                'fatigue': '',
                'arm': '',
                'balance': '',
                'assessment': 'N/A'
            }

    def wrap_text(text, max_width, font_face, font_scale):
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            # Get size of current line with test word
            line_text = ' '.join(current_line)
            (line_width, _) = cv2.getTextSize(line_text, font_face, font_scale, 1)[0]
            
            if line_width > max_width:
                # Remove last word and add line to lines
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]  # Start new line with word that didn't fit
                
        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines

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
        header_text = "PITCHER SCORECARD"
        text_size = cv2.getTextSize(header_text, cv2.FONT_HERSHEY_COMPLEX_SMALL, TITLE_SIZE, 2)[0]
        header_x = int(overlay_x + (overlay_width - text_size[0]) // 2)
        header_y = int(overlay_y + (header_height / 2) + text_size[1]/2)
        cv2.putText(overlay, header_text,
                   (header_x, header_y),
                   cv2.FONT_HERSHEY_COMPLEX_SMALL, TITLE_SIZE, WHITE, 1)

        # Content spacing
        line_spacing = (overlay_height - header_height - 30) / 6  # Keep tighter spacing
        content_x = int(overlay_x + 15)
        y = overlay_y + header_height + int(line_spacing * 0.8)

        # Pitch type
        status_text = pitch_type.upper()
        desc_width = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, STATUS_SIZE, 2)[0][0]
        desc_x = int(overlay_x + (overlay_width - desc_width) // 2)
        cv2.putText(overlay, status_text,
                   (desc_x, int(y)),
                   cv2.FONT_HERSHEY_SIMPLEX, STATUS_SIZE, WHITE, 1)

        # Add deviation with more spacing before and after
        y += line_spacing * 0.8  # Increased from 0.6
        deviation_text = f"Deviation from ideal: {analysis['assessment']}"
        dev_width = cv2.getTextSize(deviation_text, cv2.FONT_HERSHEY_SIMPLEX, DATA_SIZE * 0.8, 1)[0][0]
        dev_x = int(overlay_x + (overlay_width - dev_width) // 2)
        cv2.putText(overlay, deviation_text,
                  (dev_x, int(y)),
                  cv2.FONT_HERSHEY_SIMPLEX, DATA_SIZE * 0.8, WHITE, 1)

        # Add more space before categories
        y += line_spacing * 0.8  # Increased from 0.6

        # Categories with scores and explanations
        categories = [
            ("SIGNS OF FATIGUE", analysis['fatigue']),
            ("ARM", analysis['arm']),
            ("BALANCE", analysis['balance'])
        ]
        
        for cat, explanation in categories:
            # Category name only (no score)
            cv2.putText(overlay, cat,
                      (content_x, int(y)),
                      cv2.FONT_HERSHEY_SIMPLEX, DATA_SIZE, WHITE, 1)
            
            # Add explanation with tighter spacing and right margin
            if explanation:
                available_width = overlay_width - content_x - 60
                wrapped_lines = wrap_text(explanation, 
                                       available_width,
                                       cv2.FONT_HERSHEY_SIMPLEX, 
                                       EXPLANATION_SIZE)
                
                explanation_y = y + int(line_spacing * 0.35)
                
                # Add bullet only for first line
                first_line = True
                for line in wrapped_lines:
                    prefix = "- " if first_line else "  "
                    cv2.putText(overlay, f"{prefix}{line}",
                              (content_x + 20, int(explanation_y)),
                              cv2.FONT_HERSHEY_SIMPLEX, EXPLANATION_SIZE, WHITE, 1)
                    explanation_y += int(line_spacing * 0.5)
                    first_line = False
                
                y = explanation_y + int(line_spacing * 0.25)
            else:
                y += line_spacing * 0.8

        # Blend overlay
        frame = cv2.addWeighted(overlay, 0.95, frame, 0.05, 0)
        out.write(frame)
    
    cap.release()
    out.release()
    return output_path

def create_mechanics_overlay(self, frame, landmarks, deviations):
    """Create visual overlay showing mechanical deviations"""
    overlay = frame.copy()
    
    # Draw skeleton connections
    self._draw_pose_skeleton(overlay, landmarks)
    
    # Visualize arm slot
    self._visualize_arm_slot(overlay, landmarks, deviations['arm_slot'])
    
    # Visualize stride length
    self._visualize_stride(overlay, landmarks, deviations['stride_length'])
    
    # Visualize balance metrics
    self._visualize_balance(overlay, landmarks, deviations['balance'])
    
    return overlay

def _visualize_arm_slot(self, overlay, landmarks, deviation):
    """Visualize arm slot with ideal vs actual"""
    shoulder = landmarks[self.config['landmarks']['shoulder'][1]]
    elbow = landmarks[self.config['landmarks']['elbow'][1]]
    
    # Draw actual arm line
    cv2.line(overlay, 
             (int(shoulder.x), int(shoulder.y)),
             (int(elbow.x), int(elbow.y)),
             (0, 255, 0), 2)
    
    # Draw ideal arm slot line
    ideal_angle = np.pi/6  # 1 o'clock position
    ideal_length = np.sqrt((elbow.x - shoulder.x)**2 + (elbow.y - shoulder.y)**2)
    ideal_end = (
        int(shoulder.x + ideal_length * np.cos(ideal_angle)),
        int(shoulder.y + ideal_length * np.sin(ideal_angle))
    )
    cv2.line(overlay,
             (int(shoulder.x), int(shoulder.y)),
             ideal_end,
             (255, 0, 0), 2, cv2.LINE_DASHED)
    
    # Add deviation annotation
    cv2.putText(overlay,
                f"Arm Slot Dev: {deviation:.1f}°",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2)

def _visualize_balance(self, overlay, landmarks, deviation):
    """Visualize balance metrics"""
    head = landmarks['nose']
    hips_center = self._get_hips_center(landmarks)
    
    # Draw vertical center line
    cv2.line(overlay,
             (int(hips_center.x), 0),
             (int(hips_center.x), overlay.shape[0]),
             (0, 255, 255), 1, cv2.LINE_DASHED)
    
    # Draw head position deviation
    cv2.circle(overlay,
              (int(head.x), int(head.y)),
              5,
              (0, 0, 255) if deviation > 0.1 else (0, 255, 0),
              -1)
    
    # Add balance metric
    cv2.putText(overlay,
                f"Balance Dev: {deviation*100:.1f}%",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2)

def create_scorecard(analysis_text):
    """Create scorecard visualization from analysis text"""
    # Parse the mechanics assessment
    variance_line = [line for line in analysis_text.split('\n') if 'Mechanics Assessment:' in line]
    if variance_line:
        assessment = variance_line[0].split('Mechanics Assessment:')[1].strip()
    else:
        assessment = "N/A"
        
    # Create the scorecard image
    img = np.zeros((800, 800, 3), dtype=np.uint8)
    img.fill(20)  # Dark blue background
    
    # Add title
    cv2.putText(img, "PITCHER SCORECARD", (200, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (200, 200, 200), 2)
                
    # Add pitch type
    cv2.putText(img, "SLIDER", (300, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (150, 150, 150), 2)
                
    # Add assessment
    cv2.putText(img, f"Deviation from ideal: {assessment}", (250, 300),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
    
    # Parse and add explanations
    categories = {
        "SIGNS OF FATIGUE": None,
        "ARM": None,
        "BALANCE": None
    }
    
    current_category = None
    for line in analysis_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        for category in categories.keys():
            if category.lower() in line.lower():
                current_category = category
                break
                
        if current_category and line.startswith('-'):
            categories[current_category] = line[1:].strip()
    
    # Add categories and their explanations
    y_pos = 400
    for category, explanation in categories.items():
        cv2.putText(img, category, (100, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (150, 150, 150), 2)
        if explanation:
            cv2.putText(img, f"- {explanation}", (120, y_pos + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)
        y_pos += 100
        
    return img 