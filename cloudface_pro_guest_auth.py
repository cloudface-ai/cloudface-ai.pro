"""
CloudFace Pro - Guest Authentication
Manages guest user accounts and selfie storage
"""

import uuid
import json
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict
from cloudface_pro_storage import storage

# Testing mode - use local JSON file instead of Firebase
TESTING_MODE = os.environ.get('TESTING_MODE', 'true').lower() == 'true'


class GuestAuth:
    """Manage guest user accounts"""
    
    def __init__(self):
        if TESTING_MODE:
            self.db = None
            self.local_db_path = 'storage/cloudface_pro/guests_db.json'
            os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)
            print("🧪 Guest Auth: Using local JSON (not Firebase)")
        else:
            from firebase_store import initialize_firebase
            self.db = initialize_firebase()
            print("🔥 Guest Auth: Using Firebase")
        
        self.collection = 'cloudface_pro_guests'
    
    def _load_local_db(self) -> Dict:
        """Load local JSON database"""
        if os.path.exists(self.local_db_path):
            with open(self.local_db_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_local_db(self, data: Dict):
        """Save local JSON database"""
        with open(self.local_db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_guest(self, email: str, password: str, name: str, phone: str = '') -> Optional[Dict]:
        """
        Create new guest account
        Returns guest data if successful, None if email exists
        """
        guest_id = str(uuid.uuid4())[:12]
        
        guest_doc = {
            'guest_id': guest_id,
            'email': email.lower(),
            'password_hash': self._hash_password(password),
            'name': name,
            'phone': phone,
            'selfie_filename': None,  # Will be set when selfie is uploaded
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'events_accessed': [],  # List of event IDs they've accessed
            'total_searches': 0,
            'total_downloads': 0
        }
        
        if TESTING_MODE:
            # Check if email exists
            db = self._load_local_db()
            for guest in db.values():
                if guest.get('email') == email.lower():
                    return None  # Email already exists
            
            db[guest_id] = guest_doc
            self._save_local_db(db)
        else:
            # Check Firebase
            existing = self.db.collection(self.collection)\
                .where('email', '==', email.lower())\
                .limit(1)\
                .get()
            
            if len(list(existing)) > 0:
                return None  # Email exists
            
            self.db.collection(self.collection).document(guest_id).set(guest_doc)
        
        print(f"✅ Created guest account: {email}")
        return {
            'guest_id': guest_id,
            'email': email,
            'name': name
        }
    
    def sign_in(self, email: str, password: str) -> Optional[Dict]:
        """
        Sign in guest
        Returns guest data if successful
        """
        password_hash = self._hash_password(password)
        
        if TESTING_MODE:
            db = self._load_local_db()
            for guest_id, guest in db.items():
                if guest.get('email') == email.lower() and guest.get('password_hash') == password_hash:
                    # Update last login
                    db[guest_id]['last_login'] = datetime.now().isoformat()
                    self._save_local_db(db)
                    
                    return {
                        'guest_id': guest_id,
                        'email': guest['email'],
                        'name': guest['name'],
                        'selfie_filename': guest.get('selfie_filename')
                    }
            return None
        else:
            # Firebase query
            results = self.db.collection(self.collection)\
                .where('email', '==', email.lower())\
                .where('password_hash', '==', password_hash)\
                .limit(1)\
                .get()
            
            for doc in results:
                guest = doc.to_dict()
                # Update last login
                self.db.collection(self.collection).document(doc.id).update({
                    'last_login': datetime.now().isoformat()
                })
                return {
                    'guest_id': doc.id,
                    'email': guest['email'],
                    'name': guest['name'],
                    'selfie_filename': guest.get('selfie_filename')
                }
            
            return None
    
    def get_guest(self, guest_id: str) -> Optional[Dict]:
        """Get guest by ID"""
        if TESTING_MODE:
            db = self._load_local_db()
            return db.get(guest_id)
        else:
            doc = self.db.collection(self.collection).document(guest_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
    
    def update_guest(self, guest_id: str, updates: dict) -> bool:
        """Update guest fields"""
        try:
            if TESTING_MODE:
                db = self._load_local_db()
                if guest_id in db:
                    for key, value in updates.items():
                        db[guest_id][key] = value
                    self._save_local_db(db)
            else:
                self.db.collection(self.collection).document(guest_id).update(updates)
            
            return True
        except Exception as e:
            print(f"❌ Error updating guest {guest_id}: {e}")
            return False
    
    def save_guest_selfie(self, guest_id: str, selfie_bytes: bytes) -> Optional[str]:
        """
        Save guest's selfie photo
        Returns filename if successful
        """
        try:
            from io import BytesIO
            
            filename = f"guest_{guest_id}_selfie.jpg"
            
            # Save to storage (wrap bytes in BytesIO for file-like interface)
            selfie_path = f"guests/{guest_id}/{filename}"
            storage.save_file(selfie_path, BytesIO(selfie_bytes))
            
            # Update guest record
            self.update_guest(guest_id, {'selfie_filename': filename})
            
            print(f"✅ Saved selfie for guest {guest_id}: {len(selfie_bytes)} bytes")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving guest selfie: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_guest_selfie(self, guest_id: str) -> Optional[bytes]:
        """Get guest's stored selfie"""
        guest = self.get_guest(guest_id)
        if not guest or not guest.get('selfie_filename'):
            return None
        
        selfie_path = f"guests/{guest_id}/{guest['selfie_filename']}"
        return storage.get_file(selfie_path)
    
    def track_event_access(self, guest_id: str, event_id: str):
        """Track which events a guest has accessed"""
        try:
            if TESTING_MODE:
                db = self._load_local_db()
                if guest_id in db:
                    events = db[guest_id].get('events_accessed', [])
                    if event_id not in events:
                        events.append(event_id)
                        db[guest_id]['events_accessed'] = events
                        self._save_local_db(db)
        except Exception as e:
            print(f"❌ Error tracking event access: {e}")
    
    def increment_guest_stat(self, guest_id: str, stat_name: str):
        """Increment guest statistics (searches, downloads)"""
        try:
            if TESTING_MODE:
                db = self._load_local_db()
                if guest_id in db:
                    current = db[guest_id].get(stat_name, 0)
                    db[guest_id][stat_name] = current + 1
                    self._save_local_db(db)
        except Exception as e:
            print(f"❌ Error incrementing guest stat: {e}")


# Global instance
guest_auth = GuestAuth()


if __name__ == "__main__":
    print("🧪 Testing Guest Auth...")
    
    # Test create guest
    result = guest_auth.create_guest(
        email="test@example.com",
        password="password123",
        name="Test Guest",
        phone="+1234567890"
    )
    
    if result:
        print(f"✅ Created guest: {result}")
        
        # Test sign in
        login = guest_auth.sign_in("test@example.com", "password123")
        print(f"✅ Login successful: {login}")
        
        # Clean up
        if TESTING_MODE:
            db = guest_auth._load_local_db()
            if result['guest_id'] in db:
                del db[result['guest_id']]
                guest_auth._save_local_db(db)
    else:
        print("❌ Guest creation failed (email exists)")
    
    print("✅ Guest Auth test complete!")

