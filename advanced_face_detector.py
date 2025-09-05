"""
advanced_face_detector.py - Advanced face detection and embedding with fallback to original system
This module provides enhanced face recognition capabilities while maintaining compatibility
"""

import cv2
import numpy as np
from typing import List, Optional, Tuple
import os

# Try to import advanced libraries, fallback gracefully if not available
try:
    import torch
    from facenet_pytorch import MTCNN, InceptionResnetV1
    _HAS_ADVANCED_MODELS = True
    print("✅ Advanced face recognition models available")
except ImportError:
    _HAS_ADVANCED_MODELS = False
    print("⚠️ Advanced models not available, using fallback")

try:
    from sklearn.preprocessing import normalize
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False

class AdvancedFaceDetector:
    """
    Advanced face detector with fallback to original system
    """
    
    def __init__(self):
        if _HAS_ADVANCED_MODELS:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = 'cpu'
        self.mtcnn = None
        self.facenet = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize advanced models if available"""
        if not _HAS_ADVANCED_MODELS:
            print("⚠️ Using fallback face detection")
            return
        
        try:
            # Initialize MTCNN for better face detection
            self.mtcnn = MTCNN(
                image_size=160,
                margin=0,
                min_face_size=20,
                thresholds=[0.6, 0.7, 0.7],  # More sensitive detection
                factor=0.709,
                post_process=True,
                device=self.device
            )
            
            # Initialize FaceNet for better embeddings
            self.facenet = InceptionResnetV1(pretrained='vggface2').eval()
            if self.device == 'cuda':
                self.facenet = self.facenet.cuda()
            
            print(f"✅ Advanced models initialized on {self.device}")
            
        except Exception as e:
            print(f"⚠️ Failed to initialize advanced models: {e}")
            self.mtcnn = None
            self.facenet = None
    
    def detect_faces_advanced(self, image_path: str) -> List[np.ndarray]:
        """
        Advanced face detection with fallback to original system
        Returns list of face embeddings
        """
        if not self.mtcnn or not self.facenet:
            # Fallback to original system
            return self._fallback_detection(image_path)
        
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                print(f"⚠️ Could not load image: {image_path}")
                return []
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect faces with MTCNN
            boxes, probs, landmarks = self.mtcnn.detect(img_rgb, landmarks=True)
            
            if boxes is None or len(boxes) == 0:
                print(f"⚠️ No faces detected in {image_path}")
                return []
            
            # Extract face crops and generate embeddings
            embeddings = []
            for i, box in enumerate(boxes):
                if probs[i] > 0.9:  # High confidence threshold
                    x1, y1, x2, y2 = box.astype(int)
                    
                    # Ensure valid face crop
                    if x2 <= x1 or y2 <= y1 or x1 < 0 or y1 < 0:
                        continue
                        
                    face = img_rgb[y1:y2, x1:x2]
                    
                    # Check if face crop is valid
                    if face.size == 0 or face.shape[0] < 10 or face.shape[1] < 10:
                        continue
                    
                    try:
                        # Generate embedding with FaceNet
                        face_tensor = self.mtcnn(face)
                        if face_tensor is not None and face_tensor.numel() > 0:
                            with torch.no_grad():
                                embedding = self.facenet(face_tensor.unsqueeze(0))
                                embedding = embedding.cpu().numpy().flatten()
                                
                                # Normalize embedding
                                if _HAS_SKLEARN:
                                    embedding = normalize(embedding.reshape(1, -1)).flatten()
                                
                                embeddings.append(embedding.astype(np.float32))
                    except Exception as e:
                        print(f"⚠️ Face processing failed for face {i}: {e}")
                        continue
            
            print(f"✅ Detected {len(embeddings)} faces with advanced model")
            return embeddings
            
        except Exception as e:
            print(f"⚠️ Advanced detection failed: {e}, falling back to 512D system")
            return self._fallback_512d_detection(image_path)
    
    def _fallback_detection(self, image_path: str) -> List[np.ndarray]:
        """Fallback to original face_recognition system"""
        try:
            import face_recognition
            image = face_recognition.load_image_file(image_path)
            embeddings = face_recognition.face_encodings(image)
            print(f"✅ Fallback detected {len(embeddings)} faces")
            return [np.array(emb, dtype=np.float32) for emb in embeddings]
        except Exception as e:
            print(f"❌ Fallback detection failed: {e}")
            return []
    
    def _fallback_512d_detection(self, image_path: str) -> List[np.ndarray]:
        """Fallback that produces 512D embeddings"""
        try:
            import face_recognition
            image = face_recognition.load_image_file(image_path)
            embeddings = face_recognition.face_encodings(image)
            
            if not embeddings:
                return []
            
            # Convert 128D to 512D by padding with zeros
            converted_embeddings = []
            for emb in embeddings:
                if len(emb) == 128:
                    # Pad 128D to 512D
                    padded_emb = np.pad(emb, (0, 384), mode='constant', constant_values=0)
                    converted_embeddings.append(padded_emb.astype(np.float32))
                elif len(emb) == 512:
                    # Already 512D
                    converted_embeddings.append(emb.astype(np.float32))
                else:
                    # Unknown dimension, skip
                    print(f"⚠️ Unknown embedding dimension: {len(emb)}")
                    continue
            
            print(f"✅ 512D fallback detected {len(converted_embeddings)} faces")
            return converted_embeddings
            
        except Exception as e:
            print(f"❌ 512D fallback detection failed: {e}")
            return []
    
    def compare_embeddings_advanced(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Advanced embedding comparison with cosine similarity
        """
        try:
            # Normalize embeddings
            if _HAS_SKLEARN:
                emb1_norm = normalize(embedding1.reshape(1, -1)).flatten()
                emb2_norm = normalize(embedding2.reshape(1, -1)).flatten()
            else:
                emb1_norm = embedding1 / np.linalg.norm(embedding1)
                emb2_norm = embedding2 / np.linalg.norm(embedding2)
            
            # Cosine similarity (higher is more similar)
            similarity = np.dot(emb1_norm, emb2_norm)
            
            # Convert to distance (lower is more similar)
            distance = 1 - similarity
            return float(distance)
            
        except Exception as e:
            print(f"⚠️ Advanced comparison failed: {e}")
            # Fallback to Euclidean distance
            return float(np.linalg.norm(embedding1 - embedding2))

# Global instance for easy access
advanced_detector = AdvancedFaceDetector()

def get_advanced_face_embeddings(image_path: str) -> List[np.ndarray]:
    """
    Get face embeddings using advanced detection with fallback
    This function can be used as a drop-in replacement
    """
    return advanced_detector.detect_faces_advanced(image_path)

def compare_embeddings_advanced(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compare embeddings using advanced method with fallback
    """
    return advanced_detector.compare_embeddings_advanced(embedding1, embedding2)

# Test function
def test_advanced_detection():
    """Test the advanced detection system"""
    print("🧪 Testing Advanced Face Detection...")
    
    # Test with sample images if available
    test_images = []
    if os.path.exists('storage/data'):
        for root, dirs, files in os.walk('storage/data'):
            for file in files[:3]:  # Test first 3 images
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_images.append(os.path.join(root, file))
                    break
            if test_images:
                break
    
    if not test_images:
        print("⚠️ No test images found")
        return
    
    for img_path in test_images:
        print(f"\n🔍 Testing: {os.path.basename(img_path)}")
        embeddings = get_advanced_face_embeddings(img_path)
        print(f"   Found {len(embeddings)} faces")
        
        if len(embeddings) >= 2:
            # Test comparison
            distance = compare_embeddings_advanced(embeddings[0], embeddings[1])
            print(f"   Distance between first two faces: {distance:.4f}")

if __name__ == "__main__":
    test_advanced_detection()
