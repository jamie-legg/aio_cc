"""YouTube Shorts uploader using YouTube Data API v3."""

import os
import time
import random
import httplib2
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from ..content_creation.oauth_manager import OAuthCredentials
from ..content_creation.types import UploadResult

# YouTube upload retry configuration
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib2.error.HttpLib2Error)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


@dataclass
class YouTubeUploader:
    """Handles YouTube Shorts uploads with retry logic."""
    
    def upload(self, video_path: Path, metadata: Dict[str, str], creds: OAuthCredentials) -> UploadResult:
        """Upload video to YouTube Shorts with retry logic."""
        try:
            # Create YouTube service with proper credentials
            # We need to reconstruct the full credentials object
            client_id = os.getenv("YOUTUBE_CLIENT_ID")
            client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
            
            if not client_id or not client_secret:
                raise ValueError("YouTube client credentials not found. Please set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET in your .env file")
            
            credentials = Credentials(
                token=creds.access_token,
                refresh_token=creds.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret
            )
            youtube = build('youtube', 'v3', credentials=credentials)
        
            # Prepare video metadata for YouTube Shorts with fallbacks
            title = metadata.get('title', '').strip()
            if not title:
                title = f"Gaming Clip - {video_path.stem}"
                print(f"⚠️  Empty title in metadata, using fallback: {title}")
            
            description = f"{metadata.get('caption', '')}\n\n{metadata.get('hashtags', '')}".strip()
            if not description:
                description = "Check out this epic gaming moment! 🎮"
                print(f"⚠️  Empty description in metadata, using fallback: {description}")
            
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': self._extract_hashtags(metadata.get('hashtags', '')),
                    'categoryId': '20',  # Gaming category
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False,
                }
            }
            
            print(f"🔍 DEBUG: YouTube metadata prepared:")
            print(f"  Title: '{body['snippet']['title']}'")
            print(f"  Description: '{body['snippet']['description']}'")
            print(f"  Tags: {body['snippet']['tags']}")
            
            # Create media upload with resumable upload
            media = MediaFileUpload(
                str(video_path), 
                chunksize=-1,  # Upload entire file in single request
                resumable=True
            )
            
            # Initialize upload request
            insert_request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute resumable upload with retry logic
            response = self._resumable_upload(insert_request)
            
            if response and 'id' in response:
                video_id = response['id']
                video_url = f"https://www.youtube.com/shorts/{video_id}"
                
                print(f"✅ YouTube Short uploaded successfully! Video ID: {video_id}")
                print(f"🔗 Short URL: {video_url}")
                
                return UploadResult(
                    "youtube",
                    True,
                    video_id=video_id,
                    url=video_url
                )
            else:
                return UploadResult("youtube", False, error="No video ID in response")
                
        except HttpError as e:
            return UploadResult("youtube", False, error=f"YouTube API error: {e}")
        except Exception as e:
            return UploadResult("youtube", False, error=str(e))
    
    def _resumable_upload(self, insert_request):
        """Execute resumable upload with exponential backoff retry logic."""
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                print("📤 Uploading video to YouTube...")
                status, response = insert_request.next_chunk()
                
                if status:
                    progress = int(status.progress() * 100)
                    print(f"📊 Upload progress: {progress}%")
                
                if response is not None:
                    if 'id' in response:
                        print(f"✅ Video uploaded successfully! ID: {response['id']}")
                        return response
                    else:
                        print(f"❌ Unexpected response: {response}")
                        return None
                        
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = f"Retriable HTTP error {e.resp.status}: {e.content}"
                else:
                    print(f"❌ Non-retriable HTTP error: {e}")
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = f"Retriable error: {e}"
            
            if error is not None:
                print(f"⚠️ {error}")
                retry += 1
                
                if retry > MAX_RETRIES:
                    print(f"❌ Max retries ({MAX_RETRIES}) exceeded")
                    return None
                
                # Exponential backoff
                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f"⏳ Retrying in {sleep_seconds:.2f} seconds... (attempt {retry}/{MAX_RETRIES})")
                time.sleep(sleep_seconds)
                
                # Reset error for next iteration
                error = None
        
        return response
    
    def get_upload_status(self, creds: OAuthCredentials) -> Dict[str, any]:
        """Get YouTube upload status and channel info."""
        try:
            # Get channel info
            credentials = Credentials(token=creds.access_token)
            youtube = build('youtube', 'v3', credentials=credentials)
            channels = youtube.channels().list(part='snippet', mine=True).execute()
            return {"authenticated": True, "channels": channels.get('items', [])}
            
        except Exception as e:
            return {"authenticated": False, "error": str(e)}
    
    def _extract_hashtags(self, hashtags_str: str) -> List[str]:
        """Extract hashtags from string and return as list."""
        if not hashtags_str:
            return []
        
        # Split by space and filter hashtags
        tags = [tag.strip() for tag in hashtags_str.split() if tag.strip().startswith('#')]
        # Remove # symbol for YouTube tags
        return [tag[1:] for tag in tags if len(tag) > 1]
