"""
local_cache.py - Abstraction for local/browser cache of downloaded photos and thumbnails.
- Desktop: uses filesystem under storage/data
- Web: provides in-memory stubs (to be expanded if needed)
"""
import os
import io
import shutil
import json
import pickle
from typing import Optional, Tuple, List, Dict, Any

BASE_STORAGE_DIR = os.path.join("storage", "data")
TEMP_DIR = os.path.join("storage", "temp")
EMBEDDING_CACHE_DIR = os.path.join("storage", "embeddings")

os.makedirs(BASE_STORAGE_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(EMBEDDING_CACHE_DIR, exist_ok=True)

def get_user_cache_dir(user_id: str, folder_id: str) -> str:
	"""Return the directory path for a user's cached folder."""
	safe_user = user_id.replace("/", "_")
	safe_folder = folder_id.replace("/", "_")
	cache_dir = os.path.join(BASE_STORAGE_DIR, safe_user, safe_folder)
	os.makedirs(cache_dir, exist_ok=True)
	return cache_dir

def get_user_embedding_cache_dir(user_id: str) -> str:
	"""Return the directory path for a user's embedding cache."""
	safe_user = user_id.replace("/", "_")
	embedding_dir = os.path.join(EMBEDDING_CACHE_DIR, safe_user)
	os.makedirs(embedding_dir, exist_ok=True)
	return embedding_dir

def save_bytes_to_cache(user_id: str, folder_id: str, filename: str, data: bytes) -> str:
	"""Save binary data to the user's cache and return absolute file path."""
	cache_dir = get_user_cache_dir(user_id, folder_id)
	target_path = os.path.join(cache_dir, filename)
	with open(target_path, "wb") as f:
		f.write(data)
	return target_path

def copy_file_to_cache(user_id: str, folder_id: str, source_path: str, target_name: Optional[str] = None) -> str:
	"""Copy an existing local file into the user's cache; returns new path."""
	cache_dir = get_user_cache_dir(user_id, folder_id)
	if not target_name:
		target_name = os.path.basename(source_path)
	target_path = os.path.join(cache_dir, target_name)
	shutil.copy2(source_path, target_path)
	return target_path

def list_cached_images(user_id: str, folder_id: str) -> list:
	"""List cached image file paths for the user and folder."""
	cache_dir = get_user_cache_dir(user_id, folder_id)
	if not os.path.isdir(cache_dir):
		return []
	return [os.path.join(cache_dir, f) for f in os.listdir(cache_dir) if _is_image_file(f)]

def file_exists_in_cache(user_id: str, folder_id: str, filename: str) -> bool:
	"""Check if a specific file already exists in the user's cache."""
	cache_dir = get_user_cache_dir(user_id, folder_id)
	file_path = os.path.join(cache_dir, filename)
	
	if os.path.exists(file_path):
		return True
	
	# Check if this is a HEIC/RAW file that was converted to JPG
	base_name = os.path.splitext(filename)[0]
	converted_jpg = f"{base_name}.jpg"
	converted_path = os.path.join(cache_dir, converted_jpg)
	
	return os.path.exists(converted_path)

def get_cached_file_path(user_id: str, folder_id: str, filename: str) -> Optional[str]:
	"""Get the full path of a cached file if it exists, None otherwise."""
	cache_dir = get_user_cache_dir(user_id, folder_id)
	
	# First check if the original file exists
	file_path = os.path.join(cache_dir, filename)
	if os.path.exists(file_path):
		# If this is a HEIC/RAW file, check if there's a converted JPG version
		lower_filename = filename.lower()
		is_heic = lower_filename.endswith(('.heic', '.heif')) or lower_filename.endswith(('.HEIC', '.HEIF'))
		is_raw = lower_filename.endswith(('.arw', '.cr2', '.cr3', '.nef', '.raf', '.orf', '.dng', '.rw2', '.pef', '.srw', '.kdc', '.dcr', '.mos', '.mrw', '.bay', '.erf', '.mef', '.raw', '.3fr', '.fff', '.hdr', '.x3f'))
		
		if is_heic or is_raw:
			# Look for converted JPG version
			base_name = os.path.splitext(filename)[0]
			converted_jpg = f"{base_name}.jpg"
			converted_path = os.path.join(cache_dir, converted_jpg)
			
			if os.path.exists(converted_path):
				print(f"🔄 Using converted JPG for {filename}: {converted_jpg}")
				return converted_path
			else:
				print(f"⚠️ HEIC/RAW file {filename} exists but no converted JPG found")
				return file_path
		else:
			# Not HEIC/RAW, return original
			return file_path
	
	# Check if this is a HEIC/RAW file that was converted to JPG
	base_name = os.path.splitext(filename)[0]
	converted_jpg = f"{base_name}.jpg"
	converted_path = os.path.join(cache_dir, converted_jpg)
	
	if os.path.exists(converted_path):
		print(f"🔄 Found converted JPG for {filename}: {converted_jpg}")
		return converted_path
	
	return None

def save_embedding_to_cache(user_id: str, photo_ref: str, embedding_data: Any) -> str:
	"""Save face embedding data to local cache for faster access."""
	embedding_dir = get_user_embedding_cache_dir(user_id)
	# Use photo_ref as filename (sanitized)
	safe_filename = photo_ref.replace("/", "_").replace("\\", "_")
	embedding_path = os.path.join(embedding_dir, f"{safe_filename}.pkl")
	
	with open(embedding_path, "wb") as f:
		pickle.dump(embedding_data, f)
	
	return embedding_path

def load_embedding_from_cache(user_id: str, photo_ref: str) -> Optional[Any]:
	"""Load face embedding data from local cache if it exists."""
	embedding_dir = get_user_embedding_cache_dir(user_id)
	# Handle both full paths and filenames
	if os.path.sep in photo_ref:
		# Full path provided, extract filename
		photo_ref = os.path.basename(photo_ref)
	
	safe_filename = photo_ref.replace("/", "_").replace("\\", "_")
	embedding_path = os.path.join(embedding_dir, f"{safe_filename}.pkl")
	
	if os.path.exists(embedding_path):
		try:
			with open(embedding_path, "rb") as f:
				return pickle.load(f)
		except Exception as e:
			print(f"⚠️ Failed to load cached embedding for {photo_ref}: {e}")
			return None
	return None

def embedding_exists_in_cache(user_id: str, photo_ref: str) -> bool:
	"""Check if a face embedding already exists in local cache."""
	embedding_dir = get_user_embedding_cache_dir(user_id)
	# Handle both full paths and filenames
	if os.path.sep in photo_ref:
		# Full path provided, extract filename
		photo_ref = os.path.basename(photo_ref)
	
	safe_filename = photo_ref.replace("/", "_").replace("\\", "_")
	embedding_path = os.path.join(embedding_dir, f"{safe_filename}.pkl")
	return os.path.exists(embedding_path)

def list_cached_embeddings(user_id: str) -> List[str]:
	"""List all photo references that have cached embeddings."""
	embedding_dir = get_user_embedding_cache_dir(user_id)
	if not os.path.isdir(embedding_dir):
		return []
	
	embeddings = []
	for filename in os.listdir(embedding_dir):
		if filename.endswith('.pkl'):
			# Remove .pkl extension to get original filename
			photo_ref = filename[:-4]
			embeddings.append(photo_ref)
	
	return embeddings

def get_cache_stats(user_id: str) -> Dict[str, Any]:
	"""Get statistics about user's cache usage."""
	stats = {
		'photos_count': 0,
		'embeddings_count': 0,
		'total_photo_size': 0,
		'total_embedding_size': 0
	}
	
	# Count photos in all user folders
	user_base_dir = os.path.join(BASE_STORAGE_DIR, user_id.replace("/", "_"))
	if os.path.exists(user_base_dir):
		for folder_name in os.listdir(user_base_dir):
			folder_path = os.path.join(user_base_dir, folder_name)
			if os.path.isdir(folder_path):
				for filename in os.listdir(folder_path):
					if _is_image_file(filename):
						file_path = os.path.join(folder_path, filename)
						stats['photos_count'] += 1
						try:
							stats['total_photo_size'] += os.path.getsize(file_path)
						except:
							pass
	
	# Count embeddings
	embedding_dir = get_user_embedding_cache_dir(user_id)
	if os.path.exists(embedding_dir):
		for filename in os.listdir(embedding_dir):
			if filename.endswith('.pkl'):
				file_path = os.path.join(embedding_dir, filename)
				stats['embeddings_count'] += 1
				try:
					stats['total_embedding_size'] += os.path.getsize(file_path)
				except:
					pass
	
	return stats

def _is_image_file(name: str) -> bool:
	lower = name.lower()
	return lower.endswith((".jpg", ".jpeg", ".png", ".webp"))

def get_temp_file_path(name_hint: str) -> str:
	"""Create a path in temp folder for transient operations."""
	safe = name_hint.replace("/", "_")
	return os.path.join(TEMP_DIR, safe)

def ensure_dirs():
	"""Ensure base directories exist (idempotent)."""
	os.makedirs(BASE_STORAGE_DIR, exist_ok=True)
	os.makedirs(TEMP_DIR, exist_ok=True)
	os.makedirs(EMBEDDING_CACHE_DIR, exist_ok=True)

# Web stubs (to be enhanced if we add true browser cache integration)
class InMemoryBlobStore:
	"""Simple in-memory blob store for web fallback."""
	def __init__(self) -> None:
		self._store = {}
	def put(self, key: str, data: bytes) -> None:
		self._store[key] = data
	def get(self, key: str) -> Optional[bytes]:
		return self._store.get(key)
	def delete(self, key: str) -> None:
		self._store.pop(key, None)

in_memory_store = InMemoryBlobStore()

