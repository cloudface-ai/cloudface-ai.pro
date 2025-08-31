"""
supabase_store.py - Save and query face embeddings and metadata in Supabase.
"""
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
import numpy as np

# Load environment variables from example.env (dev/local)
load_dotenv('example.env')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
	try:
		supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
		print("✅ Supabase client ready (supabase_store)")
	except Exception as e:
		print(f"⚠️  Supabase init failed in supabase_store: {e}")
else:
	print("⚠️  Supabase credentials not found in env (supabase_store)")

FACES_TABLE = 'faces'


def save_face_embedding(user_id: str, photo_ref: str, embedding: np.ndarray) -> bool:
	"""Persist a face embedding for a photo reference under a user."""
	try:
		if supabase is None:
			print(f"⚠️  No Supabase client; simulate save for {photo_ref}")
			return True
		payload = {
			'user_id': user_id,
			'photo_reference': photo_ref,
			'face_embedding': embedding.tolist(),
		}
		res = supabase.table(FACES_TABLE).insert(payload).execute()
		return bool(res.data)
	except Exception as e:
		print(f"❌ save_face_embedding error: {e}")
		return False


def fetch_embeddings_for_user(user_id: str) -> List[Dict[str, Any]]:
	"""Fetch all face records for a user."""
	try:
		if supabase is None:
			print(f"⚠️  No Supabase client; return empty list for {user_id}")
			return []
		res = supabase.table(FACES_TABLE).select('*').eq('user_id', user_id).execute()
		return res.data or []
	except Exception as e:
		print(f"❌ fetch_embeddings_for_user error: {e}")
		return []


def delete_user_face(user_id: str, face_id: str) -> bool:
	"""Delete a single face row by id ensuring ownership."""
	try:
		if supabase is None:
			print(f"⚠️  No Supabase client; simulate delete {face_id}")
			return True
		res = supabase.table(FACES_TABLE).delete().eq('id', face_id).eq('user_id', user_id).execute()
		return bool(res.data)
	except Exception as e:
		print(f"❌ delete_user_face error: {e}")
		return False

