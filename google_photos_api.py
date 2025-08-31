"""
google_photos_api.py - Google Photos API integration for face recognition and photo search
Integrates with existing Facetak system to find user's photos in Google Drive folders
"""
import os
import requests
import json
from typing import List, Dict, Optional, Tuple
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from datetime import datetime, timedelta

# Google Photos API scopes
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/photoslibrary.sharing'
]

class GooglePhotosAPI:
    def __init__(self, credentials_path: str = None):
        """Initialize Google Photos API with authentication"""
        self.credentials_path = credentials_path or 'token.pickle'
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Photos API"""
        creds = None
        
        # Load existing credentials if available
        if os.path.exists(self.credentials_path):
            with open(self.credentials_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Try to load from client secrets file
                client_secrets_file = 'client_secret_2_578997008856-nlb4os28315p5jasdncjlgpat69hp7gk.apps.googleusercontent.com.json'
                
                if os.path.exists(client_secrets_file):
                    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    print("⚠️ Client secrets file not found. Please ensure it's in the project directory.")
                    return
            
            # Save credentials for next run
            with open(self.credentials_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build the Photos Library API service
        try:
            self.service = build('photoslibrary', 'v1', credentials=creds)
            print("✅ Google Photos API authenticated successfully")
        except Exception as e:
            print(f"❌ Failed to build Photos API service: {e}")
            self.service = None
    
    def search_user_photos(self, query: str = None, filters: Dict = None) -> List[Dict]:
        """Search through user's Google Photos"""
        if not self.service:
            print("❌ Photos API service not available")
            return []
        
        try:
            # Build search request
            search_request = {
                'pageSize': 100,
                'filters': filters or {}
            }
            
            if query:
                search_request['filters']['textFilter'] = query
            
            # Execute search
            results = self.service.mediaItems().search(body=search_request).execute()
            
            photos = results.get('mediaItems', [])
            print(f"📸 Found {len(photos)} photos in Google Photos")
            
            return photos
            
        except Exception as e:
            print(f"❌ Error searching Google Photos: {e}")
            return []
    
    def get_photo_details(self, photo_id: str) -> Optional[Dict]:
        """Get detailed information about a specific photo"""
        if not self.service:
            return None
        
        try:
            photo = self.service.mediaItems().get(mediaItemId=photo_id).execute()
            return photo
        except Exception as e:
            print(f"❌ Error getting photo details: {e}")
            return None
    
    def search_photos_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Search photos within a specific date range"""
        filters = {
            'dateFilter': {
                'ranges': [{
                    'startDate': {
                        'year': start_date.year,
                        'month': start_date.month,
                        'day': start_date.day
                    },
                    'endDate': {
                        'year': end_date.year,
                        'month': end_date.month,
                        'day': end_date.day
                    }
                }]
            }
        }
        
        return self.search_user_photos(filters=filters)
    
    def search_photos_by_album(self, album_id: str) -> List[Dict]:
        """Search photos in a specific album"""
        filters = {
            'albumFilter': {
                'albumIds': [album_id]
            }
        }
        
        return self.search_user_photos(filters=filters)
    
    def get_user_albums(self) -> List[Dict]:
        """Get list of user's albums"""
        if not self.service:
            return []
        
        try:
            albums = self.service.albums().list(pageSize=50).execute()
            return albums.get('albums', [])
        except Exception as e:
            print(f"❌ Error getting albums: {e}")
            return []

class FaceSearchIntegration:
    """Integrates Google Photos API with existing face recognition system"""
    
    def __init__(self, photos_api: GooglePhotosAPI):
        self.photos_api = photos_api
    
    def find_user_photos_in_drive_folder(self, 
                                        selfie_embedding: List[float], 
                                        drive_folder_photos: List[str],
                                        threshold: float = 0.6) -> List[Dict]:
        """
        Find user's photos in a Google Drive folder using face recognition
        
        Args:
            selfie_embedding: Face embedding from user's selfie
            drive_folder_photos: List of photo paths from Drive folder
            threshold: Similarity threshold for face matching
        
        Returns:
            List of matching photos with metadata
        """
        print("🔍 Starting face search integration...")
        
        # Step 1: Search user's Google Photos for similar faces
        print("📸 Searching Google Photos for user's photos...")
        user_photos = self.photos_api.search_user_photos()
        
        if not user_photos:
            print("⚠️ No photos found in Google Photos")
            return []
        
        # Step 2: Get face embeddings for user's photos (this would use your existing embedding system)
        # For now, we'll simulate this step
        print(f"🎭 Processing {len(user_photos)} photos for face embeddings...")
        
        # Step 3: Find photos in Drive folder that match user's face
        print("🔍 Cross-referencing with Drive folder photos...")
        matching_photos = []
        
        # This is where you'd integrate with your existing face recognition system
        # For now, returning the structure
        for photo_path in drive_folder_photos:
            # Simulate face matching (replace with actual face recognition)
            match_score = self._simulate_face_match(selfie_embedding, photo_path)
            
            if match_score > threshold:
                matching_photos.append({
                    'photo_path': photo_path,
                    'match_score': match_score,
                    'source': 'drive_folder',
                    'user_photo_reference': 'matched_from_photos'
                })
        
        print(f"✅ Found {len(matching_photos)} matching photos in Drive folder")
        return matching_photos
    
    def _simulate_face_match(self, selfie_embedding: List[float], photo_path: str) -> float:
        """Simulate face matching (replace with actual face recognition)"""
        # This is a placeholder - you'd use your existing face recognition here
        import random
        return random.uniform(0.0, 1.0)

def create_photos_api_service() -> GooglePhotosAPI:
    """Factory function to create Google Photos API service"""
    return GooglePhotosAPI()

def integrate_with_existing_system():
    """Example of how to integrate with your existing system"""
    
    # Initialize Photos API
    photos_api = create_photos_api_service()
    
    # Create integration layer
    face_search = FaceSearchIntegration(photos_api)
    
    # Example usage (this would be called from your existing code)
    def search_user_faces_in_drive(selfie_embedding, drive_photos):
        return face_search.find_user_photos_in_drive_folder(
            selfie_embedding, 
            drive_photos
        )
    
    return face_search

# Example usage
if __name__ == "__main__":
    print("🚀 Google Photos API Integration Module")
    print("📸 This module provides Google Photos API functionality")
    print("🔍 Integrates with existing face recognition system")
    print("💡 Import and use in your main application")
    
    # Test the API connection
    try:
        photos_api = create_photos_api_service()
        if photos_api.service:
            print("✅ API connection successful")
            
            # Get user albums as a test
            albums = photos_api.get_user_albums()
            print(f"📁 Found {len(albums)} albums")
            
        else:
            print("❌ API connection failed")
    except Exception as e:
        print(f"❌ Error testing API: {e}")
