import os
import google_auth_oauthlib
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import pickle
import glob
from news_video import main as news_video_main
from news_text import get_gemini_response
import tempfile
from logger_config import get_logger

# Set up logger for this module
logger = get_logger(__name__)

logger.info("=== Starting YouTube Upload Process ===")
logger.info("Generating video metadata with Gemini AI")

try:
    TITLE = get_gemini_response('''Give a best cautchy attractive youtube title today's top India national news.''')
    logger.info(f"Generated title: {TITLE}")
    
    DESCRIPTION = get_gemini_response(f'''Give a best cautchy attractive formatted with oneline space youtube description,
    with 50 trending # tags in description like #tag1,... , for {TITLE}. My youtube https://www.youtube.com/@rdrjsethurajan and playlist https://www.youtube.com/watch?v=NnQ4a35KR1A&list=PLhv_6lhldIL52dNu3VGOZCjRwDkjeVST_''')
    logger.info(f"Generated description length: {len(DESCRIPTION)} characters")
    
    # Focused set of relevant tags (staying within YouTube's 500 character limit)
    TAGS = get_gemini_response(f'''Give a best cautchy attractive 25 youtube tags formatted like ["tag1", ...] for {TITLE}.''')
    logger.info(f"Generated tags: {TAGS}")
    
except Exception as e:
    logger.error(f"Error generating metadata: {str(e)}")
    # Fallback metadata
    TITLE = "Today's Top India National News - Latest Updates"
    DESCRIPTION = "Stay updated with the latest national news from India. #India #News #National #Updates"
    TAGS = ["India", "News", "National", "Updates", "Latest"]

# Add playlist modification scope
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"  # This scope allows playlist modifications
]

def authenticate_youtube():
    """Authenticate with YouTube API using cached credentials if available."""
    logger.info("=== Starting YouTube Authentication Process ===")
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    credentials = None
    token_file = 'youtube_token.pickle'

    # Try to load cached credentials first
    if os.path.exists(token_file):
        logger.info("Found cached credentials file")
        try:
            with open(token_file, 'rb') as token:
                credentials = pickle.load(token)
                logger.info("Loaded cached credentials")
                
                # Check if credentials are valid or can be refreshed
                if credentials and credentials.expired and credentials.refresh_token:
                    try:
                        logger.info("Refreshing expired credentials")
                        credentials.refresh(Request())
                        logger.info("Refreshed expired credentials")
                        # Save the refreshed credentials
                        with open(token_file, 'wb') as token:
                            pickle.dump(credentials, token)
                        logger.info("Saved refreshed credentials to cache")
                    except Exception as e:
                        logger.error(f"Could not refresh credentials: {str(e)}")
                        credentials = None
                elif not credentials or not credentials.valid:
                    logger.warning("Cached credentials are invalid")
                    credentials = None
                else:
                    logger.info("Cached credentials are valid")
        except Exception as e:
            logger.error(f"Error loading cached credentials: {str(e)}")
            credentials = None

    # Only get new credentials if we don't have valid ones
    if not credentials or not credentials.valid:
        logger.info("No valid credentials found, starting new authentication")
        try:
            # Load client secrets file
            client_secrets_file = "client.json"
            logger.info(f"Loading client secrets from: {client_secrets_file}")
            
            if not os.path.exists(client_secrets_file):
                logger.error(f"Client secrets file not found: {client_secrets_file}")
                raise FileNotFoundError(f"Client secrets file not found: {client_secrets_file}")
            
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, 
                SCOPES,
                redirect_uri='http://localhost:8080/'
            )
            
            # Force offline access to get refresh token
            flow.oauth2session.auto_refresh_url = flow.client_config['token_uri']
            flow.oauth2session.auto_refresh_kwargs = {
                'client_id': flow.client_config['client_id'],
                'client_secret': flow.client_config['client_secret']
            }
            
            logger.info("Starting OAuth2 authentication flow")
            logger.info("Please follow the browser prompts to sign in.")
            logger.info("Make sure to check 'Keep me signed in' if prompted.")
            
            credentials = flow.run_local_server(
                port=8080,
                prompt='consent',  # Force consent screen to ensure we get refresh token
                authorization_prompt_message='Please authorize the application to access your YouTube account'
            )
            
            # Verify we have a refresh token
            if not credentials.refresh_token:
                logger.error("No refresh token received")
                raise Exception("No refresh token received. Please try again and make sure to grant all requested permissions.")
                
            logger.info("Successfully obtained credentials with refresh token")
            
            # Save the complete credentials
            with open(token_file, 'wb') as token:
                pickle.dump(credentials, token)
            logger.info("Saved credentials to cache")
            
        except Exception as e:
            logger.error(f"Authentication Error: {str(e)}")
            if "redirect_uri_mismatch" in str(e):
                logger.error("Redirect URI mismatch detected")
                logger.info("To fix the redirect URI mismatch:")
                logger.info("1. Go to https://console.cloud.google.com")
                logger.info("2. Select your project")
                logger.info("3. Go to APIs & Services > Credentials")
                logger.info("4. Edit your OAuth 2.0 Client ID")
                logger.info("5. Add 'http://localhost:8080/' to Authorized redirect URIs")
                logger.info("6. Save the changes")
            raise

    try:
        logger.info("Building YouTube service")
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=credentials)
        logger.info("YouTube service built successfully")
        logger.info("=== YouTube Authentication Completed Successfully ===")
        return youtube
    except Exception as e:
        logger.error(f"Error building YouTube service: {str(e)}")
        raise

def upload_video(youtube, TITLE, video_buffer):
    """Upload a video to YouTube with the given title and video buffer."""
    logger.info("=== Starting Video Upload Process ===")
    logger.info(f"Uploading video with title: {TITLE}")
    
    request_body = {
        "snippet": {
            "categoryId": "25",  # News & Politics
            "title": TITLE,  # Use the provided title
            "description": DESCRIPTION,
           "tags": TAGS,
        },
        "status": {
            "privacyStatus": "public",  # or "private"/"unlisted"
            # "selfDeclaredMadeForKids": False,  # Mandatory COPPA compliance
        },
        "accessControl": {
            "embed": {
                "allowed": True  # Allow embedding on external sites
            },
            "comment": {
                "allowed": True  # Allow comments
            },
            "rate": {
                "allowed": True  # Allow ratings (likes/dislikes)
            },
            "syndicate": {
                "allowed": True  # Publish to subscriptions feed
            },
            "notifySubscribers": {
                "allowed": True  # Notify subscribers
            }
        }
    }

    logger.info("Creating temporary file from video buffer")
    # Create a temporary file from the video buffer
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        temp_file.write(video_buffer.read())
        temp_file_path = temp_file.name
        logger.info(f"Temporary file created: {temp_file_path}")

    try:
        logger.info("Initiating YouTube upload request")
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=googleapiclient.http.MediaFileUpload(temp_file_path, chunksize=-1, resumable=True)
        )

        logger.info("Starting upload process")
        response = None 
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress()*100)
                logger.info(f"Upload progress: {progress}%")

        video_id = response['id']
        logger.info(f"Video uploaded successfully with ID: {video_id}")
        
        # Add to playlist
        try:
            logger.info("Adding video to playlist")
            playlist_id = "PLhv_6lhldIL43rj2UDm1xFagg6EpL8kB_"  # Your playlist ID
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()
            logger.info("Video added to playlist successfully!")
            logger.info(f"Playlist URL: https://www.youtube.com/playlist?list={playlist_id}")
        except Exception as e:
            logger.warning(f"Could not add video to playlist: {str(e)}")
    
    finally:
        # Clean up temporary file
        logger.info("Cleaning up temporary file")
        os.unlink(temp_file_path)
        logger.info("=== Video Upload Process Completed Successfully ===")

if __name__ == "__main__":
    try:
        logger.info("=== Starting Complete News Video Upload Workflow ===")
        
        # Get video from news_video.main()
        logger.info("Generating video from news_video.main()...")
        video_buffer = news_video_main()
        
        if not video_buffer:
            logger.error("No video data generated!")
            exit(1)
            
        logger.info("Video generated successfully!")
            
        # Authenticate once for all uploads
        logger.info("Authenticating with YouTube")
        youtube = authenticate_youtube()
        
        # Upload the video
        try:
            logger.info("Processing generated video for upload")
            logger.info(f"Generated title: {TITLE}")
            
            upload_video(youtube, TITLE, video_buffer)
            logger.info("Successfully uploaded generated video")
            
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
                
        logger.info("=== Complete News Video Upload Workflow Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"An error occurred in main workflow: {str(e)}")
        raise
