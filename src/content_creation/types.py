"""Common types and classes for the content creation system."""

import os
import uuid
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError


@dataclass
class UploadResult:
    """Result of an upload operation."""
    platform: str
    success: bool
    video_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None


class FTPUploader:
    """Handles video uploads to the FTP server (MinIO)."""
    
    def __init__(self):
        self.endpoint_url = os.getenv("FTP_URL")
        self.access_key = os.getenv("FTP_ACCESS_KEY")
        self.secret_key = os.getenv("FTP_SECRET_KEY")
        self.bucket_name = os.getenv("FTP_BUCKET")
        
        if not all([self.endpoint_url, self.access_key, self.secret_key, self.bucket_name]):
            raise ValueError("FTP credentials not configured. Please set FTP_URL, FTP_ACCESS_KEY, FTP_SECRET_KEY, and FTP_BUCKET in your .env file")

        
        # Initialize S3 client with correct MinIO configuration
        from botocore.config import Config
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='us-east-1',
            config=Config(
                signature_version='s3v4',
                s3={
                    'addressing_style': 'path'
                }
            )
        )
    
    def upload_video(self, video_path: Path, client_folder: str = "content-creation") -> Optional[str]:
        """Upload video to FTP server and return public URL."""
        try:
            # Generate unique filename
            file_extension = video_path.suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # S3 key (path in bucket)
            s3_key = f"{client_folder}/{unique_filename}"
            
            # Test connection first
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                print("✅ FTP connection successful")
            except ClientError as e:
                print(f"❌ FTP connection failed: {e}")
                print(f"🔍 DEBUG: Error code: {e.response.get('Error', {}).get('Code', 'Unknown')}")
                return None
            
            # Upload file
            self.s3_client.upload_file(
                str(video_path),
                self.bucket_name,
                s3_key
            )
            
            # Generate public URL
            # For MinIO, we need to use the correct public URL format
            # The FTP server is at http://ftp.syn.gl:9000 but public access might be different
            if self.endpoint_url.startswith("http://ftp.syn.gl:9000"):
                # Use the public domain without port for public access
                public_url = f"https://ftp.syn.gl/{self.bucket_name}/{s3_key}"
            elif self.endpoint_url.startswith("http://"):
                public_domain = self.endpoint_url.replace("http://", "https://")
                public_url = f"{public_domain}/{self.bucket_name}/{s3_key}"
            elif self.endpoint_url.startswith("https://"):
                public_url = f"{self.endpoint_url}/{self.bucket_name}/{s3_key}"
            else:
                public_url = f"https://{self.endpoint_url}/{self.bucket_name}/{s3_key}"
            print(f"✅ Video uploaded to FTP: {public_url}")
            
            return public_url
            
        except ClientError as e:
            print(f"❌ FTP upload failed: {e}")
            return None
        except Exception as e:
            print(f"❌ FTP upload error: {e}")
            return None
