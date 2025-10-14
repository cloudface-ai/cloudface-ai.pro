"""
CloudFace Pro - Event Manager
Manages events with Firebase - NO FAKE DATA
"""

import uuid
import json
import os
from datetime import datetime
from typing import Optional, List, Dict
import cloudface_pro_config as config
from cloudface_pro_storage import storage

# Testing mode - use local JSON file instead of Firebase
TESTING_MODE = os.environ.get('TESTING_MODE', 'true').lower() == 'true'


class EventManager:
    """Manage events in Firebase or local JSON (for testing)"""
    
    def __init__(self):
        if TESTING_MODE:
            self.db = None
            self.local_db_path = 'storage/cloudface_pro/events_db.json'
            os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)
            print("🧪 Testing Mode: Using local JSON (not Firebase)")
        else:
            from firebase_store import initialize_firebase
            self.db = initialize_firebase()
            print("🔥 Production Mode: Using Firebase")
        
        self.collection = 'cloudface_pro_events'
    
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
    
    def create_event(self, user_id: str, event_data: dict) -> str:
        """Create a new event - returns event_id"""
        event_id = str(uuid.uuid4())[:12]  # Short UUID
        
        event_doc = {
            'event_id': event_id,
            'user_id': user_id,
            'event_name': event_data.get('event_name', ''),
            'event_date': event_data.get('event_date', ''),
            'event_type': event_data.get('event_type', 'other'),
            'event_details': event_data.get('event_details', ''),
            'company_name': event_data.get('company_name', ''),
            'logo_filename': event_data.get('logo_filename', ''),
            'enable_selling': event_data.get('enable_selling', False),
            'is_public': event_data.get('is_public', True),
            'enable_pin': event_data.get('enable_pin', False),
            'guest_pin': event_data.get('guest_pin', ''),
            'full_access_pin': event_data.get('full_access_pin', ''),
            # Watermark settings
            'enable_watermark': event_data.get('enable_watermark', False),
            'watermark_type': event_data.get('watermark_type', 'text'),
            'watermark_text': event_data.get('watermark_text', ''),
            'watermark_logo_filename': event_data.get('watermark_logo_filename', ''),
            'watermark_position': event_data.get('watermark_position', 'bottom_left'),
            'watermark_opacity': event_data.get('watermark_opacity', 70),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'created',  # created, uploading, processing, ready
            'stats': {
                'total_photos': 0,
                'total_faces': 0,
                'total_searches': 0,
                'total_downloads': 0,
                'storage_bytes': 0
            }
        }
        
        if TESTING_MODE:
            # Save to local JSON
            db = self._load_local_db()
            db[event_id] = event_doc
            self._save_local_db(db)
        else:
            # Save to Firebase
            self.db.collection(self.collection).document(event_id).set(event_doc)
        
        print(f"✅ Created event: {event_id}")
        return event_id
    
    def get_event(self, event_id: str) -> Optional[Dict]:
        """Get event by ID"""
        if TESTING_MODE:
            db = self._load_local_db()
            return db.get(event_id)
        else:
            doc = self.db.collection(self.collection).document(event_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
    
    def update_event(self, event_id: str, updates: dict) -> bool:
        """Update event fields"""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            
            if TESTING_MODE:
                db = self._load_local_db()
                if event_id in db:
                    # Deep update for nested fields (stats.xxx)
                    for key, value in updates.items():
                        if '.' in key:
                            parts = key.split('.')
                            current = db[event_id]
                            for part in parts[:-1]:
                                current = current[part]
                            current[parts[-1]] = value
                        else:
                            db[event_id][key] = value
                    self._save_local_db(db)
            else:
                self.db.collection(self.collection).document(event_id).update(updates)
            
            print(f"✅ Updated event: {event_id}")
            return True
        except Exception as e:
            print(f"❌ Error updating event {event_id}: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """Delete event and all its files"""
        try:
            if TESTING_MODE:
                db = self._load_local_db()
                if event_id in db:
                    del db[event_id]
                    self._save_local_db(db)
            else:
                self.db.collection(self.collection).document(event_id).delete()
            
            # Delete from storage
            storage.delete_event(event_id)
            
            print(f"🗑️ Deleted event: {event_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting event {event_id}: {e}")
            return False
    
    def list_user_events(self, user_id: str, limit: int = 100) -> List[Dict]:
        """List all events for a user"""
        try:
            if TESTING_MODE:
                db = self._load_local_db()
                events = [event for event in db.values() if event.get('user_id') == user_id]
            else:
                docs = self.db.collection(self.collection)\
                    .where('user_id', '==', user_id)\
                    .limit(limit)\
                    .stream()
                
                events = []
                for doc in docs:
                    events.append(doc.to_dict())
            
            # Sort in Python (avoid Firebase index requirement)
            events.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return events
        except Exception as e:
            print(f"❌ Error listing events for {user_id}: {e}")
            return []
    
    def increment_stat(self, event_id: str, stat_name: str, increment: int = 1):
        """Increment a statistic"""
        try:
            if TESTING_MODE:
                db = self._load_local_db()
                if event_id in db:
                    current_value = db[event_id]['stats'].get(stat_name, 0)
                    db[event_id]['stats'][stat_name] = current_value + increment
                    db[event_id]['updated_at'] = datetime.now().isoformat()
                    self._save_local_db(db)
            else:
                event_ref = self.db.collection(self.collection).document(event_id)
                event_ref.update({
                    f'stats.{stat_name}': increment,
                    'updated_at': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"❌ Error incrementing stat: {e}")
    
    def update_storage_size(self, event_id: str):
        """Update storage size from actual files"""
        size_bytes = storage.get_event_size(event_id)
        self.update_event(event_id, {
            'stats.storage_bytes': size_bytes
        })
        return size_bytes


# Global instance
event_manager = EventManager()


if __name__ == "__main__":
    print("🧪 Testing Event Manager...")
    
    # Test create event
    test_user = "test@example.com"
    event_data = {
        'event_name': 'Test Event',
        'event_date': '2025-10-15',
        'company_name': 'Test Company'
    }
    
    event_id = event_manager.create_event(test_user, event_data)
    print(f"Created: {event_id}")
    
    # Test get event
    event = event_manager.get_event(event_id)
    print(f"Retrieved: {event}")
    
    # Test list events
    events = event_manager.list_user_events(test_user)
    print(f"User has {len(events)} events")
    
    # Clean up
    event_manager.delete_event(event_id)
    print("✅ Event Manager test complete!")

