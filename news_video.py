from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from news_audio import main as news_audio_main
import librosa
import soundfile as sf
import math
import io
import tempfile
import os
from logger_config import get_logger

# Set up logger for this module
logger = get_logger(__name__)

def change_audio_speed(input_buffer, speed_factor=1.0):
    """
    Change the playback speed of an audio buffer using librosa and return the audio data.
    """
    logger.info("=== Starting Audio Speed Change Process ===")
    logger.info(f"Speed factor: {speed_factor}x")
    
    try:
        logger.info("Creating temporary audio file for processing")
        # Create a temporary file from the audio buffer
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(input_buffer.read())
            temp_file_path = temp_file.name
        
        try:
            logger.info("Loading audio file with librosa")
            # Load the audio file
            y, sr = librosa.load(temp_file_path, sr=None)
            logger.info(f"Audio loaded successfully. Duration: {len(y)/sr:.2f}s, Sample rate: {sr}Hz")
            
            # Use librosa's time_stretch with the correct parameter name
            # In newer versions of librosa, the parameter is 'rate' not 'rate'
            try:
                logger.info("Attempting to stretch audio using librosa.effects.time_stretch")
                # Try the newer librosa version approach
                y_stretched = librosa.effects.time_stretch(y, rate=speed_factor)
                logger.info("Audio stretching completed using primary method")
            except TypeError:
                logger.warning("Primary stretching method failed, trying fallback")
                # Fallback for older versions or different parameter names
                try:
                    y_stretched = librosa.effects.time_stretch(y, rate=speed_factor)
                    logger.info("Audio stretching completed using fallback method 1")
                except:
                    logger.warning("Fallback method 1 failed, using simple resampling approach")
                    # If all else fails, use a simple resampling approach
                    print("Using fallback method for audio speed change")
                    new_length = int(len(y) / speed_factor)
                    y_stretched = librosa.util.fix_length(y, size=new_length)
                    logger.info("Audio stretching completed using simple resampling")
            
            # Save to bytes buffer instead of file
            logger.info("Converting stretched audio to buffer")
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, y_stretched, sr, format='WAV')
            audio_buffer.seek(0)
            
            buffer_size = len(audio_buffer.getvalue())
            logger.info(f"Audio buffer created. Size: {buffer_size} bytes")
            logger.info(f"Original duration: {len(y)/sr:.2f}s, New duration: {len(y_stretched)/sr:.2f}s")
            logger.info("=== Audio Speed Change Completed Successfully ===")
            return audio_buffer
            
        finally:
            # Clean up temporary file
            logger.info("Cleaning up temporary audio file")
            os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error in audio speed change: {str(e)}")
        raise

def repeat_video_to_match_audio(video_path, audio_buffer):
    """Repeat video to match audio duration and combine them."""
    logger.info("=== Starting Video-Audio Combination Process ===")
    logger.info(f"Video path: {video_path}")
    
    try:
        logger.info("Loading video file")
        # Load the video file
        video = VideoFileClip(video_path)
        logger.info(f"Video loaded successfully. Duration: {video.duration:.2f}s, FPS: {video.fps}")
        
        logger.info("Creating temporary audio file for MoviePy")
        # Create a temporary file from the audio buffer for MoviePy
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio_file:
            temp_audio_file.write(audio_buffer.read())
            temp_audio_path = temp_audio_file.name
        
        try:
            logger.info("Loading audio file with MoviePy")
            audio = AudioFileClip(temp_audio_path)  # MoviePy still needs FFmpeg here, but only for reading
            logger.info(f"Audio loaded successfully. Duration: {audio.duration:.2f}s")
            
            # Get durations
            video_duration = video.duration
            audio_duration = audio.duration
            
            logger.info(f"Video duration: {video_duration:.2f}s")
            logger.info(f"Audio duration: {audio_duration:.2f}s")
            logger.info(f"Using audio file: {temp_audio_path}")
            
            # Calculate how many times we need to repeat the video
            num_repeats = math.ceil(audio_duration / video_duration)
            logger.info(f"Number of video repeats needed: {num_repeats}")
            
            # Create a list of repeated video clips
            logger.info("Creating repeated video clips")
            repeated_clips = [video] * num_repeats
            
            # Concatenate all the clips
            logger.info("Concatenating video clips")
            final_video = concatenate_videoclips(repeated_clips)
            logger.info(f"Video concatenation completed. Duration: {final_video.duration:.2f}s")
            
            # Set the audio of the final video
            logger.info("Setting audio to final video")
            final_video = final_video.set_audio(audio)
            
            # Trim the video to exactly match the audio duration
            logger.info("Trimming video to match audio duration")
            final_video = final_video.subclip(0, audio_duration)
            
            logger.info(f"Final video duration: {final_video.duration:.2f}s")
            
            # Write to bytes buffer instead of file
            logger.info("Writing final video to buffer")
            video_buffer = io.BytesIO()
            final_video.write_videofile(
                video_buffer,
                codec='libx264', 
                audio_codec='aac',
                fps=video.fps
            )
            video_buffer.seek(0)
            
            buffer_size = len(video_buffer.getvalue())
            logger.info(f"Video buffer created successfully. Size: {buffer_size} bytes")
            
            # Close the clips to free resources
            logger.info("Cleaning up video and audio resources")
            video.close()
            audio.close()
            final_video.close()
            
            logger.info("=== Video-Audio Combination Completed Successfully ===")
            return video_buffer
            
        finally:
            # Clean up temporary audio file
            logger.info("Cleaning up temporary audio file")
            os.unlink(temp_audio_path)
        
    except Exception as e:
        logger.error(f"Error in video-audio combination: {str(e)}")
        raise

def main():
    """Main function to generate news video."""
    logger.info("=== Starting News Video Generation Process ===")
    
    try:
        video_path = "template.mp4"
        logger.info(f"Using template video: {video_path}")
        
        logger.info("Calling news_audio_main to generate audio")
        audio_buffer = news_audio_main(1)
        
        if not audio_buffer:
            logger.error("No audio buffer received from news_audio_main")
            raise Exception("Audio generation failed")
        
        logger.info("Audio buffer received successfully")
        
        speed = 1.25  # 1.25x speed (change this value as needed)
        logger.info(f"Applying speed factor: {speed}x")
        
        logger.info("Processing audio speed change")
        audio_speeded_buffer = change_audio_speed(audio_buffer, speed)
        
        logger.info("Combining video and audio")
        final_video_buffer = repeat_video_to_match_audio(video_path, audio_speeded_buffer)
        
        logger.info("=== News Video Generation Completed Successfully ===")
        return final_video_buffer
        
    except Exception as e:
        logger.error(f"Error in main video generation process: {str(e)}")
        raise
    