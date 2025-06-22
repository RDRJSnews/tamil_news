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
from datetime import datetime
import ast
import argparse
import time

# Add playlist modification scope
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"  # This scope allows playlist modifications
]

PLAYLIST_ID = "PLhv_6lhldIL52dNu3VGOZCjRwDkjeVST_"

def log_print(level, message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}")

log_print("INFO", "=== Starting YouTube Upload Process ===")
log_print("INFO", "Generating video metadata with Gemini AI")

# Simple in-memory cache for Gemini API responses
_gemini_cache = {}
def get_gemini_response_cached(prompt):
    if prompt in _gemini_cache:
        log_print("INFO", "Using cached Gemini API response.")
        return _gemini_cache[prompt]
    result = get_gemini_response(prompt)
    _gemini_cache[prompt] = result
    return result

def generate_title_description_tags(lang_code, news_text=None):
    try:
        lang_list = ['ta', 'en-in', 'hi']
        if lang_code == 0:
            language = 'Tamil'
        elif lang_code == 1:
            language = 'English'
        elif lang_code == 2:
            language = 'Hindi'
        else:
            raise ValueError(f"Invalid language code: {lang_code}. Valid range: 0-{len(lang_list)-1}")

        TITLE = get_gemini_response_cached(f'''Give one best cautchy attractive youtube title on today's top India national news in {language}. Give only one title content no extra text. Include emojies.''')
        log_print("INFO", f"Generated title: {TITLE}")
        
        DESCRIPTION = get_gemini_response_cached(f'''Give a best cautchy attractive formatted with oneline space youtube description,
    with 50 trending # tags in description like #tag1,... , for {TITLE}. In the description include the exact news text = {news_text}. Use my channel link https://www.youtube.com/@rdrjsethurajan and the playlist link https://www.youtube.com/playlist?list={PLAYLIST_ID}''')
        log_print("INFO", f"Generated description length: {len(DESCRIPTION)} characters")
        log_print("INFO", f"Generated description: {DESCRIPTION}")
        
        # Focused set of relevant tags (staying within YouTube's 500 character limit)
        TAGS = get_gemini_response_cached(f'''Give a best trending viral youtube tags only in English, formatted like ["tag1", "tag2", ...] for {TITLE}.
    Give only tags content no extra text. Note that the sum of all tag length that is len(tag1)+len(tag2)+...etc. should be less than 500''')
        log_print("INFO", f"Generated tags: {TAGS}")
        
    except Exception as e:
        log_print("ERROR", f"Error generating metadata: {str(e)}")
        # Fallback metadata
        TITLE = "Today's Top India National News - Latest Updates"
        DESCRIPTION = "Stay updated with the latest national news from India. #India #News #National #Updates"
        TAGS = ["India", "News", "National", "Updates", "Latest"]

    def get_tags_within_limit(strings_list, max_chars=499):
        sublist = []
        current_count = 0
        for s in strings_list:
            s = s.strip()
            if not s or len(s) > 30:  # allow longer tags if needed
                continue  # skip empty or too-long tags
            if current_count + len(s) <= max_chars:
                sublist.append(s)
                current_count += len(s)
            else:
                break
        return sublist  # return as a real list

    # Safely convert to list if TAGS is a string
    if isinstance(TAGS, str):
        TAGS = ast.literal_eval(TAGS)
    # Focused set of relevant tags (staying within YouTube's 500 character limit)
    TAGS = get_tags_within_limit(TAGS, 499)
    # Ensure TAGS is a list
    if not isinstance(TAGS, list):
        TAGS = list(TAGS)
    print("INFO", f"Generated tags within limit: {TAGS}")
    print("INFO", f"Type of TAGS: {type(TAGS)}")

    return TITLE, DESCRIPTION, TAGS

def authenticate_youtube():
    """Authenticate with YouTube API using cached credentials if available."""
    log_print("INFO", "=== Starting YouTube Authentication Process ===")
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    credentials = None
    token_file = 'youtube_token.pickle'

    # Try to load cached credentials first
    if os.path.exists(token_file):
        log_print("INFO", "Found cached credentials file")
        try:
            with open(token_file, 'rb') as token:
                credentials = pickle.load(token)
                log_print("INFO", "Loaded cached credentials")
                
                # Check if credentials are valid or can be refreshed
                if credentials and credentials.expired and credentials.refresh_token:
                    try:
                        log_print("INFO", "Refreshing expired credentials")
                        credentials.refresh(Request())
                        log_print("INFO", "Refreshed expired credentials")
                        # Save the refreshed credentials
                        with open(token_file, 'wb') as token:
                            pickle.dump(credentials, token)
                        log_print("INFO", "Saved refreshed credentials to cache")
                    except Exception as e:
                        log_print("ERROR", f"Could not refresh credentials: {str(e)}")
                        credentials = None
                elif not credentials or not credentials.valid:
                    log_print("WARNING", "Cached credentials are invalid")
                    credentials = None
                else:
                    log_print("INFO", "Cached credentials are valid")
        except Exception as e:
            log_print("ERROR", f"Error loading cached credentials: {str(e)}")
            credentials = None

    # Only get new credentials if we don't have valid ones
    if not credentials or not credentials.valid:
        log_print("INFO", "No valid credentials found, starting new authentication")
        try:
            # Load client secrets file
            client_secrets_file = "client.json"
            log_print("INFO", f"Loading client secrets from: {client_secrets_file}")
            
            if not os.path.exists(client_secrets_file):
                log_print("ERROR", f"Client secrets file not found: {client_secrets_file}")
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
            
            log_print("INFO", "Starting OAuth2 authentication flow")
            log_print("INFO", "Please follow the browser prompts to sign in.")
            log_print("INFO", "Make sure to check 'Keep me signed in' if prompted.")
            
            credentials = flow.run_local_server(
                port=8080,
                prompt='consent',  # Force consent screen to ensure we get refresh token
                authorization_prompt_message='Please authorize the application to access your YouTube account'
            )
            
            # Verify we have a refresh token
            if not credentials.refresh_token:
                log_print("ERROR", "No refresh token received")
                raise Exception("No refresh token received. Please try again and make sure to grant all requested permissions.")
                
            log_print("INFO", "Successfully obtained credentials with refresh token")
            
            # Save the complete credentials
            with open(token_file, 'wb') as token:
                pickle.dump(credentials, token)
            log_print("INFO", "Saved credentials to cache")
            
        except Exception as e:
            log_print("ERROR", f"Authentication Error: {str(e)}")
            if "redirect_uri_mismatch" in str(e):
                log_print("ERROR", "Redirect URI mismatch detected")
                log_print("INFO", "To fix the redirect URI mismatch:")
                log_print("INFO", "1. Go to https://console.cloud.google.com")
                log_print("INFO", "2. Select your project")
                log_print("INFO", "3. Go to APIs & Services > Credentials")
                log_print("INFO", "4. Edit your OAuth 2.0 Client ID")
                log_print("INFO", "5. Add 'http://localhost:8080/' to Authorized redirect URIs")
                log_print("INFO", "6. Save the changes")
            raise

    try:
        log_print("INFO", "Building YouTube service")
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=credentials)
        log_print("INFO", "YouTube service built successfully")
        log_print("INFO", "=== YouTube Authentication Completed Successfully ===")
        return youtube
    except Exception as e:
        log_print("ERROR", f"Error building YouTube service: {str(e)}")
        raise

def upload_video(youtube, TITLE, DESCRIPTION, TAGS, PLAYLIST_ID, video_buffer):
    """Upload a video to YouTube with the given title and video buffer."""
    log_print("INFO", "=== Starting Video Upload Process ===")
    log_print("INFO", f"Uploading video with title: {TITLE}")
    
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
            "autoCaption": True  # Enable auto captions by default
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

    log_print("INFO", "Creating temporary file from video buffer")
    # Create a temporary file from the video buffer
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        temp_file.write(video_buffer.read())
        temp_file_path = temp_file.name
        log_print("INFO", f"Temporary file created: {temp_file_path}")

    try:
        log_print("INFO", "Initiating YouTube upload request")
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=googleapiclient.http.MediaFileUpload(temp_file_path, chunksize=-1, resumable=True)
        )

        log_print("INFO", "Starting upload process")
        response = None 
        last_progress = 0
        start_time = time.time()
        retry_count = 0
        max_retries = 5
        backoff = 5  # seconds
        
        from googleapiclient.errors import HttpError
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress()*100)
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    # Log progress every 10% or every 30 seconds
                    if progress > last_progress + 9 or elapsed_time > 30:
                        log_print("INFO", f"Upload progress: {progress}% (elapsed: {elapsed_time:.1f}s)")
                        last_progress = progress
                        start_time = current_time  # Reset timer
                    # Check for timeout (15 minutes)
                    if elapsed_time > 900:  # 15 minutes
                        log_print("ERROR", "Upload timeout after 15 minutes")
                        raise Exception("Upload timeout - taking too long")
            except HttpError as e:
                if e.resp.status == 403 and 'quotaExceeded' in str(e):
                    log_print("ERROR", "Quota exceeded. Stopping further retries.")
                    raise
                retry_count += 1
                if retry_count > max_retries:
                    log_print("ERROR", f"Max retries ({max_retries}) reached. Giving up.")
                    raise
                log_print("ERROR", f"Upload error: {str(e)}. Retrying in {backoff} seconds (attempt {retry_count}/{max_retries})...")
                time.sleep(backoff)
                backoff = min(backoff * 2, 300)  # Exponential backoff, max 5 min
                continue
            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    log_print("ERROR", f"Max retries ({max_retries}) reached. Giving up.")
                    raise
                log_print("ERROR", f"Upload error: {str(e)}. Retrying in {backoff} seconds (attempt {retry_count}/{max_retries})...")
                time.sleep(backoff)
                backoff = min(backoff * 2, 300)
                continue

        video_id = response['id']
        log_print("INFO", f"Video uploaded successfully with ID: {video_id}")
        
        # Add to playlist
        try:
            log_print("INFO", "Adding video to playlist")
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": PLAYLIST_ID,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()
            log_print("INFO", "Video added to playlist successfully!")
            log_print("INFO", f"Playlist URL: https://www.youtube.com/playlist?list={PLAYLIST_ID}")
        except Exception as e:
            log_print("WARNING", f"Could not add video to playlist: {str(e)}")
    
    finally:
        # Clean up temporary file
        log_print("INFO", "Cleaning up temporary file")
        os.unlink(temp_file_path)
        log_print("INFO", "=== Video Upload Process Completed Successfully ===")

if __name__ == "__main__":
    try:
        log_print("INFO", "=== Starting Complete News Video Upload Workflow ===")

        parser = argparse.ArgumentParser(description="Upload generated news video to YouTube.")
        parser.add_argument('--lang', type=str, default='ta', choices=['ta', 'en-in', 'hi'], help='Language code: ta for Tamil, en-in for English, hi for Hindi')
        args = parser.parse_args()
        lang_map = {'ta': 0, 'en-in': 1, 'hi': 2}
        lang_code = lang_map.get(args.lang, 0)

        # Determine the video file name based on language
        video_file_map = {
            'ta': 'output_video.mp4',
            'en-in': 'output_video_1.mp4',
            'hi': 'output_video_2.mp4'
        }
        video_path = video_file_map.get(args.lang, 'output_video.mp4')

        # Determine the news text file name based on language
        text_file_map = {
            'ta': 'news_text_ta_output.txt',
            'en-in': 'news_text_en_output.txt',
            'hi': 'news_text_hi_output.txt'
        }
        text_path = text_file_map.get(args.lang, 'news_text_output.txt')

        # Read news text if available
        news_text = None
        if os.path.exists(text_path):
            try:
                with open(text_path, 'r', encoding='utf-8') as f:
                    news_text = f.read()
                log_print("INFO", f"News text loaded from {text_path}")
            except Exception as e:
                log_print("WARNING", f"Could not read news text from {text_path}: {str(e)}")
        else:
            log_print("WARNING", f"News text file {text_path} not found, will generate metadata without context")

        TITLE, DESCRIPTION, TAGS = generate_title_description_tags(lang_code, news_text)

        if not os.path.exists(video_path):
            log_print("ERROR", f"Video file {video_path} does not exist!")
            exit(1)

        with open(video_path, "rb") as f:
            import io
            video_buffer = io.BytesIO(f.read())

        log_print("INFO", "Video file loaded successfully!")

        # Authenticate once for all uploads
        log_print("INFO", "Authenticating with YouTube")
        youtube = authenticate_youtube()

        # Upload the video
        try:
            log_print("INFO", "Processing video for upload")
            log_print("INFO", f"Generated title: {TITLE}")
            upload_video(youtube, TITLE, DESCRIPTION, TAGS, PLAYLIST_ID, video_buffer)
            log_print("INFO", "Successfully uploaded generated video")
        except Exception as e:
            log_print("ERROR", f"Error uploading video: {str(e)}")

        log_print("INFO", "=== Complete News Video Upload Workflow Completed Successfully ===")

    except Exception as e:
        log_print("ERROR", f"An error occurred in main workflow: {str(e)}")
        raise

