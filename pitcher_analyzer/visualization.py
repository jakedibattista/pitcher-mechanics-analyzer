import cv2
from pathlib import Path
from datetime import datetime
import numpy as np
import os
from .config import Config
import tempfile
import asyncio
import inspect
import logging

__all__ = ['create_analysis_visualization']

logger = logging.getLogger(__name__)

def create_analysis_visualization(video_path, analysis_data):
    """
    Create a visualization of the pitch analysis by adding overlays to the video.
    
    Args:
        video_path (str): Path to the original video
        analysis_data (dict): Analysis results including mechanics score and deviations
        
    Returns:
        str: Path to the analyzed video with overlays
    """
    try:
        # Create a temporary file for the output video
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        output_path = output_file.name
        output_file.close()
        
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Get analysis data
        mechanics_score = analysis_data.get('mechanics_score', 0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Add score overlay
            cv2.putText(
                frame,
                f"Score: {mechanics_score:.1f}%",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            
            out.write(frame)
        
        # Release resources
        cap.release()
        out.release()
        
        logger.info(f"Analysis visualization created at: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        return video_path  # Return original video path if visualization fails

def add_analysis_overlay(frame, analysis, pitch_type):
    """Add analysis information overlay to frame"""
    # Add error checking for missing keys
    if not isinstance(analysis, dict):
        logging.error(f"Expected analysis to be a dict, got {type(analysis)}")
        # Create a default analysis dict to avoid errors
        analysis = {
            'mechanics_score': 0.0,
            'risk_factors': ['Analysis failed'],
            'recommendations': ['Please try again'],
            'deviations': {}  # Add empty deviations dict
        }
    
    # Ensure all required keys exist
    if 'mechanics_score' not in analysis:
        analysis['mechanics_score'] = 0.0
    
    if 'risk_factors' not in analysis:
        analysis['risk_factors'] = ['Analysis incomplete']
    
    if 'recommendations' not in analysis:
        analysis['recommendations'] = ['Please try again']
    
    if 'deviations' not in analysis:
        analysis['deviations'] = {}
    
    # Create a copy for the overlay
    overlay = frame.copy()
    height, width = frame.shape[:2]
    
    # Create semi-transparent background for text
    text_bg = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add mechanics score (top left)
    score_text = f"Mechanics Score: {analysis.get('mechanics_score', 0.0):.1f}%"
    cv2.putText(text_bg, score_text, 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Add deviations (left side)
    y_pos = 70
    if analysis['deviations']:
        for aspect, deviation in analysis['deviations'].items():
            text = f"{aspect}: {deviation:.1f}% deviation"
            cv2.putText(text_bg, text, (10, y_pos), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_pos += 30
    else:
        # Handle case with no deviations
        pass  # Add appropriate visualization for no deviations
    
    # Add recommendations (right side)
    y_pos = 70
    cv2.putText(text_bg, "Recommendations:", (width - 400, y_pos), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    y_pos += 30
    for rec in analysis['recommendations'][:3]:  # Show top 3 recommendations
        cv2.putText(text_bg, f"• {rec[:50]}...", (width - 390, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y_pos += 25
    
    # Add risk factors (bottom)
    if analysis['risk_factors']:
        y_pos = height - 100
        cv2.putText(text_bg, "Risk Factors:", (10, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        y_pos += 30
        for risk in analysis['risk_factors'][:2]:  # Show top 2 risk factors
            cv2.putText(text_bg, f"! {risk[:60]}...", (20, y_pos), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
            y_pos += 25
    
    # Blend the text background with the original frame
    alpha = 0.3  # Transparency for the background
    mask = text_bg.sum(axis=2) > 0
    overlay[mask] = cv2.addWeighted(text_bg[mask], alpha, overlay[mask], 1 - alpha, 0)
    
    return overlay

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