# database_handler.py

import os
import numpy as np
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from example.env
load_dotenv('example.env')

# Initialize Supabase client
supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

# Initialize Supabase client (optional for now)
supabase = None
if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized successfully")
    except Exception as e:
        print(f"⚠️  Failed to initialize Supabase client: {e}")
        supabase = None
else:
    print("⚠️  Supabase credentials not found - running in local mode")
    print("   Database operations will be simulated locally")

def add_face(user_id: str, photo_ref: str, embedding: np.ndarray) -> bool:
    """
    Add a face embedding to the database.
    
    Args:
        user_id (str): Unique identifier for the user
        photo_ref (str): Reference to the photo (filename or path)
        embedding (np.ndarray): Face embedding vector
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if Supabase is available
        if not supabase:
            print(f"⚠️  Supabase not available - simulating face save for {photo_ref}")
            print(f"   User: {user_id}, Photo: {photo_ref}")
            return True  # Simulate success
        
        # Convert numpy array to list for JSON serialization
        embedding_list = embedding.tolist()
        
        # Prepare data for insertion
        face_data = {
            'user_id': user_id,
            'photo_reference': photo_ref,
            'face_embedding': embedding_list,
            'created_at': 'now()'  # Supabase will handle timestamp
        }
        
        # Insert into faces table
        result = supabase.table('faces').insert(face_data).execute()
        
        if result.data:
            print(f"✅ Face embedding saved for {photo_ref}")
            return True
        else:
            print(f"❌ Failed to save face embedding for {photo_ref}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving face embedding: {e}")
        return False

def get_faces_by_user(user_id: str) -> list:
    """
    Retrieve all face embeddings for a specific user.
    
    Args:
        user_id (str): Unique identifier for the user
        
    Returns:
        list: List of face records with embeddings
    """
    try:
        # Check if Supabase is available
        if not supabase:
            print(f"⚠️  Supabase not available - returning empty face list for user {user_id}")
            return []
        
        result = supabase.table('faces').select('*').eq('user_id', user_id).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"❌ Error retrieving faces: {e}")
        return []

def find_similar_faces(target_embedding: np.ndarray, user_id: str, threshold: float = 0.6) -> list:
    """
    Find faces similar to the target embedding within a user's collection.
    
    Args:
        target_embedding (np.ndarray): The face embedding to compare against
        user_id (str): User ID to search within
        threshold (float): Similarity threshold (0.6 is default for face recognition)
        
    Returns:
        list: List of similar face records
    """
    try:
        # Get all faces for the user
        user_faces = get_faces_by_user(user_id)
        similar_faces = []
        
        target_list = target_embedding.tolist()
        
        for face_record in user_faces:
            stored_embedding = np.array(face_record['face_embedding'])
            
            # Calculate similarity (lower distance = higher similarity)
            distance = np.linalg.norm(target_embedding - stored_embedding)
            
            if distance <= threshold:
                face_record['similarity_score'] = 1 - (distance / threshold)
                similar_faces.append(face_record)
        
        # Sort by similarity score (highest first)
        similar_faces.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_faces
        
    except Exception as e:
        print(f"❌ Error finding similar faces: {e}")
        return []

def delete_face(face_id: str) -> bool:
    """
    Delete a specific face record from the database.
    
    Args:
        face_id (str): ID of the face record to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        result = supabase.table('faces').delete().eq('id', face_id).execute()
        return bool(result.data)
    except Exception as e:
        print(f"❌ Error deleting face: {e}")
        return False

def create_tables():
    """
    Create the necessary tables in Supabase if they don't exist.
    This function should be run once during setup.
    """
    # Note: In Supabase, tables are typically created through the dashboard
    # This function is provided for reference of the expected schema
    
    table_schema = """
    -- Create faces table
    CREATE TABLE IF NOT EXISTS faces (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id TEXT NOT NULL,
        photo_reference TEXT NOT NULL,
        face_embedding JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create index for faster user_id lookups
    CREATE INDEX IF NOT EXISTS idx_faces_user_id ON faces(user_id);
    
    -- Create index for face embedding similarity searches
    CREATE INDEX IF NOT EXISTS idx_faces_embedding ON faces USING GIN (face_embedding);
    """
    
    print("📋 Table schema for reference:")
    print(table_schema)
    print("⚠️  Please create these tables in your Supabase dashboard.")

# Test function
if __name__ == '__main__':
    print("🔧 Database Handler Test")
    print(f"Supabase URL: {supabase_url}")
    print(f"Supabase Key: {supabase_key[:20]}...")
    
    # Show table creation instructions
    create_tables()
