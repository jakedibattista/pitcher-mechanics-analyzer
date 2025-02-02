import cv2
import numpy as np
from pathlib import Path

def create_test_pitch_video():
    """Create a simple test video simulating a pitch"""
    # Set up video parameters
    width, height = 1280, 720  # HD resolution
    fps = 30
    duration = 5  # seconds
    
    # Create output path
    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(exist_ok=True, parents=True)
    output_path = output_dir / "sample_pitch.mp4"
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    # Create ball simulation
    ball_x = width // 4
    ball_y = height // 2
    ball_radius = 10
    velocity_x = 15
    
    try:
        # Generate frames
        for frame_num in range(fps * duration):
            # Create blank frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Draw pitcher's mound (simple circle)
            cv2.circle(frame, (width//4, height//2), 50, (100, 100, 100), -1)
            
            # Update ball position
            ball_x += velocity_x
            
            # Draw ball
            cv2.circle(frame, (int(ball_x), int(ball_y)), ball_radius, (255, 255, 255), -1)
            
            # Write frame
            out.write(frame)
            
        print(f"Test video created at: {output_path}")
        return str(output_path)
        
    finally:
        out.release()

if __name__ == "__main__":
    create_test_pitch_video() 