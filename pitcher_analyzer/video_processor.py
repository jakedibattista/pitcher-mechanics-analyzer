import cv2
import base64
import logging
from pathlib import Path
import numpy as np
from pitcher_analyzer.config import Config

class VideoProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # For now, let's skip pose detection until we have the model
        # self.net = cv2.dnn.readNetFromTensorflow('pose/graph_opt.pb')
        self.BODY_PARTS = {
            "Nose": 0, "Neck": 1,
            "RShoulder": 2, "RElbow": 3, "RWrist": 4,
            "LShoulder": 5, "LElbow": 6, "LWrist": 7,
            "RHip": 8, "RKnee": 9, "RAnkle": 10,
            "LHip": 11, "LKnee": 12, "LAnkle": 13
        }

    def extract_frames(self, video_path: str, pitch_type: str = None) -> list:
        """Extract key frames from pitch video"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise ValueError("Could not open video file")

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            self.logger.info(f"Video loaded: {total_frames} frames at {fps} FPS")

            # Calculate safe frame range (avoid last 30 frames)
            safe_end_frame = total_frames - 30
            num_frames_needed = 10
            frame_step = safe_end_frame // (num_frames_needed + 1)  # +1 to leave room at start/end
            
            # Extract frames with safe spacing
            encoded_frames = []
            for i in range(num_frames_needed):
                frame_idx = frame_step * (i + 1)  # Skip first frame_step frames
                self.logger.info(f"Reading frame {frame_idx} ({i+1}/{num_frames_needed})")
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    success, encoded = cv2.imencode('.jpg', frame)
                    if success:
                        encoded_frames.append(encoded.tobytes())
                        self.logger.info(f"Encoded frame {frame_idx}")
                    else:
                        raise ValueError(f"Failed to encode frame {frame_idx}")
                else:
                    raise ValueError(f"Failed to read frame {frame_idx}")

            if len(encoded_frames) != num_frames_needed:
                raise ValueError(f"Only got {len(encoded_frames)} frames, needed {num_frames_needed}")
            
            return encoded_frames

        except Exception as e:
            self.logger.error(f"Frame extraction failed: {str(e)}")
            raise
        finally:
            if 'cap' in locals():
                cap.release()

    def _detect_release_frame(self, cap) -> int:
        """
        Detect the frame where the pitch is released
        This is a simplified version - you might want to use more sophisticated detection
        """
        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames to find motion
            sample_rate = 5  # Check every 5th frame
            max_motion = 0
            release_frame = None
            
            prev_frame = None
            for frame_idx in range(0, total_frames, sample_rate):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    break
                    
                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(prev_frame, frame)
                    motion = np.sum(diff)
                    
                    # Update if this has more motion
                    if motion > max_motion:
                        max_motion = motion
                        release_frame = frame_idx
                        
                prev_frame = frame
                
            return release_frame
            
        except Exception as e:
            self.logger.error(f"Release frame detection failed: {str(e)}")
            return None

    def _get_frame_indices(self, total_frames, pitch_type):
        """Determine which frames to extract based on pitch type"""
        if pitch_type == 'CURVEBALL':
            key_points = {
                'setup': 0.1,
                'leg_lift': 0.3,
                'top': 0.4,
                'arm_slot': 0.5,
                'release': 0.6,
                'follow_through': 0.7,
                'finish': 0.8
            }
            return [int(total_frames * percentage) for percentage in key_points.values()]
        else:
            max_frames = 16
            return [int(i * total_frames / max_frames) for i in range(max_frames)]

    def _capture_frames(self, cap, frame_indices):
        """Capture and encode specific frames"""
        frames = []
        landmarks = []
        for i, frame_idx in enumerate(frame_indices):
            self.logger.info(f"Reading frame {frame_idx} ({i+1}/{len(frame_indices)})")
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                # Get pose landmarks using OpenCV
                frame_landmarks = self._detect_pose(frame)
                if frame_landmarks:
                    landmarks.append(frame_landmarks)
                    frames.append(frame)
        return frames, landmarks

    def process_video(self, video_path, pitch_type='CURVEBALL'):
        """Process video and extract frames with pose landmarks"""
        frames = []
        landmarks = []
        
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Get key frames for analysis
        frame_indices = self._get_frame_indices(total_frames, pitch_type)
        
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                # For now, return empty landmarks until we have pose detection working
                frame_landmarks = {}  # temporary
                landmarks.append(frame_landmarks)
                # Encode frame for AI model
                success, buffer = cv2.imencode('.jpg', frame)
                if success:
                    frames.append(base64.b64encode(buffer).decode('utf-8'))
        
        cap.release()
        return frames, landmarks

    def _detect_pose(self, frame):
        """Detect pose landmarks using OpenCV DNN"""
        frame_height, frame_width = frame.shape[:2]
        
        # Prepare input blob
        input_blob = cv2.dnn.blobFromImage(frame, 1.0/255, (368, 368), (0, 0, 0), swapRB=False, crop=False)
        self.net.setInput(input_blob)
        
        # Forward pass
        output = self.net.forward()
        
        # Extract landmarks
        landmarks = {}
        for part_name, part_id in self.BODY_PARTS.items():
            # Get heatmap for this body part
            heatmap = output[0, part_id, :, :]
            
            # Find global maxima
            _, conf, _, point = cv2.minMaxLoc(heatmap)
            
            # Scale to frame size
            x = int((point[0] * frame_width) / output.shape[3])
            y = int((point[1] * frame_height) / output.shape[2])
            
            # Add if confidence is high enough
            if conf > 0.5:
                landmarks[self._convert_part_name(part_name)] = Point(x, y, conf)
        
        return landmarks

    def _convert_part_name(self, opencv_name):
        """Convert OpenCV part names to our format"""
        name_map = {
            "RShoulder": "RIGHT_SHOULDER",
            "LShoulder": "LEFT_SHOULDER",
            "RElbow": "RIGHT_ELBOW",
            "LElbow": "LEFT_ELBOW",
            "RWrist": "RIGHT_WRIST",
            "LWrist": "LEFT_WRIST",
            "RHip": "RIGHT_HIP",
            "LHip": "LEFT_HIP",
            "RKnee": "RIGHT_KNEE",
            "LKnee": "LEFT_KNEE",
            "RAnkle": "RIGHT_ANKLE",
            "LAnkle": "LEFT_ANKLE",
            "Nose": "nose"
        }
        return name_map.get(opencv_name)

class Point:
    def __init__(self, x, y, visibility=1.0):
        self.x = x
        self.y = y
        self.visibility = visibility 