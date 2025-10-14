"""
CloudFace Pro - Photo Processor
Adapts existing face recognition engine to work with CloudFace Pro storage
"""

import os
import cv2
from io import BytesIO
from PIL import Image
import numpy as np
from typing import List, Dict
from datetime import datetime
from cloudface_pro_storage import storage
from cloudface_pro_events import event_manager
from real_face_recognition_engine import RealFaceRecognitionEngine


class CloudFaceProProcessor:
    """Process photos for CloudFace Pro events"""
    
    def __init__(self):
        self.engine = RealFaceRecognitionEngine()
        print("✅ CloudFace Pro Processor initialized")
    
    def process_event_photos(self, event_id: str, photo_files: List[tuple], 
                           progress_callback=None) -> Dict:
        """
        Process all photos for an event
        photo_files: List of (filename, file_object) tuples
        Returns: Processing stats
        """
        
        stats = {
            'total_photos': len(photo_files),
            'processed': 0,
            'faces_found': 0,
            'errors': 0,
            'face_embeddings': []
        }
        
        print(f"🔄 Processing {len(photo_files)} photos for event {event_id}")
        
        for idx, (filename, file_obj) in enumerate(photo_files):
            try:
                # 1. Load image for processing (photos already saved in upload route)
                file_obj.seek(0)
                image_bytes = file_obj.read()
                
                if len(image_bytes) == 0:
                    print(f"  ⚠️ Empty file: {filename}")
                    continue
                
                image = self._bytes_to_image(image_bytes)
                if image is None:
                    print(f"  ⚠️ Could not load image: {filename}")
                    continue
                
                # 3. Skip thumbnail generation (already done during upload)
                
                # 4. Detect faces and generate embeddings
                try:
                    face_results = self.engine.detect_and_embed_faces(image)
                except Exception as e:
                    print(f"  ⚠️ Face detection error for {filename}: {e}")
                    face_results = []
                
                if face_results:
                    for face_data in face_results:
                        # Store embedding with filename (convert numpy array to list for JSON)
                        stats['face_embeddings'].append({
                            'filename': filename,
                            'embedding': face_data['embedding'].tolist(),  # Convert numpy array to list
                            'bbox': face_data.get('bbox', [])
                        })
                        stats['faces_found'] += 1
                
                stats['processed'] += 1
                
                # Progress callback
                if progress_callback:
                    progress_callback(idx + 1, len(photo_files))
                
                if (idx + 1) % 10 == 0:
                    print(f"  ✅ Processed {idx + 1}/{len(photo_files)} photos")
                
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {e}")
                stats['errors'] += 1
        
        # Update event stats
        try:
            event_manager.update_event(event_id, {
                'stats.total_photos': stats['processed'],
                'stats.total_faces': stats['faces_found'],
                'status': 'ready'
            })
            
            # Update storage size
            event_manager.update_storage_size(event_id)
        except Exception as e:
            print(f"⚠️ Warning: Could not update event stats: {e}")
            # Continue anyway - stats are not critical
        
        print(f"✅ Event processing complete:")
        print(f"   Photos: {stats['processed']}")
        print(f"   Faces: {stats['faces_found']}")
        print(f"   Errors: {stats['errors']}")
        
        return stats
    
    def generate_thumbnails_only(self, event_id: str, photo_files: List[tuple]) -> int:
        """
        Generate thumbnails only (fast operation for immediate display)
        Returns count of thumbnails generated
        """
        generated_count = 0
        
        print(f"🖼️ Generating thumbnails for {len(photo_files)} photos")
        
        for filename, file_obj in photo_files:
            try:
                # Load image
                file_obj.seek(0)
                image_bytes = file_obj.read()
                
                if len(image_bytes) == 0:
                    continue
                
                image = self._bytes_to_image(image_bytes)
                if image is None:
                    continue
                
                # Generate thumbnail
                thumbnail = self._create_thumbnail(image)
                thumbnail_bytes = self._image_to_bytes(thumbnail)
                storage.save_event_thumbnail(event_id, filename, BytesIO(thumbnail_bytes))
                
                generated_count += 1
                
                if generated_count % 5 == 0:
                    print(f"  ✅ Generated {generated_count}/{len(photo_files)} thumbnails")
                
            except Exception as e:
                print(f"  ⚠️ Thumbnail error for {filename}: {e}")
        
        print(f"✅ Generated {generated_count} thumbnails")
        return generated_count
    
    def process_event_photos_background(self, event_id: str, photo_files: List[tuple]):
        """Process photos in background thread"""
        print(f"🔄 Starting background processing for event {event_id}")
        
        try:
            # Update event status to processing
            event_manager.update_event(event_id, {'status': 'processing'})
            
            # Process photos (same logic as before but in background)
            stats = self.process_event_photos(event_id, photo_files)
            
            # Mark as complete
            event_manager.update_event(event_id, {'status': 'ready'})
            
            # Store completion status for frontend to check
            import os
            testing_mode = os.environ.get('TESTING_MODE', 'true').lower() == 'true'
            if testing_mode:
                import json
                completion_file = f'storage/cloudface_pro/events/{event_id}/processing_complete.json'
                os.makedirs(os.path.dirname(completion_file), exist_ok=True)
                
                # Create a JSON-safe version of stats (remove face_embeddings as they're large)
                safe_stats = {
                    'total_photos': stats.get('total_photos', 0),
                    'processed': stats.get('processed', 0),
                    'faces_found': stats.get('faces_found', 0),
                    'errors': stats.get('errors', 0)
                }
                
                with open(completion_file, 'w') as f:
                    json.dump({
                        'completed': True,
                        'timestamp': datetime.now().isoformat(),
                        'stats': safe_stats
                    }, f)
            
            print(f"✅ Background processing complete for event {event_id}")
            
        except Exception as e:
            print(f"❌ Background processing failed for event {event_id}: {e}")
            event_manager.update_event(event_id, {'status': 'error'})
    
    def search_face_in_event(self, event_id: str, query_image_bytes: bytes,
                            threshold: float = 0.6) -> List[Dict]:
        """
        Search for a face in an event's photos
        Returns: List of matching photos with similarity scores
        """
        
        # Load query image
        query_image = self._bytes_to_image(query_image_bytes)
        
        # Detect face in query image
        query_face_results = self.engine.detect_and_embed_faces(query_image)
        if not query_face_results:
            print("❌ No face detected in query image")
            return []
        
        # Get embedding for first face
        query_embedding = np.array(query_face_results[0]['embedding'])
        if query_embedding is None:
            print("❌ Could not generate embedding for query face")
            return []
        
        # Load event embeddings from Firebase
        # (In production, these would be stored in FAISS index)
        event = event_manager.get_event(event_id)
        if not event:
            print(f"❌ Event {event_id} not found")
            return []
        
        # For now, we'll do simple comparison
        # In production, use FAISS for faster search
        matches = []
        
        # Get all photos from storage
        photo_files = storage.list_event_photos(event_id)
        
        for photo_file in photo_files:
            try:
                # Load photo
                photo_bytes = storage.get_event_photo(event_id, photo_file)
                if not photo_bytes:
                    continue
                
                photo_image = self._bytes_to_image(photo_bytes)
                
                # Detect faces
                face_results = self.engine.detect_and_embed_faces(photo_image)
                
                for face_data in face_results:
                    embedding = np.array(face_data['embedding'])
                    
                    # Calculate similarity
                    similarity = self._calculate_similarity(query_embedding, embedding)
                    
                    if similarity >= threshold:
                        matches.append({
                            'filename': photo_file,
                            'similarity': float(similarity),
                            'bbox': face_data.get('bbox', [])
                        })
            
            except Exception as e:
                print(f"  ❌ Error searching {photo_file}: {e}")
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Increment search counter
        event_manager.increment_stat(event_id, 'total_searches')
        
        print(f"✅ Found {len(matches)} matches above {threshold} threshold")
        
        return matches
    
    def search_face_in_single_photo(self, photo_bytes: bytes, query_bytes: bytes, photo_filename: str, threshold: float = 0.6) -> List[Dict]:
        """
        Search for a face in a single photo (for streaming results)
        Returns list of matches for this specific photo
        """
        try:
            # Load images
            photo_image = self._bytes_to_image(photo_bytes)
            query_image = self._bytes_to_image(query_bytes)
            
            if photo_image is None or query_image is None:
                return []
            
            # Detect faces in query image
            query_face_results = self.engine.detect_and_embed_faces(query_image)
            if not query_face_results:
                return []
            
            # Detect faces in photo
            photo_face_results = self.engine.detect_and_embed_faces(photo_image)
            if not photo_face_results:
                return []
            
            # Compare embeddings
            matches = []
            for query_face in query_face_results:
                query_embedding = np.array(query_face['embedding'])
                
                for photo_face in photo_face_results:
                    photo_embedding = np.array(photo_face['embedding'])
                    
                    # Calculate similarity
                    similarity = self._calculate_similarity(query_embedding, photo_embedding)
                    
                    if similarity >= threshold:
                        matches.append({
                            'filename': photo_filename,
                            'similarity': float(similarity),
                            'bbox': photo_face.get('bbox', [])
                        })
            
            return matches
            
        except Exception as e:
            print(f"⚠️ Error searching in single photo {photo_filename}: {e}")
            return []
    
    def _bytes_to_image(self, image_bytes: bytes) -> np.ndarray:
        """Convert bytes to OpenCV image"""
        # Use PIL to handle EXIF orientation
        pil_image = Image.open(BytesIO(image_bytes))
        
        # Fix orientation
        try:
            from PIL import ExifTags
            exif = pil_image._getexif()
            if exif:
                for tag, value in exif.items():
                    if ExifTags.TAGS.get(tag) == 'Orientation':
                        if value == 3:
                            pil_image = pil_image.rotate(180, expand=True)
                        elif value == 6:
                            pil_image = pil_image.rotate(270, expand=True)
                        elif value == 8:
                            pil_image = pil_image.rotate(90, expand=True)
        except:
            pass
        
        # Convert to OpenCV format
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return image
    
    def _image_to_bytes(self, image: np.ndarray, format: str = 'JPEG') -> bytes:
        """Convert OpenCV image to bytes"""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Save to bytes
        buffer = BytesIO()
        pil_image.save(buffer, format=format, quality=85)
        return buffer.getvalue()
    
    def _create_thumbnail(self, image: np.ndarray, size: tuple = (400, 400)) -> np.ndarray:
        """Create thumbnail maintaining aspect ratio"""
        height, width = image.shape[:2]
        
        # Calculate scaling
        scale = min(size[0] / width, size[1] / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize
        thumbnail = cv2.resize(image, (new_width, new_height), 
                             interpolation=cv2.INTER_AREA)
        
        return thumbnail
    
    def _calculate_similarity(self, embedding1: np.ndarray, 
                            embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        # Normalize
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2)
        
        return float(similarity)


# Global instance
processor = CloudFaceProProcessor()


if __name__ == "__main__":
    print("✅ CloudFace Pro Processor ready!")
    print("   Use processor.process_event_photos() to process uploads")
    print("   Use processor.search_face_in_event() to search faces")

