# auth_handler.py - Direct Google OAuth Authentication
import os
import json
import base64
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from dotenv import load_dotenv

# Load environment variables
load_dotenv('example.env')

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8550/auth/callback')

# Google OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/drive.readonly'  # For Google Drive access
]

def test_google_setup():
    """Test function to verify Google OAuth configuration."""
    print("🔧 Testing Google OAuth Setup...")
    
    if not GOOGLE_CLIENT_ID:
        print("❌ GOOGLE_CLIENT_ID not found in example.env")
        print("Please add your Google OAuth client ID to example.env:")
        print("GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com")
        return False
    
    if not GOOGLE_CLIENT_SECRET:
        print("❌ GOOGLE_CLIENT_SECRET not found in example.env")
        print("Please add your Google OAuth client secret to example.env:")
        print("GOOGLE_CLIENT_SECRET=your_client_secret")
        return False
    
    print("✅ Google OAuth configuration looks good!")
    print(f"✅ Client ID: {GOOGLE_CLIENT_ID[:20]}...")
    print(f"✅ Redirect URI: {GOOGLE_REDIRECT_URI}")
    return True

def get_google_login_url():
    """Generate Google OAuth login URL."""
    if not test_google_setup():
        return None
    
    try:
        # Create OAuth flow with explicit redirect URI
        flow = InstalledAppFlow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI],
                    "scopes": SCOPES
                }
            },
            scopes=SCOPES
        )
        
        # Force the redirect URI to be used
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # Generate authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='select_account consent'
        )
        
        print(f"✅ Google OAuth URL generated: {auth_url[:50]}...")
        return auth_url
        
    except Exception as e:
        print(f"❌ Error generating Google OAuth URL: {e}")
        return None
    
def exchange_code_for_tokens(authorization_code):
    """Exchange authorization code for access and refresh tokens."""
    try:
        print(f"🔄 Exchanging authorization code for tokens...")
        
        # Token exchange request
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_REDIRECT_URI
        }
        
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        
        tokens = response.json()
        print("✅ Token exchange successful")
        
        return tokens
        
    except Exception as e:
        print(f"❌ Token exchange error: {e}")
        return None

def get_user_info(access_token):
    """Get user information from Google using access token."""
    try:
        print(f"🔍 Getting user info from Google...")
        
        # Get user profile
        profile_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(profile_url, headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        print(f"✅ User info retrieved: {user_data.get('email', 'No email')}")
        
        # Create user info structure
        user_info = {
            'id': user_data.get('id', 'unknown'),
            'email': user_data.get('email', 'no-email@google.com'),
            'name': user_data.get('name', 'Google User'),
            'picture': user_data.get('picture'),
            'google_user': user_data.get('id'),
            'access_token': access_token
        }
        
        return user_info
        
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return None

def verify_access_token(access_token):
    """Verify if the access token is still valid."""
    try:
        # Try to get user info with the token
        user_info = get_user_info(access_token)
        return user_info is not None
        
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return False

def refresh_access_token(refresh_token):
    """Refresh an expired access token."""
    try:
        print("🔄 Refreshing access token...")
        
        # Create credentials object
        creds = Credentials(
            None,  # No access token initially
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )
        
        # Refresh the token
        creds.refresh(Request())
        
        print("✅ Access token refreshed successfully")
        return creds.token
        
    except RefreshError as e:
        print(f"❌ Token refresh failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during token refresh: {e}")
        return None

def create_test_user():
    """Create a test user for development purposes."""
    return {
        'id': 'test_user_123',
        'email': 'test@example.com',
        'name': 'Test User',
        'picture': None,
        'google_user': 'test_mode',
        'access_token': 'test_token'
    }

def test_google_connection():
    """Test the connection to Google OAuth."""
    try:
        print("🔍 Testing Google OAuth connection...")
        
        # Test configuration
        if not test_google_setup():
            return False
        
        # Test URL generation
        login_url = get_google_login_url()
        if not login_url:
            print("❌ Failed to generate login URL")
            return False
        
        print("✅ Google OAuth connection test passed")
        return True
        
    except Exception as e:
        print(f"❌ Google OAuth connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google OAuth Authentication Setup...")
    print("=" * 60)
    
    # Test 1: Environment variables
    print("\n1. Testing environment variables...")
    test_google_setup()
    
    # Test 2: Google OAuth connection
    print("\n2. Testing Google OAuth connection...")
    test_google_connection()
    
    # Test 3: Login URL generation
    print("\n3. Testing login URL generation...")
    login_url = get_google_login_url()
    if login_url:
        print(f"✅ Login URL: {login_url[:80]}...")
    else:
        print("❌ Failed to generate login URL")
    
    print("\n" + "=" * 60)
    print("✅ Google OAuth Authentication Setup Test Complete!")
    print("\n📋 Next steps:")
    print("1. Add your Google OAuth credentials to example.env")
    print("2. Run your main app: python main_app.py")
    print("3. Click 'Sign in with Google'")
    print("4. Complete OAuth flow on Google's page")