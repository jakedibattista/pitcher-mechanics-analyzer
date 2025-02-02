import logging
from pitcher_analyzer.video_manager import VideoManager

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Initialize video manager
    manager = VideoManager()
    
    # List all available videos
    logger.info("\nSearching for videos...")
    
    logger.info("\nLocal videos:")
    for video in manager.list_local_videos():
        logger.info(f"- {video}")
    
    logger.info("\nCloud videos:")
    for video in manager.list_cloud_videos():
        logger.info(f"- gs://{manager.bucket_name}/{video.name}")
    
    # Try to find and upload dodgers video
    video_path, location = manager.find_video("dodgers")
    
    if location == "cloud":
        logger.info(f"\nVideo already in cloud: {video_path}")
    elif location == "local":
        logger.info(f"\nUploading local video: {video_path}")
        cloud_uri = manager.upload_video("dodgers")
        if cloud_uri:
            logger.info(f"Successfully uploaded to: {cloud_uri}")
    else:
        logger.error("\nCould not find dodgers video locally or in cloud")

if __name__ == "__main__":
    main() 