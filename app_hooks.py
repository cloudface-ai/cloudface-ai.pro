"""
app_hooks.py - Thin adapters callable from UI without importing heavy modules in many places.
Safe to import from main_app.py.
"""
from typing import List, Dict, Any

from flow_controller import process_drive_folder_and_store, search_with_selfies
from results_presenter import resolve_photo_paths, build_zip


def process_drive_url_for_user(user_id: str, drive_url: str, access_token: str) -> Dict[str, Any]:
	"""High-level: download+embed+store. Returns summary with photo_refs and local paths."""
	return process_drive_folder_and_store(user_id, drive_url, access_token)


def search_matches_for_user(user_id: str, selfie_bytes_list: List[bytes], threshold: float = 0.6) -> Dict[str, Any]:
	"""Embed selfies and return ranked matches along with resolved local file paths when available."""
	matches = search_with_selfies(user_id, selfie_bytes_list, threshold)
	photo_refs = [m['photo_reference'] for m in matches]
	paths = resolve_photo_paths(photo_refs)
	return {"matches": matches, "photo_refs": photo_refs, "paths": paths}


def build_zip_from_paths(basename: str, file_paths: List[str]) -> str:
	"""Create a zip of selected files and return the archive path."""
	return build_zip(basename, file_paths)

