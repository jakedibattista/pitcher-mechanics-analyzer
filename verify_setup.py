import os
import logging
from google.cloud import storage
from pathlib import Path

def verify_environment():
    print("\nVerifying setup...")
    
    # Check Google Cloud credentials
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    print(f"\n1. Google Cloud Credentials:")
    print(f"   Path: {creds_path}")
    print(f"   Exists: {os.path.exists(creds_path) if creds_path else False}")
    
    # Check GCS bucket
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket('baseball-pitcher-analyzer-videos')
        print("\n2. GCS Bucket:")
        print(f"   Name: baseball-pitcher-analyzer-videos")
        print(f"   Accessible: {bucket.exists()}")
    except Exception as e:
        print(f"   Error accessing bucket: {str(e)}")
    
    # Check directory structure
    test_dir = Path("pitcher_analyzer/tests/data")
    print("\n3. Local directories:")
    print(f"   Test directory exists: {test_dir.exists()}")
    
    # Create necessary directories if they don't exist
    test_dir.mkdir(parents=True, exist_ok=True)
    Path("analysis_output").mkdir(exist_ok=True)
    
    print("\nSetup verification complete!")

if __name__ == "__main__":
    verify_environment() 