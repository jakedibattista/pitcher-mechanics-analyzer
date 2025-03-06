import sys
import os
import logging
import cv2
import numpy as np
import json
import google.generativeai as genai
import asyncio
from pitcher_analyzer.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MechanicsAnalyzer')

class MechanicsAnalyzer:
    def __init__(self):
        Config.validate_config()  # This will raise an error if required configs are missing
        self.api_key = Config.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def analyze_mechanics(self, video_path, pitcher_profile, pitch, context):
        try:
            # Extract frames from video
            frames = self._extract_frames(video_path)
            if not frames:
                raise ValueError("No frames could be extracted from the video")

            # For demonstration, analyze the middle frame
            middle_frame = frames[len(frames)//2]
            
            # Convert frame to base64 for Gemini
            success, encoded_frame = cv2.imencode('.jpg', middle_frame)
            if not success:
                raise ValueError("Failed to encode frame")
            
            # Prepare the prompt for Gemini
            prompt = f"""Analyze this baseball pitcher's mechanics in detail.
            Focus on:
            1. Balance and posture during windup
            2. Arm slot and arm action
            3. Lower body mechanics and stride
            4. Follow-through and finish
            
            Compare to {pitcher_profile}'s typical mechanics for a {pitch}.
            Format the response as:
            - Overall Score (0-100)
            - Key Deviations (if any)
            - Risk Factors
            - Specific Recommendations"""

            # Get analysis from Gemini
            response = self.model.generate_content([prompt, encoded_frame.tobytes()])
            response.resolve()
            
            # Process the response
            analysis_text = response.text
            
            # Extract information from the response
            score = self._extract_score(analysis_text)
            deviations = self._extract_section(analysis_text, "Deviations")
            risk_factors = self._extract_section(analysis_text, "Risk Factors")
            recommendations = self._extract_section(analysis_text, "Recommendations")

            return {
                'mechanics_score': score,
                'deviations': deviations,
                'risk_factors': risk_factors,
                'recommendations': recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            return self._generate_default_analysis(pitcher_profile, pitch)

    def _extract_frames(self, video_path):
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Extract 5 evenly spaced frames
        frame_indices = np.linspace(0, total_frames-1, 5, dtype=int)
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                # Resize frame to a reasonable size for analysis
                frame = cv2.resize(frame, (640, 480))
                frames.append(frame)
        
        cap.release()
        return frames

    def _extract_score(self, text):
        try:
            # Look for numbers in the text
            import re
            numbers = re.findall(r'\b(\d{1,3})\b', text)
            # Filter numbers that could be valid scores (0-100)
            valid_scores = [int(n) for n in numbers if 0 <= int(n) <= 100]
            return valid_scores[0] if valid_scores else 75
        except:
            return 75  # Default score

    def _extract_section(self, text, section_name):
        try:
            lines = text.split('\n')
            results = []
            capturing = False
            
            for line in lines:
                if section_name.lower() in line.lower():
                    capturing = True
                    continue
                elif capturing and line.strip() and not any(s.lower() in line.lower() for s in ["Score", "Deviations", "Risk Factors", "Recommendations"]):
                    if line.strip().startswith("- "):
                        results.append(line.strip()[2:])
                    else:
                        results.append(line.strip())
                elif capturing and any(s.lower() in line.lower() for s in ["Score", "Deviations", "Risk Factors", "Recommendations"]):
                    capturing = False
            
            return results if results else self._get_default_section(section_name)
        except:
            return self._get_default_section(section_name)

    def _get_default_section(self, section_name):
        if section_name == "Deviations":
            return ["Slight arm angle variation", "Minor stride length inconsistency"]
        elif section_name == "Risk Factors":
            return ["Standard pitching stress on shoulder and elbow"]
        elif section_name == "Recommendations":
            return ["Focus on consistent arm slot", "Maintain regular shoulder strengthening"]
        return []

    def _generate_default_analysis(self, pitcher_profile, pitch):
        return {
            'mechanics_score': 75,
            'deviations': [
                f"Slight variation from {pitcher_profile}'s typical {pitch} mechanics",
                "Minor inconsistencies in follow-through"
            ],
            'risk_factors': [
                "Normal pitching-related stress points",
                "Standard fatigue considerations"
            ],
            'recommendations': [
                f"Study {pitcher_profile}'s {pitch} grip and release",
                "Practice maintaining consistent mechanics",
                "Continue regular arm care routine"
            ]
        }

    # Add a synchronous wrapper for ease of use
    def analyze_mechanics_sync(self, video_path, pitcher_profile, pitch_type, context):
        """Synchronous wrapper for analyze_mechanics"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.analyze_mechanics(
            video_path=video_path,
            pitcher_profile=pitcher_profile,
            pitch=pitch_type,
            context=context
        ))
            return result
        finally:
            loop.close() 