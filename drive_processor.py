"""
drive_processor.py - Validate Google Drive URLs and download photos/folders.
Requires a valid Google OAuth access token (user already authenticated).
"""
from typing import Tuple, List
import re
import os
import requests
from local_cache import save_bytes_to_cache, get_user_cache_dir, file_exists_in_cache, get_cached_file_path
import pillow_heif
from PIL import Image
import io

# Try to import rawpy for RAW format support
try:
    import rawpy
    RAWPY_AVAILABLE = True
except ImportError:
    RAWPY_AVAILABLE = False
    print("⚠️ rawpy not available - RAW files will be saved as-is")

# Basic validators for Google Drive URLs - More flexible patterns
_DRIVE_FILE_RE = re.compile(r"https?://drive\.google\.com/file/d/([\w-]+)")
_DRIVE_FOLDER_RE = re.compile(r"https?://drive\.google\.com/drive/folders/([\w-]+)")
# Additional patterns for various Google Drive URL formats
_DRIVE_SHARED_RE = re.compile(r"https?://drive\.google\.com/drive/u/\d+/folders/([\w-]+)")
_DRIVE_VIEW_RE = re.compile(r"https?://drive\.google\.com/open\?id=([\w-]+)")
_DRIVE_SHORT_RE = re.compile(r"https?://drive\.google\.com/([\w-]+)")
# More flexible patterns for different URL formats
_DRIVE_FOLDER_ALT1 = re.compile(r"https?://drive\.google\.com/drive/folders/([^/?]+)")
_DRIVE_FOLDER_ALT2 = re.compile(r"https?://drive\.google\.com/drive/folders/([^/?&\s]+)")
_DRIVE_FOLDER_ALT3 = re.compile(r"https?://drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)")


def validate_drive_url(url: str) -> Tuple[bool, str, str]:
	"""Validate a Drive URL. Returns (is_valid, type, id) where type is 'file' or 'folder'."""
	if not url:
		return False, "empty", ""
	
	print(f"🔍 Validating URL: {url}")
	
	# Try all patterns in order of specificity
	m = _DRIVE_FILE_RE.match(url)
	if m:
		print(f"✅ Matched as FILE with ID: {m.group(1)}")
		return True, "file", m.group(1)
	
	m = _DRIVE_FOLDER_RE.match(url)
	if m:
		print(f"✅ Matched as FOLDER with ID: {m.group(1)}")
		return True, "folder", m.group(1)
	
	m = _DRIVE_SHARED_RE.match(url)
	if m:
		print(f"✅ Matched as SHARED FOLDER with ID: {m.group(1)}")
		return True, "folder", m.group(1)
	
	m = _DRIVE_VIEW_RE.match(url)
	if m:
		print(f"✅ Matched as VIEW FOLDER with ID: {m.group(1)}")
		return True, "folder", m.group(1)
	
	m = _DRIVE_SHORT_RE.match(url)
	if m:
		print(f"✅ Matched as SHORT FOLDER with ID: {m.group(1)}")
		return True, "folder", m.group(1)
	
	# Try more flexible patterns
	m = _DRIVE_FOLDER_ALT1.match(url)
	if m:
		print(f"✅ Matched as ALT1 FOLDER with ID: {m.group(1)}")
		return True, "folder", m.group(1)
	
	m = _DRIVE_FOLDER_ALT2.match(url)
	if m:
		print(f"✅ Matched as ALT2 FOLDER with ID: {m.group(1)}")
		return True, "folder", m.group(1)
	
	m = _DRIVE_FOLDER_ALT3.match(url)
	if m:
		print(f"✅ Matched as ALT3 FOLDER with ID: {m.group(1)}")
		return True, "folder", m.group(1)
	
	# If no pattern matches, try to extract ID manually
	print(f"❌ No regex pattern matched, trying manual extraction...")
	
	# Look for folder ID in common patterns
	if "folders/" in url:
		parts = url.split("folders/")
		if len(parts) > 1:
			folder_id = parts[1].split("?")[0].split("&")[0].split("/")[0]
			if folder_id and len(folder_id) > 10:  # Google Drive IDs are usually long
				print(f"✅ Manually extracted FOLDER ID: {folder_id}")
				return True, "folder", folder_id
	
	# Look for any long alphanumeric string that might be an ID
	import re
	potential_ids = re.findall(r'[a-zA-Z0-9_-]{20,}', url)
	if potential_ids:
		for potential_id in potential_ids:
			if len(potential_id) >= 20:  # Google Drive IDs are usually 20+ characters
				print(f"✅ Found potential ID: {potential_id}")
				return True, "folder", potential_id
	
	print(f"❌ Could not extract valid Drive ID from URL")
	return False, "invalid", ""


def _headers(access_token: str) -> dict:
	return {"Authorization": f"Bearer {access_token}"}


def download_drive_file(user_id: str, folder_id: str, file_id: str, access_token: str, force_redownload: bool = False) -> str:
	"""Download a single Drive file (image) and cache it. Returns local path."""
	# Get metadata to derive filename
	meta_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=id,name,mimeType"
	r = requests.get(meta_url, headers=_headers(access_token))
	r.raise_for_status()
	meta = r.json()
	name = meta.get("name", f"{file_id}.bin")
	
	# Check if file already exists in cache
	if not force_redownload and file_exists_in_cache(user_id, folder_id, name):
		print(f"✅ File already cached: {name}")
		return get_cached_file_path(user_id, folder_id, name)
	
	# Download content
	dl_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
	r = requests.get(dl_url, headers=_headers(access_token), stream=True)
	r.raise_for_status()
	content = r.content
	
	# Convert HEIC or RAW camera formats to JPG if needed
	converted_content, converted_name = _convert_heic_if_needed(content, name)
	
	return save_bytes_to_cache(user_id, folder_id, converted_name, converted_content)


def list_folder_files(folder_id: str, access_token: str) -> List[dict]:
	"""List files in a Drive folder (images only)."""
	q = f"'{folder_id}' in parents and trashed=false"
	fields = "files(id,name,mimeType),nextPageToken"
	url = f"https://www.googleapis.com/drive/v3/files?q={requests.utils.quote(q)}&fields={fields}&pageSize=1000"
	files = []
	page_token = None
	while True:
		u = url
		if page_token:
			u += f"&pageToken={page_token}"
		r = requests.get(u, headers=_headers(access_token))
		r.raise_for_status()
		data = r.json()
		for f in data.get("files", []):
			mt = f.get("mimeType", "")
			if mt.startswith("image/"):
				files.append(f)
		page_token = data.get("nextPageToken")
		if not page_token:
			break
	return files


def download_drive_folder(user_id: str, folder_id: str, access_token: str, force_redownload: bool = False) -> List[str]:
	"""Download all image files from a Drive folder; returns local paths."""
	print(f"📂 Listing files in Google Drive folder...")
	files = list_folder_files(folder_id, access_token)
	print(f"📋 Found {len(files)} image files in folder")
	
	# Check which files are already cached
	cached_files = []
	new_files = []
	
	for f in files:
		filename = f.get('name', 'Unknown')
		if file_exists_in_cache(user_id, folder_id, filename):
			cached_files.append(f)
		else:
			new_files.append(f)
	
	print(f"📦 Already cached: {len(cached_files)} files")
	print(f"🆕 Need to download: {len(new_files)} files")
	
	paths = []
	
	# Add already cached files to paths
	for f in cached_files:
		filename = f.get('name', 'Unknown')
		cached_path = get_cached_file_path(user_id, folder_id, filename)
		if cached_path:
			paths.append(cached_path)
			print(f"✅ Using cached: {filename}")
	
	# Download new files
	for i, f in enumerate(new_files, 1):
		try:
			print(f"  [{i}/{len(new_files)}] Downloading: {f.get('name', 'Unknown')}")
			p = download_drive_file(user_id, folder_id, f["id"], access_token, force_redownload)
			paths.append(p)
			print(f"     ✅ Downloaded to: {p}")
		except Exception as e:
			print(f"     ❌ Failed to download {f.get('name')} ({f.get('id')}): {e}")
	
	print(f"📥 Folder processing complete: {len(paths)}/{len(files)} files available")
	return paths


def _convert_heic_if_needed(content: bytes, filename: str) -> Tuple[bytes, str]:
	"""Convert HEIC or RAW camera formats to JPG if needed. Returns (converted_content, converted_filename)."""
	try:
		# Check if file is HEIC or RAW by extension
		lower_filename = filename.lower()
		is_heic = lower_filename.endswith(('.heic', '.heif')) or lower_filename.endswith(('.HEIC', '.HEIF'))
		is_raw = lower_filename.endswith(('.arw', '.cr2', '.cr3', '.nef', '.raf', '.orf', '.dng', '.rw2', '.pef', '.srw', '.kdc', '.dcr', '.mos', '.mrw', '.bay', '.erf', '.mef', '.raw', '.3fr', '.fff', '.hdr', '.x3f'))
		
		if is_heic or is_raw:
			format_type = "HEIC" if is_heic else "RAW"
			print(f"🔄 Converting {format_type} to JPG: {filename}")
			
			if is_heic:
				# Open HEIC image using pillow_heif
				heif_file = pillow_heif.read_heif(content)
				image = Image.frombytes(
					heif_file.mode, 
					heif_file.size, 
					heif_file.data,
					"raw",
					heif_file.mode,
					heif_file.stride,
				)
			elif is_raw and RAWPY_AVAILABLE:
				# Open RAW image using rawpy for proper RAW format support
				with rawpy.imread(io.BytesIO(content)) as raw:
					# Process RAW with default settings
					rgb = raw.postprocess(use_camera_wb=True, half_size=False, no_auto_bright=False, output_bps=8)
					image = Image.fromarray(rgb)
			elif is_raw and not RAWPY_AVAILABLE:
				# RAW conversion not available
				print(f"⚠️ RAW conversion not available (rawpy not installed) - saving {filename} as-is")
				return content, filename
			else:
				# Fallback for other formats
				image = Image.open(io.BytesIO(content))
			
			# Convert to RGB if needed (RAW/HEIC might be in different color spaces)
			if image.mode in ('RGBA', 'LA', 'P', 'CMYK', 'LAB', 'HSV', 'YCbCr'):
				image = image.convert('RGB')
			
			# Save as JPG to bytes
			output_buffer = io.BytesIO()
			image.save(output_buffer, format='JPEG', quality=95, optimize=True)
			converted_content = output_buffer.getvalue()
			
			# Update filename from original extension to .jpg
			converted_name = os.path.splitext(filename)[0] + '.jpg'
			
			print(f"✅ Converted {filename} to {converted_name}")
			return converted_content, converted_name
		
		# Not HEIC or RAW, return original content and filename
		return content, filename
		
	except Exception as e:
		print(f"⚠️ {format_type if 'format_type' in locals() else 'Image'} conversion failed for {filename}: {e}")
		print(f"   Saving original file as-is")
		# If conversion fails, return original content and filename
		return content, filename
