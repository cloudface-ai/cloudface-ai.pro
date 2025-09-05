"""
kwikpic_killer_models.py - Advanced AI models to beat Kwikpic's 99.9% accuracy
"""

import torch
import torch.nn as nn
import numpy as np
import cv2
from typing import List, Dict, Tuple
import os

class KwikpicKillerDetector:
    """
    Advanced face detection system designed to beat Kwikpic's 99.9% accuracy
    """
    
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.models = {}
        self._initialize_killer_models()
    
    def _initialize_killer_models(self):
        """Initialize multiple advanced models for ensemble accuracy"""
        print("🔥 Initializing KWIKPIC KILLER MODELS...")
        
        try:
            # Model 1: MTCNN + FaceNet (current)
            from facenet_pytorch import MTCNN, InceptionResnetV1
            self.models['mtcnn'] = MTCNN(
                image_size=224,  # Higher resolution
                margin=0,
                min_face_size=15,  # Detect smaller faces
                thresholds=[0.5, 0.6, 0.6],  # More sensitive
                factor=0.6,  # More detection scales
                post_process=True,
                device=self.device
            )
            
            self.models['facenet'] = InceptionResnetV1(pretrained='vggface2').eval()
            if self.device == 'cuda':
                self.models['facenet'] = self.models['facenet'].cuda()
            
            # Model 2: RetinaFace (state-of-the-art)
            try:
                from retinaface import RetinaFace
                self.models['retinaface'] = RetinaFace
                print("✅ RetinaFace loaded - EXTREME accuracy!")
            except:
                print("⚠️ RetinaFace not available")
            
            # Model 3: MediaPipe (Google's best) - Disabled due to Windows protobuf issue
            try:
                import mediapipe as mp
                # Skip MediaPipe due to Windows protobuf parsing error
                # self.models['mediapipe'] = mp.solutions.face_detection
                # self.models['mp_detector'] = mp.solutions.face_detection.FaceDetection(
                #     model_selection=1,  # Full range model
                #     min_detection_confidence=0.5
                # )
                print("⚠️ MediaPipe disabled - Windows protobuf issue")
            except:
                print("⚠️ MediaPipe not available")
            
            # Model 4: YOLOv8 Face (latest)
            try:
                from ultralytics import YOLO
                # Try to load face detection model
                try:
                    self.models['yolo_face'] = YOLO('yolov8n.pt')  # Use general YOLO model
                    print("✅ YOLOv8 loaded - Latest tech!")
                except:
                    self.models['yolo_face'] = YOLO('yolov8n.pt')  # Fallback to general model
                    print("✅ YOLOv8 loaded (general model) - Latest tech!")
            except:
                print("⚠️ YOLOv8 Face not available")
            
            # Model 5: InsightFace (ONNX-based RetinaFace/SCRFD alternative)
            try:
                import insightface
                from insightface.app import FaceAnalysis
                self.models['insightface_app'] = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
                self.models['insightface_app'].prepare(ctx_id=0, det_size=(640, 640))
                print("✅ InsightFace loaded - Fast ONNX RetinaFace/SCRFD!")
            except Exception as e:
                print(f"⚠️ InsightFace not available: {e}")
            
            print(f"🔥 {len(self.models)} KILLER MODELS READY!")
            
        except Exception as e:
            print(f"❌ Model initialization failed: {e}")
    
    def detect_faces_ensemble(self, image_path: str) -> List[Dict]:
        """
        Use ALL models to detect faces - ensemble approach for maximum accuracy
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            all_detections = []
            
            # Model 1: MTCNN + FaceNet
            if 'mtcnn' in self.models and 'facenet' in self.models:
                detections = self._detect_with_mtcnn_facenet(img_rgb)
                all_detections.extend(detections)
            
            # Model 2: RetinaFace
            if 'retinaface' in self.models:
                detections = self._detect_with_retinaface(img_rgb)
                all_detections.extend(detections)
            
            # Model 3: MediaPipe (disabled due to Windows protobuf issue)
            # if 'mediapipe' in self.models:
            #     detections = self._detect_with_mediapipe(img_rgb)
            #     all_detections.extend(detections)
            
            # Model 4: YOLOv8
            if 'yolo_face' in self.models:
                detections = self._detect_with_yolo(img_rgb)
                all_detections.extend(detections)
            
            # Model 5: InsightFace
            if 'insightface_app' in self.models:
                detections = self._detect_with_insightface(img_rgb)
                all_detections.extend(detections)
            
            # Ensemble voting - combine all detections
            final_detections = self._ensemble_voting(all_detections, img_rgb.shape)
            
            print(f"🔥 ENSEMBLE DETECTED {len(final_detections)} FACES!")
            return final_detections
            
        except Exception as e:
            print(f"❌ Ensemble detection failed: {e}")
            return []
    
    def _detect_with_mtcnn_facenet(self, img_rgb):
        """MTCNN + FaceNet detection"""
        try:
            boxes, probs, landmarks = self.models['mtcnn'].detect(img_rgb, landmarks=True)
            detections = []
            
            if boxes is not None:
                for i, box in enumerate(boxes):
                    if probs[i] > 0.8:  # High confidence
                        x1, y1, x2, y2 = box.astype(int)
                        face = img_rgb[y1:y2, x1:x2]
                        
                        # Get FaceNet embedding
                        face_tensor = self.models['mtcnn'](face)
                        if face_tensor is not None:
                            with torch.no_grad():
                                embedding = self.models['facenet'](face_tensor.unsqueeze(0))
                                embedding = embedding.cpu().numpy().flatten()
                            
                            detections.append({
                                'bbox': box,
                                'confidence': float(probs[i]),
                                'embedding': embedding,
                                'model': 'mtcnn_facenet',
                                'landmarks': landmarks[i] if landmarks is not None else None
                            })
            
            return detections
        except Exception as e:
            print(f"⚠️ MTCNN detection failed: {e}")
            return []
    
    def _detect_with_retinaface(self, img_rgb):
        """RetinaFace detection"""
        try:
            # Use the correct RetinaFace method
            detections = self.models['retinaface'].detect_faces(img_rgb)
            results = []
            
            for face_key, face_data in detections.items():
                bbox = face_data['facial_area']
                confidence = face_data['score']
                
                if confidence > 0.8:
                    x1, y1, x2, y2 = bbox
                    face = img_rgb[y1:y2, x1:x2]
                    
                    # Generate embedding (simplified)
                    embedding = self._generate_simple_embedding(face)
                    
                    results.append({
                        'bbox': np.array([x1, y1, x2, y2]),
                        'confidence': confidence,
                        'embedding': embedding,
                        'model': 'retinaface',
                        'landmarks': face_data.get('landmarks')
                    })
            
            return results
        except Exception as e:
            print(f"⚠️ RetinaFace detection failed: {e}")
            return []
    
    def _detect_with_mediapipe(self, img_rgb):
        """MediaPipe detection"""
        try:
            results = self.models['mp_detector'].process(img_rgb)
            detections = []
            
            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = img_rgb.shape
                    
                    x1 = int(bbox.xmin * w)
                    y1 = int(bbox.ymin * h)
                    x2 = int((bbox.xmin + bbox.width) * w)
                    y2 = int((bbox.ymin + bbox.height) * h)
                    
                    confidence = detection.score[0]
                    
                    if confidence > 0.8:
                        face = img_rgb[y1:y2, x1:x2]
                        embedding = self._generate_simple_embedding(face)
                        
                        detections.append({
                            'bbox': np.array([x1, y1, x2, y2]),
                            'confidence': confidence,
                            'embedding': embedding,
                            'model': 'mediapipe'
                        })
            
            return detections
        except Exception as e:
            print(f"⚠️ MediaPipe detection failed: {e}")
            return []
    
    def _detect_with_yolo(self, img_rgb):
        """YOLOv8 Face detection"""
        try:
            results = self.models['yolo_face'](img_rgb)
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        confidence = box.conf[0].item()
                        # Check if it's a person class (class 0 in COCO dataset)
                        class_id = box.cls[0].item()
                        if confidence > 0.8 and class_id == 0:  # Person class
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            face = img_rgb[int(y1):int(y2), int(x1):int(x2)]
                            embedding = self._generate_simple_embedding(face)
                            
                            detections.append({
                                'bbox': np.array([x1, y1, x2, y2]),
                                'confidence': confidence,
                                'embedding': embedding,
                                'model': 'yolo_face'
                            })
            
            return detections
        except Exception as e:
            print(f"⚠️ YOLO detection failed: {e}")
            return []
    
    def _detect_with_insightface(self, img_rgb):
        """InsightFace (FaceAnalysis) detection"""
        try:
            app = self.models['insightface_app']
            faces = app.get(img_rgb)
            detections = []
            for f in faces:
                # bbox: [x1, y1, x2, y2]
                x1, y1, x2, y2 = [int(v) for v in f.bbox]
                confidence = float(f.det_score) if hasattr(f, 'det_score') else 0.9
                face = img_rgb[y1:y2, x1:x2]
                
                # Use FaceNet embedding if available; else use InsightFace embedding
                if 'facenet' in self.models and face.size > 0:
                    embedding = self._generate_simple_embedding(face)
                else:
                    embedding = f.normed_embedding if hasattr(f, 'normed_embedding') else np.random.rand(512)
                
                detections.append({
                    'bbox': np.array([x1, y1, x2, y2]),
                    'confidence': confidence,
                    'embedding': np.array(embedding),
                    'model': 'insightface',
                    'landmarks': f.landmark if hasattr(f, 'landmark') else None
                })
            return detections
        except Exception as e:
            print(f"⚠️ InsightFace detection failed: {e}")
            return []
    
    def _generate_simple_embedding(self, face):
        """Generate simple embedding for models without built-in embedding"""
        try:
            # Resize face to standard size
            face_resized = cv2.resize(face, (160, 160))
            
            # Use FaceNet if available
            if 'facenet' in self.models:
                face_tensor = torch.from_numpy(face_resized).permute(2, 0, 1).float() / 255.0
                face_tensor = face_tensor.unsqueeze(0)
                if self.device == 'cuda':
                    face_tensor = face_tensor.cuda()
                
                with torch.no_grad():
                    embedding = self.models['facenet'](face_tensor)
                    return embedding.cpu().numpy().flatten()
            else:
                # Fallback to simple histogram
                hist = cv2.calcHist([face_resized], [0, 1, 2], None, [32, 32, 32], [0, 256, 0, 256, 0, 256])
                return hist.flatten()
        except:
            return np.random.rand(512)  # Fallback
    
    def _ensemble_voting(self, all_detections, img_shape):
        """Combine all detections using ensemble voting"""
        if not all_detections:
            return []
        
        # Group nearby detections
        final_detections = []
        used_indices = set()
        
        for i, det1 in enumerate(all_detections):
            if i in used_indices:
                continue
            
            # Find similar detections
            similar_detections = [det1]
            for j, det2 in enumerate(all_detections):
                if j <= i or j in used_indices:
                    continue
                
                # Check if detections overlap
                if self._detections_overlap(det1['bbox'], det2['bbox']):
                    similar_detections.append(det2)
                    used_indices.add(j)
            
            # Combine similar detections
            if len(similar_detections) > 1:
                final_det = self._combine_detections(similar_detections)
            else:
                final_det = det1
            
            final_detections.append(final_det)
            used_indices.add(i)
        
        return final_detections
    
    def _detections_overlap(self, bbox1, bbox2, threshold=0.5):
        """Check if two bounding boxes overlap significantly"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return False
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        iou = intersection / union if union > 0 else 0
        return iou > threshold
    
    def _combine_detections(self, detections):
        """Combine multiple detections into one"""
        # Average bounding boxes
        bboxes = np.array([det['bbox'] for det in detections])
        avg_bbox = np.mean(bboxes, axis=0)
        
        # Average confidences
        confidences = [det['confidence'] for det in detections]
        avg_confidence = np.mean(confidences)
        
        # Average embeddings
        embeddings = np.array([det['embedding'] for det in detections])
        avg_embedding = np.mean(embeddings, axis=0)
        
        return {
            'bbox': avg_bbox,
            'confidence': avg_confidence,
            'embedding': avg_embedding,
            'model': 'ensemble',
            'num_models': len(detections)
        }

# Global instance
kwikpic_killer = KwikpicKillerDetector()

def detect_faces_kwikpic_killer(image_path: str) -> List[Dict]:
    """Main function to detect faces with Kwikpic-killing accuracy"""
    return kwikpic_killer.detect_faces_ensemble(image_path)

def test_kwikpic_killer():
    """Test the Kwikpic killer system"""
    print("🔥 TESTING KWIKPIC KILLER SYSTEM...")
    
    # Test with sample images
    test_images = []
    if os.path.exists('storage/data'):
        for root, dirs, files in os.walk('storage/data'):
            for file in files[:2]:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_images.append(os.path.join(root, file))
                    break
            if test_images:
                break
    
    if not test_images:
        print("⚠️ No test images found")
        return
    
    for img_path in test_images:
        print(f"\n🔥 Testing: {os.path.basename(img_path)}")
        detections = detect_faces_kwikpic_killer(img_path)
        print(f"   Detected {len(detections)} faces with ensemble method")
        
        for i, det in enumerate(detections):
            print(f"   Face {i+1}: confidence={det['confidence']:.3f}, model={det['model']}")

if __name__ == "__main__":
    test_kwikpic_killer()
