"""Utility functions for Google Cloud Storage operations."""
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

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
    logger.info(f"File {source_file_path} uploaded to gs://{bucket_name}/{destination_blob_name}")

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
        logger.info(f"Bucket {bucket_name} does not exist. Creating...")
        bucket = storage_client.create_bucket(bucket_name, location=location)
        logger.info(f"Bucket {bucket_name} created in {location}")
    else:
        logger.info(f"Bucket {bucket_name} already exists")
    
    return bucket

def list_buckets(project_id):
    """Lists all buckets in the project."""
    storage_client = storage.Client(project_id)
    buckets = storage_client.list_buckets()
    
    bucket_names = []
    for bucket in buckets:
        bucket_names.append(bucket.name)
        
    return bucket_names 