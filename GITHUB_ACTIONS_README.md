# GitHub Actions Setup for Tamil News Project

This document explains how to set up and use GitHub Actions to automate your Tamil News generation and upload process.

## Overview

The GitHub Actions workflow will:
- Run automatically at 6:00 AM and 6:00 PM IST daily
- Allow manual triggering with custom options
- Generate news content, audio, and video
- Upload to YouTube
- Save logs and artifacts for debugging

## Setup Instructions

### 1. Repository Setup

1. **Push your code to GitHub** (if not already done)
2. **Create the workflow file**: The `.github/workflows/news.yml` file is already created

### 2. Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

#### Required Secrets:

1. **`GEMINI_API_KEY`**
   - Value: Your Gemini API key
   - Example: `AIzaSyD2twlGOLgwO_cyFgNpCNDR6GlXbGkvcZA`

2. **`CLIENT_JSON`**
   - Value: The **entire content** of your `client.json` file (not just the filename)
   - Copy the entire JSON content from your `client.json` file

#### Optional Secrets (for advanced features):

3. **`YOUTUBE_CHANNEL_ID`** (if you want to specify a different channel)
4. **`PLAYLIST_ID`** (if you want to specify a different playlist)

### 3. Required Files in Repository

Make sure these files are present in your repository root:

- `template.mp4` - Video template file
- `requirements.txt` - Python dependencies
- `main_workflow.py` - Main workflow script
- All your Python modules (`news_text.py`, `news_audio.py`, etc.)

## Workflow Features

### 1. Scheduled Runs

The workflow runs automatically at:
- **6:00 AM IST** (00:30 UTC)
- **6:00 PM IST** (12:30 UTC)

### 2. Manual Trigger

You can manually trigger the workflow with options:
- **Language selection**: Choose between English (`en-in`) or Tamil (`ta`)
- **Retry logic**: Enable/disable automatic retry on failure

### 3. Artifacts

The workflow saves these artifacts:
- **Logs**: Detailed logs for debugging (retained for 7 days)
- **YouTube Token**: Authentication token (retained for 30 days)
- **Generated Video**: Final video file (retained for 1 day)
- **Generated Audio**: Audio files (retained for 1 day)

## How to Use

### Manual Run

1. Go to your GitHub repository
2. Click on **Actions** tab
3. Select **Tamil News Automation** workflow
4. Click **Run workflow**
5. Choose your options:
   - **Language**: `en-in` (English) or `ta` (Tamil)
   - **Retry on failure**: `true` or `false`
6. Click **Run workflow**

### View Results

1. **Check workflow status**: Go to Actions tab to see run status
2. **Download artifacts**: Click on the workflow run → Artifacts section
3. **View logs**: Download the logs artifact or check the workflow run logs
4. **Check YouTube**: Verify the video was uploaded to your channel

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check if `CLIENT_JSON` secret is correctly set
   - Ensure the JSON content is complete and valid
   - First run may require manual authentication

2. **Missing Dependencies**
   - Check if `requirements.txt` is up to date
   - Verify all Python packages are listed

3. **Template Video Missing**
   - Ensure `template.mp4` is in the repository root
   - Check file size (should be reasonable for GitHub)

4. **API Key Issues**
   - Verify `GEMINI_API_KEY` is correct
   - Check if the API key has proper permissions

### Debug Steps

1. **Check workflow logs**: Go to Actions → specific run → View logs
2. **Download logs artifact**: Contains detailed application logs
3. **Check error messages**: Look for specific error details in the logs
4. **Verify secrets**: Ensure all secrets are properly configured

## Security Considerations

1. **API Keys**: Never commit API keys to the repository
2. **Credentials**: Use GitHub secrets for all sensitive data
3. **Token Management**: YouTube tokens are automatically managed
4. **Cleanup**: Temporary files are cleaned up after each run

## Customization

### Modify Schedule

To change the schedule, edit the `cron` expressions in `.github/workflows/news.yml`:

```yaml
schedule:
  - cron: '30 0 * * *'   # 6:00 AM IST
  - cron: '30 12 * * *'  # 6:00 PM IST
```

### Add Notifications

You can add email or Slack notifications by modifying the workflow:

```yaml
- name: Send notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Environment Variables

Add more environment variables if needed:

```yaml
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  CUSTOM_VAR: ${{ secrets.CUSTOM_VAR }}
```

## Monitoring

### Check Workflow Status

- **Recent runs**: Actions tab shows recent workflow executions
- **Success rate**: Monitor how often the workflow succeeds
- **Execution time**: Track how long each run takes

### Performance Optimization

- **Caching**: Consider adding dependency caching for faster runs
- **Parallel jobs**: Split workflow into parallel jobs if needed
- **Resource usage**: Monitor GitHub Actions minutes usage

## Support

If you encounter issues:

1. **Check the logs**: Download and review the logs artifact
2. **Verify setup**: Ensure all secrets and files are correctly configured
3. **Test locally**: Run the workflow locally to identify issues
4. **GitHub Issues**: Create an issue in your repository for persistent problems

## Example Workflow Run

A successful workflow run will show:

```
✅ Tamil News workflow completed successfully!
📅 Run time: Mon Jun 17 17:55:51 UTC 2024
🔗 Run URL: https://github.com/username/repo/actions/runs/123456789
```

The workflow will create artifacts:
- `logs-123456789` - Detailed application logs
- `youtube-token` - YouTube authentication token
- `video-123456789` - Generated video file
- `audio-123456789` - Generated audio files

This setup provides a robust, automated solution for your Tamil News generation and upload process! 