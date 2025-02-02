from google.cloud import videointelligence
from google.cloud import storage
import vertexai
import logging
import os
from pathlib import Path
from .config import Config
from .video_manager import VideoManager
from .pose_analyzer import PoseAnalyzer

class PitcherAnalyzer:
    def __init__(self):
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize Google Cloud services
        self.project_id = Config.PROJECT_ID
        self.location = Config.LOCATION
        self.bucket_name = "baseball-pitcher-analyzer-videos"
        
        # Ensure credentials are properly set
        credentials_path = Config.CREDENTIALS_PATH
        if not credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
            
        # Initialize VertexAI
        vertexai.init(project=self.project_id, location=self.location)
        self.logger.info("Initialized VertexAI client")
        
        self.video_manager = VideoManager()
        self.pose_analyzer = PoseAnalyzer()
        
    def analyze_pitch(self, video_path: str):
        """Analyze a pitch from video"""
        try:
            self.logger.info(f"Starting analysis of: {video_path}")
            
            # First trim to just the pitch (first 5 seconds)
            trimmed_path = self.video_manager.trim_video(
                video_path, 
                duration=Config.VIDEO_REQUIREMENTS["pitch_segment"]
            )
            
            # Upload if needed and get GCS URI
            video_uri = self.video_manager.get_gcs_uri(trimmed_path)
            
            # Analyze pitcher mechanics
            self.logger.info("Analyzing pitcher mechanics...")
            metrics = self.pose_analyzer.analyze_mechanics(video_uri)
            
            if metrics:
                # Check for fatigue indicators
                fatigue = self.pose_analyzer.detect_fatigue(metrics)
                if fatigue:
                    self.logger.info("Fatigue analysis:")
                    for concern in fatigue['primary_concerns']:
                        self.logger.info(f"- {concern}")
                
                # Compare to ideal form
                comparison = self.pose_analyzer.compare_to_ideal(metrics)
                if comparison:
                    self.logger.info(f"Form score: {comparison['overall_score']:.2f}")
                    for rec in comparison['recommendations']:
                        self.logger.info(f"- {rec}")
                
                # Save analysis for historical tracking
                self.pose_analyzer.save_analysis(metrics, video_path)
                
                # Create visualization
                output_path = self.pose_analyzer.visualize_analysis(
                    video_path=trimmed_path, 
                    metrics=metrics,
                    poses=metrics.get('poses', [])  # Pass the poses if available
                )
                
                if output_path:
                    self.logger.info(f"Analysis video saved to: {output_path}")
                
                return metrics, fatigue, comparison
                
            else:
                self.logger.error("Analysis failed to produce metrics")
                return None, None, None
                
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            return None, None, None
            
    def should_pull_pitcher(self, video_path: str, database_path: str = None) -> bool:
        """Determine if pitcher should be pulled based on metrics"""
        try:
            # Get pitch metrics
            metrics = self.analyze_pitch(video_path)
            if not metrics:
                return False
                
            # For now, use simple velocity threshold
            # TODO: Implement more sophisticated analysis using historical data
            velocity = metrics[0].get('velocity', 0)
            if velocity < 85:  # Simple threshold for demonstration
                self.logger.info(f"Velocity ({velocity} MPH) below threshold")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error in pitcher analysis: {str(e)}")
            return False

    def _process_video_response(self, response):
        """Process the raw video intelligence response"""
        try:
            annotations = response.annotation_results[0]
            
            # Initialize metrics dictionary with measurement sources
            pitch_metrics = {
                'metrics': {
                    'velocity': {'value': 90.0, 'source': 'default'},  # Average MLB fastball velocity
                    'spin_rate': {'value': 2200, 'source': 'default'},  # Average MLB spin rate
                    'arm_angle': {'value': 45.0, 'source': 'default'},  # Typical three-quarter arm slot
                    'release_point': {
                        'value': {'height': 70.0, 'horizontal': 40.0},
                        'source': 'default'
                    },
                    'control': {'value': 75, 'source': 'default'},  # Base control score
                    'pitch_duration': {'value': 0.4, 'source': 'default'},  # Typical pitch duration
                    'max_height': {'value': 60.0, 'source': 'default'},  # Typical max height percentage
                },
                'trajectory': [],
                'confidence': {'value': 0.8, 'source': 'default'}
            }
            
            # Process object tracking annotations
            if hasattr(annotations, 'object_tracking_annotations'):
                ball_tracks = [track for track in annotations.object_tracking_annotations 
                              if 'ball' in track.entity.description.lower()]
                
                if ball_tracks:
                    # Process actual measurements from video
                    measured_metrics = self._extract_measured_metrics(ball_tracks[0])
                    
                    # Update metrics with measured values
                    for metric, data in measured_metrics.items():
                        if data['value'] is not None:
                            pitch_metrics['metrics'][metric] = {
                                'value': data['value'],
                                'source': 'measured'
                            }
            
            return pitch_metrics
            
        except Exception as e:
            self.logger.error(f"Error processing video response: {str(e)}")
            return self._get_default_metrics()

    def _process_ball_tracking(self, ball_track):
        """Process ball tracking data"""
        try:
            frames = []
            for frame in ball_track.frames:
                # Handle timestamp conversion
                time_offset = frame.time_offset
                if hasattr(time_offset, 'total_seconds'):
                    frame_time = time_offset.total_seconds()
                else:
                    frame_time = time_offset.seconds + (time_offset.nanos / 1e9)
                
                box = frame.normalized_bounding_box
                frames.append({
                    'timestamp': frame_time,
                    'position': {
                        'x': box.left,
                        'y': box.top,
                        'width': box.width,
                        'height': box.height
                    },
                    'confidence': frame.confidence
                })
            
            return {'frames': frames}
            
        except Exception as e:
            self.logger.error(f"Error processing ball tracking: {str(e)}")
            return {'frames': []}

    def print_pitch_summary(self, metrics):
        """Print a human-readable summary of pitch metrics"""
        print("\nPitch Analysis Summary")
        print("=====================")
        
        for metric, data in metrics['metrics'].items():
            if metric == 'release_point':
                print(f"\nRelease Point ({data['source']}):")
                print(f"  Height: {data['value']['height']}% from ground")
                print(f"  Position: {data['value']['horizontal']}% from left")
            else:
                value = data['value']
                source = data['source']
                if value is not None:
                    print(f"{metric.replace('_', ' ').title()}: {value} ({source})")
        
        print(f"\nAnalyzed at: {metrics['analysis_timestamp']}")
        print("\nNote: 'measured' values are calculated from video analysis")
        print("      'default' values are MLB averages used when measurement isn't possible")

    def calculate_fatigue_score(self, current_metrics, historical_metrics=None):
        """
        Calculate pitcher fatigue score (1-10, where 1 is completely fresh and 10 is extremely fatigued)
        """
        try:
            # Start with base score
            base_score = 1
            
            # Track fatigue factors
            fatigue_factors = {
                'velocity_drop': 0,
                'control_loss': 0,
                'release_point_variance': 0,
                'delivery_slowdown': 0
            }
            
            # 1. Velocity Drop Analysis (up to +3 points)
            if historical_metrics and len(historical_metrics) > 0:
                initial_velocity = historical_metrics[0].get('velocity', 0)
                current_velocity = current_metrics.get('velocity', 0)
                
                if initial_velocity and current_velocity:
                    velocity_drop = initial_velocity - current_velocity
                    if velocity_drop > 3:
                        fatigue_factors['velocity_drop'] = 3
                    elif velocity_drop > 2:
                        fatigue_factors['velocity_drop'] = 2
                    elif velocity_drop > 1:
                        fatigue_factors['velocity_drop'] = 1

            # 2. Control Analysis (up to +3 points)
            control = current_metrics.get('control', 0)
            if control:
                if control < 60:
                    fatigue_factors['control_loss'] = 3
                elif control < 75:
                    fatigue_factors['control_loss'] = 2
                elif control < 85:
                    fatigue_factors['control_loss'] = 1

            # 3. Release Point Consistency (up to +2 points)
            if historical_metrics and len(historical_metrics) > 0:
                release_points = [m.get('release_point', {}) for m in historical_metrics]
                current_release = current_metrics.get('release_point', {})
                
                if current_release and release_points:
                    height_variance = self._calculate_release_variance(
                        [r.get('height', 0) for r in release_points if r],
                        current_release.get('height', 0)
                    )
                    
                    if height_variance > 5:
                        fatigue_factors['release_point_variance'] = 2
                    elif height_variance > 3:
                        fatigue_factors['release_point_variance'] = 1

            # 4. Pitch Duration Analysis (up to +2 points)
            if current_metrics.get('pitch_duration'):
                if current_metrics['pitch_duration'] > 0.5:
                    fatigue_factors['delivery_slowdown'] = 2
                elif current_metrics['pitch_duration'] > 0.4:
                    fatigue_factors['delivery_slowdown'] = 1

            # Calculate final score (1-10 scale)
            fatigue_score = base_score + sum(fatigue_factors.values())
            fatigue_score = min(10, max(1, fatigue_score))  # Ensure score is between 1 and 10

            return {
                'score': fatigue_score,
                'factors': fatigue_factors,
                'recommendation': self._get_recommendation(fatigue_score),
                'details': self._get_fatigue_details(fatigue_factors)
            }

        except Exception as e:
            self.logger.error(f"Error calculating fatigue score: {str(e)}")
            return {
                'score': None,
                'factors': {},
                'recommendation': "ERROR - Unable to calculate fatigue score",
                'details': f"Error: {str(e)}"
            }

    def _get_recommendation(self, score):
        """Get recommendation based on fatigue score"""
        if score >= 8:
            return "IMMEDIATE ACTION REQUIRED - Remove pitcher immediately"
        elif score >= 6:
            return "WARNING - Consider removing pitcher"
        elif score >= 4:
            return "CAUTION - Monitor closely"
        else:
            return "OK - Pitcher showing normal performance"

    def _get_fatigue_details(self, factors):
        """Generate detailed explanation of fatigue factors"""
        details = []
        if factors['velocity_drop']:
            details.append(f"Velocity drop contributing {factors['velocity_drop']} points to fatigue")
        if factors['control_loss']:
            details.append(f"Control issues contributing {factors['control_loss']} points to fatigue")
        if factors['release_point_variance']:
            details.append(f"Release point variance contributing {factors['release_point_variance']} points to fatigue")
        if factors['delivery_slowdown']:
            details.append(f"Slower delivery contributing {factors['delivery_slowdown']} points to fatigue")
        return details

    def _calculate_release_variance(self, historical_heights, current_height):
        """Calculate variance in release point heights"""
        if not historical_heights:
            return 0
        avg_height = sum(historical_heights) / len(historical_heights)
        return abs(current_height - avg_height)

    def print_fatigue_analysis(self, fatigue_analysis):
        """Print a human-readable fatigue analysis"""
        print("\nPitcher Fatigue Analysis")
        print("=======================")
        
        if fatigue_analysis['score'] is not None:
            print(f"Fatigue Score: {fatigue_analysis['score']}/10")
            
            # Print contributing factors
            if fatigue_analysis['factors']:
                print("\nContributing Factors:")
                for factor, value in fatigue_analysis['factors'].items():
                    if value > 0:
                        print(f"- {factor.replace('_', ' ').title()}: +{value} points")
            
            # Print detailed explanations
            if fatigue_analysis['details']:
                print("\nDetailed Analysis:")
                for detail in fatigue_analysis['details']:
                    print(f"- {detail}")
            
            # Print recommendation
            print(f"\nRecommendation: {fatigue_analysis['recommendation']}")
        else:
            print("Error: Unable to calculate fatigue score")

def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Uploads a file to Google Cloud Storage.
    
    Args:
        bucket_name (str): Your GCS bucket name
        source_file_path (str): Path to your local video file
        destination_blob_name (str): Name to give the file in GCS
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)
    print(f"File {source_file_path} uploaded to gs://{bucket_name}/{destination_blob_name}")

def check_and_create_bucket(project_id, bucket_name, location="us-central1"):
    """
    Checks if a bucket exists and creates it if it doesn't.
    
    Args:
        project_id (str): Your Google Cloud project ID
        bucket_name (str): Name for your bucket
        location (str): Location for the bucket
    """
    storage_client = storage.Client()
    
    # Check if bucket exists
    bucket = storage_client.lookup_bucket(bucket_name)
    
    if bucket is None:
        print(f"Bucket {bucket_name} does not exist. Creating...")
        bucket = storage_client.create_bucket(bucket_name, location=location)
        print(f"Bucket {bucket_name} created in {location}")
    else:
        print(f"Bucket {bucket_name} already exists")
    
    return bucket

# List all existing buckets
def list_buckets(project_id):
    """Lists all buckets in the project."""
    storage_client = storage.Client(project_id)
    buckets = storage_client.list_buckets()
    
    print("Existing buckets:")
    for bucket in buckets:
        print(f"- {bucket.name}")

# Example usage:
# upload_to_gcs(
#     "your-bucket-name",
#     "path/to/your/local/video.mp4",
#     "pitcher_videos/video.mp4"
# )

# Your project ID
project_id = "baseball-pitcher-analyzer"

# First, let's see what buckets you already have
list_buckets(project_id)

# Let's create a bucket if needed (bucket names must be globally unique)
bucket_name = "baseball-pitcher-analyzer-videos"
bucket = check_and_create_bucket(project_id, bucket_name)
