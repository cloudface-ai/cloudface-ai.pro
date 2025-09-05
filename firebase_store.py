"""
firebase_store.py - Save and query face embeddings and metadata in Firebase Firestore.
"""
import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np

# Load environment variables from example.env (dev/local)
load_dotenv('example.env')

# Firebase configuration from environment variables
FIREBASE_CONFIG = {
    "apiKey": os.environ.get('FIREBASE_API_KEY'),
    "authDomain": os.environ.get('FIREBASE_AUTH_DOMAIN'),
    "projectId": os.environ.get('FIREBASE_PROJECT_ID'),
    "storageBucket": os.environ.get('FIREBASE_STORAGE_BUCKET'),
    "messagingSenderId": os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
    "appId": os.environ.get('FIREBASE_APP_ID'),
    "measurementId": os.environ.get('FIREBASE_MEASUREMENT_ID')
}

# Initialize Firebase Admin SDK using service account credentials
db: Optional[firestore.Client] = None

def initialize_firebase():
    global db
    if db is not None:
        return db

    try:
        if firebase_admin._apps:
            db = firestore.client()
            print("✅ Firebase Firestore client ready (existing app)")
            return db

        # Check if all required environment variables are present
        required_vars = ['FIREBASE_PROJECT_ID', 'FIREBASE_API_KEY', 'FIREBASE_AUTH_DOMAIN']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            raise RuntimeError(f"Missing required Firebase environment variables: {missing_vars}")

        # Initialize Firebase Admin SDK with default credentials
        # This will use the environment variables for authentication
        firebase_admin.initialize_app()
        db = firestore.client()
        print("✅ Firebase Firestore client ready (environment variables)")
        return db

    except Exception as e:
        print(f"❌ Firebase init failed: {e}")
        return None

# Initialize on import
db = initialize_firebase()

FACES_COLLECTION = 'faces'


def save_face_embedding(user_id: str, photo_ref: str, embedding: np.ndarray) -> bool:
    """Persist a face embedding for a photo reference under a user."""
    try:
        if db is None:
            print(f"⚠️ No Firebase client; simulate save for {photo_ref}")
            return True
        
        # Convert numpy array to list for Firestore
        embedding_list = embedding.tolist()
        
        # Create document data
        doc_data = {
            'user_id': user_id,
            'photo_reference': photo_ref,
            'face_embedding': embedding_list,
            'embedding_dimension': len(embedding_list),
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        # Save to Firestore
        doc_ref = db.collection(FACES_COLLECTION).add(doc_data)
        print(f"✅ Saved face embedding for {photo_ref} (doc ID: {doc_ref[1].id})")
        return True
        
    except Exception as e:
        print(f"❌ save_face_embedding error: {e}")
        return False


def fetch_embeddings_for_user(user_id: str) -> List[Dict[str, Any]]:
    """Fetch all face records for a user."""
    try:
        if db is None:
            print(f"⚠️ No Firebase client; return empty list for {user_id}")
            return []
        
        # Query Firestore for user's face embeddings
        docs = db.collection(FACES_COLLECTION).where('user_id', '==', user_id).stream()
        
        results = []
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id  # Add document ID
            results.append(doc_data)
        
        print(f"✅ Fetched {len(results)} face embeddings for user {user_id}")
        return results
        
    except Exception as e:
        print(f"❌ fetch_embeddings_for_user error: {e}")
        return []


def delete_user_face(user_id: str, face_id: str) -> bool:
    """Delete a single face row by id ensuring ownership."""
    try:
        if db is None:
            print(f"⚠️ No Firebase client; simulate delete {face_id}")
            return True
        
        # Get the document and verify ownership
        doc_ref = db.collection(FACES_COLLECTION).document(face_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            print(f"⚠️ Document {face_id} not found")
            return False
        
        doc_data = doc.to_dict()
        if doc_data.get('user_id') != user_id:
            print(f"⚠️ Document {face_id} does not belong to user {user_id}")
            return False
        
        # Delete the document
        doc_ref.delete()
        print(f"✅ Deleted face embedding {face_id}")
        return True
        
    except Exception as e:
        print(f"❌ delete_user_face error: {e}")
        return False


def clear_all_faces() -> bool:
    """Clear all face embeddings from Firestore."""
    try:
        if db is None:
            print("⚠️ No Firebase client; cannot clear faces")
            return False
        
        # Get all documents in the collection
        docs = db.collection(FACES_COLLECTION).stream()
        
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
        
        print(f"✅ Cleared {deleted_count} face embeddings from Firebase")
        return True
        
    except Exception as e:
        print(f"❌ clear_all_faces error: {e}")
        return False


def get_firebase_stats() -> Dict[str, Any]:
    """Get Firebase collection statistics."""
    try:
        if db is None:
            return {"error": "No Firebase client"}
        
        # Count total documents
        docs = db.collection(FACES_COLLECTION).stream()
        total_docs = sum(1 for _ in docs)
        
        # Count by user
        user_counts = {}
        docs = db.collection(FACES_COLLECTION).stream()
        for doc in docs:
            user_id = doc.to_dict().get('user_id', 'unknown')
            user_counts[user_id] = user_counts.get(user_id, 0) + 1
        
        return {
            "total_faces": total_docs,
            "users": user_counts,
            "collection": FACES_COLLECTION
        }
        
    except Exception as e:
        return {"error": str(e)}
