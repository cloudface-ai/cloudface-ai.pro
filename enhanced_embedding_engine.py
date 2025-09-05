"""
enhanced_embedding_engine.py - Enhanced face detection and embedding utilities
Integrates advanced face detection with AI enhancements while maintaining compatibility
"""

from typing import List, Tuple, Optional
import numpy as np
import cv2
import os

# Import our new modules
try:
    from advanced_face_detector import get_advanced_face_embeddings, compare_embeddings_advanced
    from ai_enhancements import enhance_face_for_recognition
    _HAS_ENHANCED_FEATURES = True
    print("✅ Enhanced features available")
except ImportError as e:
    _HAS_ENHANCED_FEATURES = False
    print(f"⚠️ Enhanced features not available: {e}")

# Import original embedding engine as fallback
try:
    from embedding_engine import embed_image_file as original_embed_image_file, compare_embeddings as original_compare_embeddings
    _HAS_ORIGINAL = True
except ImportError:
    _HAS_ORIGINAL = False

def embed_image_file_enhanced(path: str, use_ai_enhancements: bool = True) -> List[np.ndarray]:
    """
    Enhanced face embedding with AI improvements
    Args:
        path: Path to image file
        use_ai_enhancements: Whether to use AI enhancements (age, pose, expression, lighting)
    Returns:
        List of face embeddings
    """
    if not _HAS_ENHANCED_FEATURES:
        # Fallback to 512D system
        return _fallback_512d_embedding(path)
    
    try:
        # Use advanced face detection
        embeddings = get_advanced_face_embeddings(path)
        
        if not embeddings and use_ai_enhancements:
            # Try with AI enhancements if no faces found
            print(f"🔄 No faces found with advanced detection, trying with AI enhancements...")
            embeddings = _try_with_ai_enhancements(path)
        
        return embeddings
        
    except Exception as e:
        print(f"⚠️ Enhanced embedding failed: {e}, falling back to 512D system")
        return _fallback_512d_embedding(path)

def _try_with_ai_enhancements(path: str) -> List[np.ndarray]:
    """Try face detection with AI enhancements"""
    try:
        # Load image
        img = cv2.imread(path)
        if img is None:
            return []
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Apply AI enhancements
        enhanced_img = enhance_face_for_recognition(img_rgb)
        
        # Save enhanced image temporarily
        temp_path = f"temp_enhanced_{os.path.basename(path)}"
        cv2.imwrite(temp_path, cv2.cvtColor(enhanced_img, cv2.COLOR_RGB2BGR))
        
        try:
            # Try advanced detection on enhanced image
            embeddings = get_advanced_face_embeddings(temp_path)
            return embeddings
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"⚠️ AI enhancement attempt failed: {e}")
        return []

def embed_image_bytes_enhanced(data: bytes, use_ai_enhancements: bool = True) -> List[np.ndarray]:
    """
    Enhanced face embedding from bytes with AI improvements
    """
    if not _HAS_ENHANCED_FEATURES:
        # Fallback to 512D system
        try:
            from embedding_engine import embed_image_bytes
            original_embeddings = embed_image_bytes(data)
            if not original_embeddings:
                return []
            
            # Convert 128D to 512D by padding with zeros
            converted_embeddings = []
            for emb in original_embeddings:
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
            
            print(f"✅ Bytes fallback converted {len(converted_embeddings)} embeddings to 512D")
            return converted_embeddings
        except Exception as e:
            print(f"❌ Bytes fallback failed: {e}")
            return []
    
    try:
        # Convert bytes to image
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return []
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Apply AI enhancements if requested
        if use_ai_enhancements:
            enhanced_img = enhance_face_for_recognition(img_rgb)
        else:
            enhanced_img = img_rgb
        
        # Save temporarily and process
        temp_path = "temp_bytes_image.jpg"
        cv2.imwrite(temp_path, cv2.cvtColor(enhanced_img, cv2.COLOR_RGB2BGR))
        
        try:
            embeddings = get_advanced_face_embeddings(temp_path)
            return embeddings
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"⚠️ Enhanced bytes embedding failed: {e}")
        if _HAS_ORIGINAL:
            try:
                from embedding_engine import embed_image_bytes
                return embed_image_bytes(data)
            except:
                return []
        else:
            return []

def compare_embeddings_enhanced(a: np.ndarray, b: np.ndarray) -> float:
    """
    Enhanced embedding comparison with better accuracy
    """
    if _HAS_ENHANCED_FEATURES:
        try:
            return compare_embeddings_advanced(a, b)
        except Exception as e:
            print(f"⚠️ Enhanced comparison failed: {e}")
    
    # Fallback to original comparison
    if _HAS_ORIGINAL:
        return original_compare_embeddings(a, b)
    else:
        # Basic Euclidean distance
        return float(np.linalg.norm(a - b))

def get_face_embeddings_with_metadata(path: str) -> List[dict]:
    """
    Get face embeddings with additional metadata
    Returns list of dicts with 'embedding' and 'metadata' keys
    """
    embeddings = embed_image_file_enhanced(path)
    
    if not embeddings:
        return []
    
    # Load image for metadata extraction
    img = cv2.imread(path)
    if img is None:
        return [{'embedding': emb, 'metadata': {}} for emb in embeddings]
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Extract metadata for each face
    results = []
    for i, embedding in enumerate(embeddings):
        metadata = {}
        
        if _HAS_ENHANCED_FEATURES:
            try:
                from ai_enhancements import ai_pipeline
                
                # Get face crop (simplified - in production you'd get actual face coordinates)
                height, width = img_rgb.shape[:2]
                face_crop = img_rgb[height//4:3*height//4, width//4:3*width//4]
                
                # Extract metadata
                metadata.update({
                    'age_group': ai_pipeline.age_handler.detect_age_group(face_crop),
                    'pose_angles': ai_pipeline.pose_processor.detect_pose_angle(face_crop),
                    'expression': ai_pipeline.expression_processor.detect_expression(face_crop),
                    'lighting_conditions': ai_pipeline.lighting_processor.detect_lighting_conditions(face_crop)
                })
            except Exception as e:
                print(f"⚠️ Metadata extraction failed: {e}")
        
        results.append({
            'embedding': embedding,
            'metadata': metadata
        })
    
    return results

def test_enhanced_embedding():
    """Test the enhanced embedding system"""
    print("🧪 Testing Enhanced Embedding Engine...")
    
    # Test with sample images if available
    test_images = []
    if os.path.exists('storage/data'):
        for root, dirs, files in os.walk('storage/data'):
            for file in files[:2]:  # Test first 2 images
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
        
        # Test basic embedding
        embeddings = embed_image_file_enhanced(img_path, use_ai_enhancements=False)
        print(f"   Basic embedding: {len(embeddings)} faces")
        
        # Test with AI enhancements
        embeddings_enhanced = embed_image_file_enhanced(img_path, use_ai_enhancements=True)
        print(f"   Enhanced embedding: {len(embeddings_enhanced)} faces")
        
        # Test metadata extraction
        if embeddings_enhanced:
            metadata_results = get_face_embeddings_with_metadata(img_path)
            print(f"   Metadata extraction: {len(metadata_results)} results")
            if metadata_results:
                print(f"   Sample metadata: {metadata_results[0]['metadata']}")
        
        # Test comparison
        if len(embeddings_enhanced) >= 2:
            distance = compare_embeddings_enhanced(embeddings_enhanced[0], embeddings_enhanced[1])
            print(f"   Distance between faces: {distance:.4f}")

# Backward compatibility functions
def embed_image_file(path: str) -> List[np.ndarray]:
    """Backward compatible function - uses enhanced version"""
    return embed_image_file_enhanced(path, use_ai_enhancements=True)

def embed_image_bytes(data: bytes) -> List[np.ndarray]:
    """Backward compatible function - uses enhanced version"""
    return embed_image_bytes_enhanced(data, use_ai_enhancements=True)

def compare_embeddings(a: np.ndarray, b: np.ndarray) -> float:
    """Backward compatible function - uses enhanced version"""
    return compare_embeddings_enhanced(a, b)

def _fallback_512d_embedding(path: str) -> List[np.ndarray]:
    """
    Fallback that produces 512D embeddings using a simple method
    This ensures all embeddings are consistently 512D
    """
    try:
        # Use original detection but convert to 512D
        if _HAS_ORIGINAL:
            original_embeddings = original_embed_image_file(path)
            if not original_embeddings:
                return []
            
            # Convert 128D to 512D by padding with zeros
            # This is not ideal but ensures dimension consistency
            converted_embeddings = []
            for emb in original_embeddings:
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
            
            print(f"✅ Fallback converted {len(converted_embeddings)} embeddings to 512D")
            return converted_embeddings
        else:
            print("⚠️ No fallback available")
            return []
            
    except Exception as e:
        print(f"❌ 512D fallback failed: {e}")
        return []

if __name__ == "__main__":
    test_enhanced_embedding()
