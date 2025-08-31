"""
embedding_engine.py - Face detection and embedding utilities.
Prefers face_recognition; falls back to simple color-histogram embedding if unavailable.
"""
from typing import List, Tuple, Optional
import numpy as np

# Try to import face_recognition for real embeddings
try:
	import face_recognition  # type: ignore
	_HAS_FR = True
except Exception:
	_HAS_FR = False

try:
	from PIL import Image
except Exception:
	Image = None  # type: ignore


def embed_image_file(path: str) -> List[np.ndarray]:
	"""Return a list of face embeddings for all faces in the image file."""
	if _HAS_FR:
		image = face_recognition.load_image_file(path)
		face_locations = face_recognition.face_locations(image)
		if not face_locations:
			return []
		encodings = face_recognition.face_encodings(image, face_locations)
		return [np.array(e, dtype=np.float32) for e in encodings]
	# Fallback: produce a coarse embedding from image histogram
	return _fallback_histogram_embedding(path)


def embed_image_bytes(data: bytes) -> List[np.ndarray]:
	"""Return a list of face embeddings from raw image bytes."""
	if _HAS_FR:
		import io
		# Convert bytes to numpy array using PIL first
		img = Image.open(io.BytesIO(data))
		image = np.array(img)
		face_locations = face_recognition.face_locations(image)
		if not face_locations:
			return []
		encodings = face_recognition.face_encodings(image, face_locations)
		return [np.array(e, dtype=np.float32) for e in encodings]
	# Fallback
	if Image is None:
		return []
	return _fallback_histogram_embedding_bytes(data)


def compare_embeddings(a: np.ndarray, b: np.ndarray) -> float:
	"""Return Euclidean distance (lower is more similar)."""
	return float(np.linalg.norm(a - b))


def _fallback_histogram_embedding(path: str) -> List[np.ndarray]:
	if Image is None:
		return []
	img = Image.open(path).convert('RGB').resize((64, 64))
	arr = np.array(img)
	# Simple color histogram embedding
	hist = np.concatenate([
		np.histogram(arr[:, :, c], bins=32, range=(0, 255))[0] for c in range(3)
	]).astype(np.float32)
	# Normalize
	norm = np.linalg.norm(hist) or 1.0
	hist /= norm
	return [hist]


def _fallback_histogram_embedding_bytes(data: bytes) -> List[np.ndarray]:
	if Image is None:
		return []
	from io import BytesIO
	img = Image.open(BytesIO(data)).convert('RGB').resize((64, 64))
	arr = np.array(img)
	hist = np.concatenate([
		np.histogram(arr[:, :, c], bins=32, range=(0, 255))[0] for c in range(3)
	]).astype(np.float32)
	norm = np.linalg.norm(hist) or 1.0
	hist /= norm
	return [hist]

