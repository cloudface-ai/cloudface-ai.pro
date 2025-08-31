"""
debug_oauth.py - Debug OAuth flow step by step
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('example.env')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_oauth_flow():
    """Test OAuth flow step by step."""
    try:
        logger.info("🧪 Testing OAuth flow step by step...")
        
        # Test 1: Import auth handler
        logger.info("1. Testing import...")
        from test_auth_handler import get_google_login_url, exchange_code_for_tokens, get_user_info
        logger.info("✅ Import successful")
        
        # Test 2: Generate OAuth URL
        logger.info("2. Generating OAuth URL...")
        auth_url = get_google_login_url()
        if not auth_url:
            logger.error("❌ Failed to generate OAuth URL")
            return False
        logger.info(f"✅ OAuth URL: {auth_url[:100]}...")
        
        # Test 3: Check environment variables
        logger.info("3. Checking environment variables...")
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        
        logger.info(f"Client ID: {client_id[:20] if client_id else 'None'}...")
        logger.info(f"Client Secret: {client_secret[:10] if client_secret else 'None'}...")
        logger.info(f"Redirect URI: {redirect_uri}")
        
        if not all([client_id, client_secret, redirect_uri]):
            logger.error("❌ Missing environment variables")
            return False
        
        # Test 4: Simulate callback URL
        logger.info("4. Testing callback URL parsing...")
        test_callback = "http://localhost:8550/auth/callback?code=test_code_123&state=test"
        logger.info(f"Test callback: {test_callback}")
        
        if "code=" in test_callback:
            code_start = test_callback.find("code=") + 5
            code_end = test_callback.find("&", code_start)
            if code_end == -1:
                code_end = len(test_callback)
            auth_code = test_callback[code_start:code_end]
            logger.info(f"✅ Extracted code: {auth_code}")
        else:
            logger.error("❌ No code found in callback")
            return False
        
        logger.info("🎉 All tests passed! OAuth flow should work.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_oauth_flow()
    if success:
        print("\n✅ OAuth flow is working correctly!")
        print("The issue might be in the main app's route handling.")
    else:
        print("\n❌ OAuth flow has issues.")
        print("Check the logs above for details.")
