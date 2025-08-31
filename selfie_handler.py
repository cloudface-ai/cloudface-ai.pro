"""
selfie_handler.py - Process up to 3 selfie images and produce embeddings.
"""
from typing import List, Union
import numpy as np
from embedding_engine import embed_image_file, embed_image_bytes

ImageInput = Union[str, bytes]


def process_selfies(inputs: List[ImageInput]) -> List[np.ndarray]:
	"""
	Accept up to 3 selfies as file paths or raw bytes, return one embedding per selfie.
	If multiple faces are found, use the first one.
	"""
	embeddings: List[np.ndarray] = []
	for item in inputs[:3]:
		faces = []
		if isinstance(item, bytes):
			faces = embed_image_bytes(item)
		elif isinstance(item, str):
			faces = embed_image_file(item)
		else:
			continue
		if faces:
			embeddings.append(faces[0])
	return embeddings

