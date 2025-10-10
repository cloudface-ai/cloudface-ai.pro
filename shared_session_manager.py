"""
Shared Session Manager for CloudFace AI
Allows admins to process photos and share access with end users
"""
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from firebase_store import db

SESSIONS_COLLECTION = 'shared_sessions'

class SharedSessionManager:
    """Manages shared photo processing sessions"""
    
    def __init__(self):
        self.db = db
    
    def create_session(self, admin_user_id: str, folder_id: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Create a new shared session after admin processes photos
        
        Args:
            admin_user_id: The admin who processed the photos
            folder_id: The Google Drive folder ID that was processed
            metadata: Additional info (event name, date, company, etc.)
        
        Returns:
            session_id: Unique session ID for sharing
        """
        try:
            if self.db is None:
                print("⚠️  No Firebase client; cannot create shared session")
                return None
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())[:12]  # Short ID like: a1b2c3d4e5f6
            
            # Create session document
            session_data = {
                'session_id': session_id,
                'admin_user_id': admin_user_id,
                'folder_id': folder_id,
                'metadata': metadata,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(days=30)).isoformat(),  # 30 days validity
                'access_count': 0,
                'status': 'active'
            }
            
            # Save to Firestore
            doc_ref = self.db.collection(SESSIONS_COLLECTION).document(session_id)
            doc_ref.set(session_data)
            
            print(f"✅ Created shared session: {session_id}")
            print(f"   Admin: {admin_user_id}")
            print(f"   Folder: {folder_id}")
            print(f"   Event: {metadata.get('event_name', 'N/A')}")
            
            return session_id
            
        except Exception as e:
            print(f"❌ Error creating shared session: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session details by session ID
        
        Args:
            session_id: The session ID to retrieve
        
        Returns:
            Session data dict or None if not found/expired
        """
        try:
            if self.db is None:
                print("⚠️  No Firebase client; cannot get session")
                return None
            
            # Get session document
            doc_ref = self.db.collection(SESSIONS_COLLECTION).document(session_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                print(f"❌ Session not found: {session_id}")
                return None
            
            session_data = doc.to_dict()
            
            # Check if expired
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.utcnow() > expires_at:
                print(f"❌ Session expired: {session_id}")
                return None
            
            # Check if active
            if session_data.get('status') != 'active':
                print(f"❌ Session not active: {session_id}")
                return None
            
            # Increment access count
            doc_ref.update({'access_count': session_data.get('access_count', 0) + 1})
            
            print(f"✅ Retrieved session: {session_id}")
            return session_data
            
        except Exception as e:
            print(f"❌ Error getting session: {e}")
            return None
    
    def deactivate_session(self, session_id: str, admin_user_id: str) -> bool:
        """
        Deactivate a session (only by admin who created it)
        
        Args:
            session_id: Session to deactivate
            admin_user_id: Admin requesting deactivation
        
        Returns:
            True if successful
        """
        try:
            if self.db is None:
                return False
            
            doc_ref = self.db.collection(SESSIONS_COLLECTION).document(session_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            session_data = doc.to_dict()
            
            # Verify admin owns this session
            if session_data.get('admin_user_id') != admin_user_id:
                print(f"❌ Unauthorized: {admin_user_id} cannot deactivate session {session_id}")
                return False
            
            # Deactivate
            doc_ref.update({'status': 'inactive'})
            print(f"✅ Deactivated session: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deactivating session: {e}")
            return False
    
    def get_admin_sessions(self, admin_user_id: str) -> List[Dict[str, Any]]:
        """
        Get all sessions created by an admin
        
        Args:
            admin_user_id: The admin user ID
        
        Returns:
            List of session dictionaries
        """
        try:
            if self.db is None:
                return []
            
            # Query sessions by admin
            query = self.db.collection(SESSIONS_COLLECTION).where('admin_user_id', '==', admin_user_id)
            docs = query.stream()
            
            sessions = []
            for doc in docs:
                session_data = doc.to_dict()
                session_data['id'] = doc.id
                sessions.append(session_data)
            
            print(f"✅ Retrieved {len(sessions)} sessions for admin {admin_user_id}")
            return sessions
            
        except Exception as e:
            print(f"❌ Error getting admin sessions: {e}")
            return []

# Global instance
_session_manager = None

def get_session_manager() -> SharedSessionManager:
    """Get or create the shared session manager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SharedSessionManager()
    return _session_manager

