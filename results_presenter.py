"""
results_presenter.py - Helpers to prepare thumbnails and ZIP downloads for matches
"""
from typing import List
import os
import zipfile
from datetime import datetime

IMAGE_ROOT = "test_photos"  # fallback root for looking up originals by photo_reference


def resolve_photo_paths(photo_refs: List[str]) -> List[str]:
	"""Resolve photo_reference names into local paths if available."""
	paths = []
	for name in photo_refs:
		candidate = name
		if not os.path.isabs(candidate):
			candidate = os.path.join(IMAGE_ROOT, name)
		if os.path.exists(candidate):
			paths.append(candidate)
	return paths


def build_zip(output_basename: str, file_paths: List[str]) -> str:
	"""Create a ZIP archive with given files; return the zip path."""
	if not file_paths:
		raise ValueError("No files to zip")
	zip_name = f"{output_basename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
	with zipfile.ZipFile(zip_name, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
		for p in file_paths:
			if os.path.exists(p):
				zf.write(p, os.path.basename(p))
	return zip_name

