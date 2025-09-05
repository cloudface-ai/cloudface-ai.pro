"""
firebase_store_mock.py - Mock Firebase Firestore for development and testing.
This simulates Firebase operations locally until proper credentials are set up.
"""
import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import numpy as np
from datetime import datetime

# Load environment variables from example.env (dev/local)
load_dotenv('example.env')

# Mock database storage
_mock_database = {}
_mock_counter = 0

FACES_COLLECTION = 'faces'

print("✅ Mock Firebase Firestore client ready (development mode)")


def save_face_embedding(user_id: str, photo_ref: str, embedding: np.ndarray) -> bool:
    """Persist a face embedding for a photo reference under a user."""
    try:
        global _mock_counter
        
        # Convert numpy array to list for storage
        embedding_list = embedding.tolist()
        
        # Create document data
        doc_data = {
            'id': f"mock_doc_{_mock_counter}",
            'user_id': user_id,
            'photo_reference': photo_ref,
            'face_embedding': embedding_list,
            'embedding_dimension': len(embedding_list),
            'created_at': datetime.now().isoformat()
        }
        
        # Store in mock database
        if user_id not in _mock_database:
            _mock_database[user_id] = []
        
        _mock_database[user_id].append(doc_data)
        _mock_counter += 1
        
        print(f"✅ Mock: Saved face embedding for {photo_ref} (doc ID: {doc_data['id']})")
        return True
        
    except Exception as e:
        print(f"❌ save_face_embedding error: {e}")
        return False


def fetch_embeddings_for_user(user_id: str) -> List[Dict[str, Any]]:
    """Fetch all face records for a user."""
    try:
        if user_id not in _mock_database:
            print(f"✅ Mock: No embeddings found for user {user_id}")
            return []
        
        results = _mock_database[user_id]
        print(f"✅ Mock: Fetched {len(results)} face embeddings for user {user_id}")
        return results
        
    except Exception as e:
        print(f"❌ fetch_embeddings_for_user error: {e}")
        return []


def delete_user_face(user_id: str, face_id: str) -> bool:
    """Delete a single face row by id ensuring ownership."""
    try:
        if user_id not in _mock_database:
            print(f"⚠️ Mock: No data found for user {user_id}")
            return False
        
        # Find and remove the document
        user_data = _mock_database[user_id]
        for i, doc in enumerate(user_data):
            if doc['id'] == face_id:
                del user_data[i]
                print(f"✅ Mock: Deleted face embedding {face_id}")
                return True
        
        print(f"⚠️ Mock: Document {face_id} not found for user {user_id}")
        return False
        
    except Exception as e:
        print(f"❌ delete_user_face error: {e}")
        return False


def clear_all_faces() -> bool:
    """Clear all face embeddings from mock database."""
    try:
        global _mock_database, _mock_counter
        
        total_docs = sum(len(docs) for docs in _mock_database.values())
        _mock_database.clear()
        _mock_counter = 0
        
        print(f"✅ Mock: Cleared {total_docs} face embeddings from mock database")
        return True
        
    except Exception as e:
        print(f"❌ clear_all_faces error: {e}")
        return False


def get_firebase_stats() -> Dict[str, Any]:
    """Get mock database statistics."""
    try:
        total_docs = sum(len(docs) for docs in _mock_database.values())
        user_counts = {user_id: len(docs) for user_id, docs in _mock_database.items()}
        
        return {
            "total_faces": total_docs,
            "users": user_counts,
            "collection": FACES_COLLECTION,
            "mode": "mock_development"
        }
        
    except Exception as e:
        return {"error": str(e)}


def export_mock_data(filepath: str = "mock_firebase_data.json") -> bool:
    """Export mock data to JSON file for backup."""
    try:
        with open(filepath, 'w') as f:
            json.dump(_mock_database, f, indent=2)
        print(f"✅ Mock: Exported data to {filepath}")
        return True
    except Exception as e:
        print(f"❌ export_mock_data error: {e}")
        return False


def import_mock_data(filepath: str = "mock_firebase_data.json") -> bool:
    """Import mock data from JSON file."""
    try:
        global _mock_database
        with open(filepath, 'r') as f:
            _mock_database = json.load(f)
        print(f"✅ Mock: Imported data from {filepath}")
        return True
    except Exception as e:
        print(f"❌ import_mock_data error: {e}")
        return False
