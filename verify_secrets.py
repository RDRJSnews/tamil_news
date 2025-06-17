#!/usr/bin/env python3
"""
Script to verify GitHub secrets configuration
Run this locally to test if your environment variables are set correctly
"""

import os
import json
from logger_config import get_logger

# Set up logger
logger = get_logger(__name__)

def verify_gemini_api_key():
    """Verify GEMINI_API_KEY is set and valid."""
    logger.info("=== Verifying GEMINI_API_KEY ===")
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        logger.error("❌ GEMINI_API_KEY environment variable is not set!")
        logger.info("💡 To set it locally: export GEMINI_API_KEY='your_api_key_here'")
        return False
    
    if api_key == "AIzaSyD2twlGOLgwO_cyFgNpCNDR6GlXbGkvcZA":
        logger.warning("⚠️  Using default API key - this might not work in production")
    
    logger.info(f"✅ GEMINI_API_KEY is set (length: {len(api_key)} characters)")
    logger.info(f"🔑 Key starts with: {api_key[:10]}...")
    return True

def verify_client_json():
    """Verify CLIENT_JSON is set and valid."""
    logger.info("=== Verifying CLIENT_JSON ===")
    
    client_json_str = os.getenv('CLIENT_JSON')
    
    if not client_json_str:
        logger.error("❌ CLIENT_JSON environment variable is not set!")
        logger.info("💡 To set it locally: export CLIENT_JSON='your_json_content_here'")
        return False
    
    try:
        # Try to parse the JSON to verify it's valid
        client_json = json.loads(client_json_str)
        
        # Check for required fields
        if 'web' not in client_json:
            logger.error("❌ CLIENT_JSON is missing 'web' section")
            return False
        
        web_config = client_json['web']
        required_fields = ['client_id', 'client_secret', 'project_id']
        
        for field in required_fields:
            if field not in web_config:
                logger.error(f"❌ CLIENT_JSON is missing '{field}' field")
                return False
        
        logger.info("✅ CLIENT_JSON is valid and contains required fields")
        logger.info(f"📋 Project ID: {web_config.get('project_id', 'Not found')}")
        logger.info(f"🆔 Client ID: {web_config.get('client_id', 'Not found')[:10]}...")
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ CLIENT_JSON is not valid JSON: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Error parsing CLIENT_JSON: {str(e)}")
        return False

def verify_file_exists():
    """Verify required files exist."""
    logger.info("=== Verifying Required Files ===")
    
    required_files = [
        'template.mp4',
        'requirements.txt',
        'main_workflow.py',
        'news_text.py',
        'news_audio.py',
        'news_video.py',
        'upload_youtube.py',
        'logger_config.py'
    ]
    
    all_files_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            logger.info(f"✅ {file_path} exists ({file_size} bytes)")
        else:
            logger.error(f"❌ {file_path} is missing!")
            all_files_exist = False
    
    return all_files_exist

def verify_github_workflow():
    """Verify GitHub workflow file exists."""
    logger.info("=== Verifying GitHub Workflow ===")
    
    workflow_path = '.github/workflows/news.yml'
    
    if os.path.exists(workflow_path):
        logger.info(f"✅ GitHub workflow exists: {workflow_path}")
        return True
    else:
        logger.error(f"❌ GitHub workflow missing: {workflow_path}")
        return False

def main():
    """Main verification function."""
    logger.info("🔍 Starting GitHub Secrets Verification")
    logger.info("=" * 50)
    
    results = []
    
    # Run all verifications
    results.append(("GEMINI_API_KEY", verify_gemini_api_key()))
    results.append(("CLIENT_JSON", verify_client_json()))
    results.append(("Required Files", verify_file_exists()))
    results.append(("GitHub Workflow", verify_github_workflow()))
    
    # Summary
    logger.info("=" * 50)
    logger.info("📊 VERIFICATION SUMMARY")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"Overall: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🎉 All verifications passed! Your setup is ready for GitHub Actions.")
        logger.info("📝 Next steps:")
        logger.info("   1. Push your code to GitHub")
        logger.info("   2. Add the secrets in GitHub repository settings")
        logger.info("   3. Test the workflow manually")
    else:
        logger.error("⚠️  Some verifications failed. Please fix the issues above.")
        logger.info("💡 Tips:")
        logger.info("   - Set environment variables: export VARIABLE_NAME='value'")
        logger.info("   - Check file paths and permissions")
        logger.info("   - Ensure all required files are present")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 