# Tamil News Project - Logging System Documentation

## Overview

This document describes the comprehensive logging system implemented across all modules of the Tamil News project. The logging system provides detailed tracking of each step in the news generation and upload workflow.

## Logging Architecture

### Centralized Logger Configuration (`logger_config.py`)

The logging system is centralized through `logger_config.py` which provides:

- **Multiple log levels**: DEBUG, INFO, WARNING, ERROR
- **Multiple outputs**: Console, detailed file logs, error-only logs
- **Daily log rotation**: Logs are organized by date
- **UTF-8 encoding**: Supports Tamil and English text
- **Structured formatting**: Includes timestamps, module names, function names, and line numbers

### Log Files Structure

```
logs/
├── tamil_news_YYYY-MM-DD.log    # Detailed logs for the day
└── errors_YYYY-MM-DD.log        # Error-only logs for the day
```

## Modules with Logging

### 1. News Text Generation (`news_text.py`)

**Logs:**
- Gemini API configuration and setup
- API request/response details
- Text formatting process
- Language selection
- Error handling for API failures

**Key Log Messages:**
```
INFO - === Starting News Text Generation Process ===
INFO - Selected language: en-in
INFO - Setting up Gemini model with optimized parameters
INFO - Initiating Gemini API request
INFO - Received response from Gemini API
INFO - Text formatting completed. Final length: 2048 characters
INFO - === News Text Generation Completed Successfully ===
```

### 2. Audio Generation (`news_audio.py`)

**Logs:**
- Text-to-speech conversion process
- Language code validation
- Audio buffer creation
- gTTS initialization and processing
- Error handling for audio generation

**Key Log Messages:**
```
INFO - === Starting News Audio Generation Process ===
INFO - Language code received: 1
INFO - Selected language: en-in (code: 1)
INFO - === Starting Text-to-Speech Conversion ===
INFO - Audio buffer created successfully. Size: 1024000 bytes
INFO - === Text-to-Speech Conversion Completed Successfully ===
```

### 3. Video Generation (`news_video.py`)

**Logs:**
- Audio speed modification process
- Video file loading and processing
- Video-audio synchronization
- Buffer creation and management
- Resource cleanup

**Key Log Messages:**
```
INFO - === Starting News Video Generation Process ===
INFO - === Starting Audio Speed Change Process ===
INFO - Audio loaded successfully. Duration: 120.50s, Sample rate: 22050Hz
INFO - === Starting Video-Audio Combination Process ===
INFO - Video loaded successfully. Duration: 30.00s, FPS: 30
INFO - Number of video repeats needed: 4
INFO - Video buffer created successfully. Size: 52428800 bytes
```

### 4. YouTube Upload (`upload_youtube.py`)

**Logs:**
- Metadata generation (title, description, tags)
- YouTube authentication process
- Credential management
- Video upload progress
- Playlist management
- Error handling for upload failures

**Key Log Messages:**
```
INFO - === Starting YouTube Upload Process ===
INFO - Generated title: Today's Top India National News - Latest Updates
INFO - === Starting YouTube Authentication Process ===
INFO - Found cached credentials file
INFO - Cached credentials are valid
INFO - === Starting Video Upload Process ===
INFO - Upload progress: 50%
INFO - Video uploaded successfully with ID: ABC123xyz
INFO - Video added to playlist successfully!
```

### 5. Main Workflow (`main_workflow.py`)

**Logs:**
- Overall workflow orchestration
- Step-by-step progress tracking
- Timing information for each step
- Retry logic and error recovery
- Success/failure summaries

**Key Log Messages:**
```
INFO - ================================================================
INFO - TAMIL NEWS GENERATION AND UPLOAD WORKFLOW
INFO - ================================================================
INFO - Workflow started at: 2024-01-15 10:30:00
INFO - ================================================================
INFO - STEP 1: NEWS TEXT GENERATION
INFO - ================================================================
INFO - News text generation completed successfully in 15.23 seconds
INFO - Total workflow time: 180.45 seconds
INFO - WORKFLOW COMPLETED SUCCESSFULLY!
```

## Usage Examples

### Running Individual Modules with Logging

```python
# Test logging system
python test_logging.py

# Run complete workflow with logging
python main_workflow.py

# Run workflow with retry logic
python main_workflow.py --retry
```

### Viewing Logs

```bash
# View today's detailed logs
cat logs/tamil_news_$(date +%Y-%m-%d).log

# View today's error logs
cat logs/errors_$(date +%Y-%m-%d).log

# Monitor logs in real-time
tail -f logs/tamil_news_$(date +%Y-%m-%d).log
```

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about process flow
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations

## Error Handling and Recovery

### Automatic Retry Logic

The main workflow includes automatic retry logic:

```python
# Run with up to 3 retries
python main_workflow.py --retry
```

### Error Logging

All errors are logged with:
- Full error traceback
- Context information
- Timestamp and module details
- Recovery suggestions where applicable

### Common Error Scenarios

1. **API Failures**: Logged with retry suggestions
2. **File Not Found**: Logged with file path and creation instructions
3. **Authentication Errors**: Logged with setup instructions
4. **Network Issues**: Logged with timeout and retry information

## Performance Monitoring

### Timing Information

Each major step logs its execution time:

```
INFO - News text generation completed successfully in 15.23 seconds
INFO - Audio generation completed successfully in 45.67 seconds
INFO - Video generation completed successfully in 120.89 seconds
INFO - YouTube upload completed successfully in 180.45 seconds
```

### Resource Usage

Buffer sizes and file sizes are logged:

```
INFO - Audio buffer size: 1024000 bytes
INFO - Video buffer size: 52428800 bytes
INFO - Generated text length: 2048 characters
```

## Configuration

### Log Level Configuration

To change log levels, modify `logger_config.py`:

```python
def setup_logger(name, log_level=logging.INFO):  # Change default level here
```

### Log File Location

Logs are stored in the `logs/` directory. To change location:

```python
logs_dir = "custom_logs_path"  # Modify in logger_config.py
```

### Log Format

To modify log format, update the formatters in `logger_config.py`:

```python
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
```

## Best Practices

1. **Always check logs first** when troubleshooting issues
2. **Monitor error logs** for recurring problems
3. **Use retry logic** for transient failures
4. **Keep log files** for historical analysis
5. **Rotate old logs** to manage disk space

## Troubleshooting

### Common Issues

1. **No logs generated**: Check if `logs/` directory exists and is writable
2. **Missing log entries**: Verify log level configuration
3. **Encoding issues**: Ensure UTF-8 encoding is used
4. **Permission errors**: Check file permissions for log directory

### Debug Mode

To enable debug logging for troubleshooting:

```python
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)  # Enable debug level
```

## Integration with Monitoring

The logging system can be integrated with external monitoring tools:

- **Log aggregation**: Send logs to centralized logging systems
- **Alerting**: Set up alerts for ERROR level messages
- **Metrics**: Extract timing and performance data from logs
- **Dashboard**: Create dashboards showing workflow success rates

This comprehensive logging system ensures full visibility into the Tamil News generation and upload process, making it easy to monitor, debug, and optimize the workflow. 