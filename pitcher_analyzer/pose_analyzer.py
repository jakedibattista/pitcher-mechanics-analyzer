from vertexai.preview.generative_models import GenerativeModel
import vertexai
import logging
import cv2
import base64
from pathlib import Path
from .config import Config
import numpy as np

class PoseAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        vertexai.init(project="baseball-pitcher-analyzer", location="us-central1")
        self.multimodal_model = GenerativeModel("gemini-pro-vision")
        self.config = Config.MECHANICS
        
    def analyze_mechanics(self, video_path, pitch_type, pitcher_name='KERSHAW'):
        """Analyze pitcher's mechanics using Vertex AI"""
        try:
            # Extract frames first
            frames = self.extract_frames(video_path, pitcher_name, pitch_type)
            if not frames:
                raise Exception("No frames available for analysis")
            
            # Validate we have enough frames for proper analysis
            min_required_frames = 4
            if len(frames) < min_required_frames:
                raise Exception(f"Insufficient frames for analysis. Got {len(frames)}, need at least {min_required_frames}")

            # Get pitch-specific prompt
            system_prompt = self._get_pitch_prompt(pitch_type, len(frames), pitcher_name)
            user_prompt = self._get_scoring_prompt()
            
            content = [{
                "parts": [
                    {"text": system_prompt + "\n\n" + user_prompt},
                    *[{"inline_data": {"mime_type": "image/jpeg", "data": frame}} 
                      for frame in frames]
                ],
                "role": "user"
            }]
            
            response = self.multimodal_model.generate_content(content)
            return response.text if response.text else None
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            return None
            
    def extract_frames(self, video_path, pitcher_name='KERSHAW', pitch_type='SLIDER'):
        """Extract frames from video for analysis"""
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception(f"Failed to open video file: {video_path}")
                
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            self.logger.info(f"Video loaded: {total_frames} frames at {fps} FPS")
            
            # Define key points for specific pitches
            if pitch_type == 'CURVEBALL':
                key_points = {
                    'setup': 0.1,          # Initial setup
                    'leg_lift': 0.3,       # Peak leg lift
                    'top': 0.4,            # Top of delivery
                    'arm_slot': 0.5,       # Over-the-top position
                    'release': 0.6,        # Release point
                    'follow_through': 0.7,  # Follow through
                    'finish': 0.8          # Finish position
                }
                frame_indices = [int(total_frames * percentage) for percentage in key_points.values()]
                max_frames = len(key_points)
            else:
                max_frames = 16
                frame_indices = [int(i * total_frames / max_frames) for i in range(max_frames)]
            
            for i, frame_idx in enumerate(frame_indices):
                self.logger.info(f"Attempting to read frame {frame_idx} ({i+1}/{max_frames})")
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    success, buffer = cv2.imencode('.jpg', frame)
                    if success:
                        frames.append(base64.b64encode(buffer).decode('utf-8'))
                        self.logger.info(f"Successfully encoded frame {frame_idx}")

            cap.release()
            
            if not frames:
                raise Exception("No frames were successfully extracted and encoded")
                
            self.logger.info(f"Successfully extracted {len(frames)} frames")
            return frames
            
        except Exception as e:
            self.logger.error(f"Frame extraction failed: {str(e)}")
            if cap is not None:
                cap.release()
            raise

    def _determine_pitch_type(self, velocity, pitcher_name='KERSHAW'):
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

    def calculate_variance(self, frames, landmarks, ideal_mechanics):
        """Calculate mechanical variance with validation"""
        deviations = []
        
        for frame_idx, (frame, frame_landmarks) in enumerate(zip(frames, landmarks)):
            try:
                frame_deviations = {
                    'leg_drive': None,
                    'arm_action': None,
                    'balance': None
                }
                
                # Leg drive analysis
                leg_drive_dev = self._analyze_leg_drive(frame_landmarks, ideal_mechanics['leg_drive'])
                if leg_drive_dev is not None:
                    frame_deviations['leg_drive'] = leg_drive_dev
                
                # Arm action analysis
                arm_dev = self._analyze_arm_action(frame_landmarks, ideal_mechanics['arm_action'])
                if arm_dev is not None:
                    frame_deviations['arm_action'] = arm_dev
                
                # Balance analysis
                balance_dev = self._analyze_balance(frame_landmarks, ideal_mechanics['balance'])
                if balance_dev is not None:
                    frame_deviations['balance'] = balance_dev
                
                # Only include frame if we have all measurements
                if all(v is not None for v in frame_deviations.values()):
                    weighted_deviation = (
                        frame_deviations['leg_drive'] * 0.35 +
                        frame_deviations['arm_action'] * 0.4 +
                        frame_deviations['balance'] * 0.25
                    )
                    deviations.append(weighted_deviation)
                else:
                    self.logger.warning(f"Incomplete measurements for frame {frame_idx}")
                
            except Exception as e:
                self.logger.error(f"Frame {frame_idx} analysis failed: {str(e)}")
                continue
        
        if not deviations:
            self.logger.warning("No valid measurements obtained")
            return None
        
        return np.mean(deviations) * 100  # Convert to percentage
    
    def _analyze_leg_drive(self, landmarks, ideal):
        """Analyze leg drive mechanics"""
        # Calculate push-off angle
        push_angle = self._calculate_push_angle(landmarks)
        angle_dev = abs(push_angle - ideal['push_off_angle']) / 90
        
        # Calculate stride length
        stride_length = self._calculate_stride_length(landmarks)
        stride_dev = abs(stride_length - ideal['stride_length'])
        
        return (angle_dev + stride_dev) / 2
    
    def _analyze_arm_action(self, landmarks, ideal):
        """Analyze arm action mechanics"""
        # Calculate arm slot angle
        arm_slot = self._calculate_arm_slot(landmarks)
        slot_dev = abs(arm_slot - ideal['arm_slot']) / 12  # 12 o'clock positions
        
        # Check elbow height
        elbow_height = self._check_elbow_height(landmarks)
        height_dev = 0 if elbow_height == ideal['elbow_height'] else 0.5
        
        # Measure release point
        release_point = self._calculate_release_height(landmarks)
        release_dev = abs(release_point - ideal['release_point']) / ideal['release_point']
        
        return (slot_dev + height_dev + release_dev) / 3

    def _calculate_push_angle(self, landmarks):
        """Calculate push-off leg angle relative to ground with validation"""
        required_points = [
            self.config['landmarks']['hip'][1],      # Back hip
            self.config['landmarks']['knee'][1],     # Back knee
            self.config['landmarks']['ankle'][1]     # Back ankle
        ]
        
        if not self._validate_landmarks(landmarks, required_points):
            self.logger.warning("Missing required landmarks for push angle calculation")
            return None
        
        try:
            hip = landmarks[required_points[0]]
            knee = landmarks[required_points[1]]
            ankle = landmarks[required_points[2]]
            
            knee_to_hip = np.array([hip.x - knee.x, hip.y - knee.y])
            knee_to_ankle = np.array([ankle.x - knee.x, ankle.y - knee.y])
            
            # Check for zero vectors
            if np.all(knee_to_hip == 0) or np.all(knee_to_ankle == 0):
                self.logger.warning("Invalid joint positions detected")
                return None
            
            dot_product = np.dot(knee_to_hip, knee_to_ankle)
            norms = np.linalg.norm(knee_to_hip) * np.linalg.norm(knee_to_ankle)
            
            if norms == 0:
                self.logger.warning("Zero vector detected in angle calculation")
                return None
            
            angle = np.arccos(np.clip(dot_product/norms, -1.0, 1.0))
            return np.degrees(angle)
            
        except Exception as e:
            self.logger.error(f"Push angle calculation failed: {str(e)}")
            return None

    def _calculate_stride_length(self, landmarks):
        """Calculate stride length as percentage of height"""
        ankle_back = landmarks[self.config['landmarks']['ankle'][1]]   # Back leg
        ankle_front = landmarks[self.config['landmarks']['ankle'][0]]  # Front leg
        hip = landmarks[self.config['landmarks']['hip'][1]]           # Hip point
        
        # Calculate total height (using hip as reference)
        height = abs(hip.y - ankle_back.y) * 2  # Approximate full height
        # Calculate stride distance
        stride = abs(ankle_front.x - ankle_back.x)
        return stride / height

    def _calculate_arm_slot(self, landmarks):
        """Calculate arm slot angle (1-12 o'clock position)"""
        shoulder = landmarks[self.config['landmarks']['shoulder'][1]]  # Right shoulder
        elbow = landmarks[self.config['landmarks']['elbow'][1]]       # Right elbow
        
        # Calculate angle between vertical and upper arm
        angle = np.arctan2(elbow.y - shoulder.y, elbow.x - shoulder.x)
        # Convert to clock position (0° = 12 o'clock, moving clockwise)
        clock_position = (angle * 6/np.pi) % 12 or 12
        return clock_position

    def _check_elbow_height(self, landmarks):
        """Check if throwing elbow is above shoulder line"""
        shoulder = landmarks[self.config['landmarks']['shoulder'][1]]  # Right shoulder
        elbow = landmarks[self.config['landmarks']['elbow'][1]]       # Right elbow
        
        return 'above_shoulder' if elbow.y < shoulder.y else 'below_shoulder'

    def _calculate_release_height(self, landmarks):
        """Calculate release point height relative to ground"""
        wrist = landmarks[self.config['landmarks']['wrist'][1]]    # Right wrist
        ankle = landmarks[self.config['landmarks']['ankle'][1]]    # Right ankle
        
        # Calculate height in feet (approximate using ankle as ground reference)
        pixel_height = abs(ankle.y - wrist.y)
        return (pixel_height / self.frame_height) * 7.0  # Assuming average height ~7 feet

    def _analyze_balance(self, landmarks, ideal):
        """Analyze balance metrics"""
        # Track head position relative to center
        head = landmarks['nose']
        hips_center = self._get_hips_center(landmarks)
        
        # Calculate head deviation from center line
        head_deviation = abs(head.x - hips_center.x) / self.frame_width
        
        # Calculate spine angle
        spine_angle = self._calculate_spine_angle(landmarks)
        spine_dev = abs(spine_angle - ideal['spine_angle']) / 90
        
        # Calculate landing foot angle
        foot_angle = self._calculate_foot_angle(landmarks)
        foot_dev = abs(foot_angle - ideal['landing_foot_angle']) / 45
        
        return (head_deviation + spine_dev + foot_dev) / 3

    def _calculate_spine_angle(self, landmarks):
        """Calculate spine angle relative to vertical"""
        hip_center = self._get_hips_center(landmarks)
        shoulder_center = self._get_shoulder_center(landmarks)
        
        # Calculate angle between spine and vertical
        dx = shoulder_center.x - hip_center.x
        dy = shoulder_center.y - hip_center.y
        angle = np.degrees(np.arctan2(dx, -dy))  # Negative dy because y increases downward
        return abs(angle)

    def _calculate_foot_angle(self, landmarks):
        """Calculate landing foot angle relative to home plate line"""
        ankle_front = landmarks[self.config['landmarks']['ankle'][0]]  # Front ankle
        toe_front = landmarks[self.config['landmarks']['foot_index'][0]]  # Front toe
        
        # Calculate angle relative to horizontal
        dx = toe_front.x - ankle_front.x
        dy = toe_front.y - ankle_front.y
        angle = np.degrees(np.arctan2(dy, dx))
        return angle

    def _get_hips_center(self, landmarks):
        """Calculate center point between hips"""
        left_hip = landmarks[self.config['landmarks']['hip'][0]]
        right_hip = landmarks[self.config['landmarks']['hip'][1]]
        return Point(
            (left_hip.x + right_hip.x) / 2,
            (left_hip.y + right_hip.y) / 2
        )

    def _get_shoulder_center(self, landmarks):
        """Calculate center point between shoulders"""
        left_shoulder = landmarks[self.config['landmarks']['shoulder'][0]]
        right_shoulder = landmarks[self.config['landmarks']['shoulder'][1]]
        return Point(
            (left_shoulder.x + right_shoulder.x) / 2,
            (left_shoulder.y + right_shoulder.y) / 2
        )

    def _get_pitch_prompt(self, pitch_type, frame_count, pitcher_name):
        # Implementation of _get_pitch_prompt method
        pass

    def _get_scoring_prompt(self):
        # Implementation of _get_scoring_prompt method
        pass 

    def _validate_landmarks(self, landmarks, required_points):
        """Validate that required landmarks are visible and reliable"""
        for point in required_points:
            if point not in landmarks:
                return False
            if landmarks[point].visibility < self.config['min_visibility_threshold']:
                return False
        return True

class Point:
    """Simple point class to store x,y coordinates"""
    def __init__(self, x, y):
        self.x = x
        self.y = y 