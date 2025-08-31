"""
flow_controller.py - Orchestrates Drive download, embedding, Supabase storage, and search
"""
from typing import List, Tuple, Dict, Any
import os

from drive_processor import validate_drive_url, download_drive_folder, download_drive_file
from embedding_engine import embed_image_file
from supabase_store import save_face_embedding
from selfie_handler import process_selfies
from search_engine import rank_matches_for_user
from local_cache import embedding_exists_in_cache, load_embedding_from_cache, save_embedding_to_cache


class FlowError(Exception):
	pass


def process_drive_folder_and_store(user_id: str, url: str, access_token: str, force_reprocess: bool = False) -> Dict[str, Any]:
	"""
	Validate URL, download all images, compute embeddings for each face, and store in Supabase.
	Returns summary: { downloaded_count, embedded_count, skipped_count, total_count }
	"""
	print(f"🔍 Processing Google Drive URL: {url}")
	print(f"👤 User ID: {user_id}")
	
	ok, kind, rid = validate_drive_url(url)
	if not ok:
		print(f"❌ Invalid Google Drive URL: {url}")
		print(f"🔍 URL validation failed - kind: {kind}, rid: {rid}")
		print(f"💡 Make sure you're using a valid Google Drive folder URL")
		print(f"   Example formats:")
		print(f"   - https://drive.google.com/drive/folders/FOLDER_ID")
		print(f"   - https://drive.google.com/drive/u/0/folders/FOLDER_ID")
		print(f"   - https://drive.google.com/open?id=FOLDER_ID")
		raise FlowError(f"Invalid Google Drive URL: {url}")
	
	print(f"✅ URL validated - Type: {kind}, ID: {rid}")
	
	paths: List[str] = []
	if kind == "folder":
		print(f"📁 Downloading folder contents...")
		paths = download_drive_folder(user_id, rid, access_token, force_redownload=force_reprocess)
		print(f"📥 Processed {len(paths)} files")
	elif kind == "file":
		print(f"📄 Downloading single file...")
		# For single files, use the file_id as folder_id to keep them organized
		p = download_drive_file(user_id, rid, rid, access_token, force_redownload=force_reprocess)
		paths = [p]
		print(f"📥 Processed file: {p}")
	else:
		print(f"❌ Unsupported Drive URL type: {kind}")
		raise FlowError(f"Unsupported Drive URL type: {kind}")
	
	print(f"🔄 Processing {len(paths)} photos for face detection...")
	embedded = 0
	skipped = 0
	
	for i, p in enumerate(paths, 1):
		photo_ref = os.path.basename(p)
		print(f"  [{i}/{len(paths)}] Processing: {photo_ref}")
		
		# Skip macOS system files (._ prefix)
		if photo_ref.startswith('._'):
			print(f"     ⚠️ Skipping macOS system file: {photo_ref}")
			skipped += 1
			continue
		
		# Check if embeddings already exist for this photo
		# Use the full path for embedding cache checks, not just the filename
		if not force_reprocess and embedding_exists_in_cache(user_id, p):
			print(f"     ✅ Embeddings already cached for {photo_ref}")
			skipped += 1
			continue
		
		# Process the photo for face detection
		faces = embed_image_file(p)
		print(f"     Found {len(faces)} faces")
		
		if faces:
			# Save embeddings to both local cache and Supabase
			for face_idx, face_embedding in enumerate(faces):
				# Save to local cache first for faster access
				local_cache_path = save_embedding_to_cache(user_id, photo_ref, face_embedding)
				print(f"     💾 Saved to local cache: {local_cache_path}")
				
				# Also save to Supabase for persistence
				if save_face_embedding(user_id, photo_ref, face_embedding):
					embedded += 1
					print(f"     ✅ Saved face embedding {face_idx + 1} for {photo_ref}")
				else:
					print(f"     ❌ Failed to save face embedding {face_idx + 1} for {photo_ref}")
		else:
			print(f"     ⚠️ No faces detected in {photo_ref}")
	
	total_count = len(paths)
	result = {
		"downloaded_count": total_count, 
		"embedded_count": embedded,
		"skipped_count": skipped,
		"total_count": total_count
	}
	
	print(f"🎉 Processing complete!")
	print(f"   📥 Total files: {result['total_count']}")
	print(f"   🔄 New embeddings: {result['embedded_count']}")
	print(f"   ⏭️ Skipped (already processed): {result['skipped_count']}")
	
	return result


def search_with_selfies(user_id: str, selfie_inputs: List[bytes], threshold: float = 0.6) -> List[Dict[str, Any]]:
	"""
	Embed up to 3 selfies from bytes and rank matches against stored embeddings.
	Returns ranked matches: [{ photo_reference, min_distance, which_selfie }]
	"""
	selfie_embeds = process_selfies(selfie_inputs)
	return rank_matches_for_user(user_id, selfie_embeds, threshold)

