"""
CloudFace Pro - Firebase Authentication
Email/Password login using Firebase Auth (no Google OAuth needed)
"""

import requests
import os
import json
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, Dict

load_dotenv('.env')

# Testing mode - use local JSON file
TESTING_MODE = os.environ.get('TESTING_MODE', 'true').lower() == 'true'

# Firebase Auth REST API
FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY')
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"


class FirebaseAuth:
    """Firebase Authentication handler"""
    
    def __init__(self):
        if TESTING_MODE:
            self.api_key = None
            self.local_users_path = 'storage/cloudface_pro/users_db.json'
            os.makedirs(os.path.dirname(self.local_users_path), exist_ok=True)
            print("🧪 Testing Mode: Using local auth (not Firebase)")
        else:
            self.api_key = FIREBASE_API_KEY
            if not self.api_key:
                raise ValueError("FIREBASE_API_KEY not found in environment")
            print("🔥 Production Mode: Using Firebase Auth")
    
    def _load_users(self) -> Dict:
        """Load local users database"""
        if os.path.exists(self.local_users_path):
            with open(self.local_users_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_users(self, users: Dict):
        """Save local users database"""
        with open(self.local_users_path, 'w') as f:
            json.dump(users, f, indent=2)
    
    def sign_up(self, email: str, password: str) -> Optional[Dict]:
        """
        Create new user account
        Returns: {'user_id': '...', 'email': '...', 'token': '...'}
        """
        if TESTING_MODE:
            # Local testing mode
            users = self._load_users()
            
            if email in users:
                print(f"❌ User already exists: {email}")
                return None
            
            user_id = hashlib.md5(email.encode()).hexdigest()[:12]
            token = hashlib.md5(f"{email}{password}".encode()).hexdigest()
            
            users[email] = {
                'user_id': user_id,
                'email': email,
                'password_hash': hashlib.sha256(password.encode()).hexdigest(),
                'created_at': datetime.now().isoformat()
            }
            
            self._save_users(users)
            print(f"✅ User created (local): {email}")
            
            return {
                'user_id': user_id,
                'email': email,
                'token': token,
                'refresh_token': ''
            }
        else:
            # Firebase mode
            url = f"{FIREBASE_AUTH_URL}:signUp?key={self.api_key}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            try:
                response = requests.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    print(f"✅ User created: {email}")
                    return {
                        'user_id': data['localId'],
                        'email': data['email'],
                        'token': data['idToken'],
                        'refresh_token': data['refreshToken']
                    }
                else:
                    error = data.get('error', {}).get('message', 'Unknown error')
                    print(f"❌ Sign up failed: {error}")
                    return None
                    
            except Exception as e:
                print(f"❌ Sign up error: {e}")
                return None
    
    def sign_in(self, email: str, password: str) -> Optional[Dict]:
        """
        Sign in existing user
        Returns: {'user_id': '...', 'email': '...', 'token': '...'}
        """
        if TESTING_MODE:
            # Local testing mode
            users = self._load_users()
            
            if email not in users:
                print(f"❌ User not found: {email}")
                return None
            
            user = users[email]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if user['password_hash'] != password_hash:
                print(f"❌ Invalid password for: {email}")
                return None
            
            token = hashlib.md5(f"{email}{password}".encode()).hexdigest()
            
            print(f"✅ User signed in (local): {email}")
            return {
                'user_id': user['user_id'],
                'email': email,
                'token': token,
                'refresh_token': ''
            }
        else:
            # Firebase mode
            url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={self.api_key}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            try:
                response = requests.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    print(f"✅ User signed in: {email}")
                    return {
                        'user_id': data['localId'],
                        'email': data['email'],
                        'token': data['idToken'],
                        'refresh_token': data['refreshToken']
                    }
                else:
                    error = data.get('error', {}).get('message', 'Unknown error')
                    print(f"❌ Sign in failed: {error}")
                    return None
                    
            except Exception as e:
                print(f"❌ Sign in error: {e}")
                return None
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify ID token
        Returns: {'user_id': '...', 'email': '...'}
        """
        url = f"{FIREBASE_AUTH_URL}:lookup?key={self.api_key}"
        
        payload = {
            "idToken": token
        }
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            
            if response.status_code == 200 and data.get('users'):
                user = data['users'][0]
                return {
                    'user_id': user['localId'],
                    'email': user['email']
                }
            return None
                
        except Exception as e:
            print(f"❌ Token verification error: {e}")
            return None
    
    def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        url = f"{FIREBASE_AUTH_URL}:sendOobCode?key={self.api_key}"
        
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                print(f"✅ Password reset email sent to: {email}")
                return True
            return False
                
        except Exception as e:
            print(f"❌ Password reset error: {e}")
            return False


# Global instance
auth = FirebaseAuth()


if __name__ == "__main__":
    print("🧪 Testing Firebase Auth...")
    
    # Test sign up
    result = auth.sign_up("test@example.com", "password123")
    if result:
        print(f"User ID: {result['user_id']}")
        print(f"Email: {result['email']}")
    
    # Test sign in
    result = auth.sign_in("test@example.com", "password123")
    if result:
        print(f"Signed in: {result['email']}")
        
        # Test verify
        user = auth.verify_token(result['token'])
        print(f"Verified: {user}")
    
    print("✅ Auth test complete!")

