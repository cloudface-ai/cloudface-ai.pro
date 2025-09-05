"""
integrate_enhancements.py - Safe integration script for face recognition enhancements
This script gradually integrates the new features without breaking existing functionality
"""

import os
import shutil
from datetime import datetime

def backup_original_files():
    """Create backup of original files before integration"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'embedding_engine.py',
        'search_engine.py',
        'search_handler.py'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"✅ Backed up {file} to {backup_dir}/")
    
    return backup_dir

def test_enhanced_system():
    """Test the enhanced system before integration"""
    print("🧪 Testing Enhanced System...")
    
    try:
        # Test advanced face detector
        from advanced_face_detector import test_advanced_detection
        test_advanced_detection()
        
        # Test AI enhancements
        from ai_enhancements import test_ai_enhancements
        test_ai_enhancements()
        
        # Test enhanced embedding engine
        from enhanced_embedding_engine import test_enhanced_embedding
        test_enhanced_embedding()
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def create_enhanced_search_engine():
    """Create enhanced version of search_engine.py"""
    enhanced_content = '''"""
search_engine.py - Enhanced face matching with advanced features
Maintains compatibility with original system while adding improvements
"""

from typing import List, Dict, Any
import numpy as np
import os
from supabase_store import fetch_embeddings_for_user
from local_cache import load_embedding_from_cache, list_cached_embeddings

# Try to import enhanced features
try:
    from enhanced_embedding_engine import compare_embeddings_enhanced
    _HAS_ENHANCED_FEATURES = True
    print("✅ Enhanced search features available")
except ImportError:
    from embedding_engine import compare_embeddings as compare_embeddings_enhanced
    _HAS_ENHANCED_FEATURES = False
    print("⚠️ Using original search features")

def rank_matches_for_user(user_id: str, selfie_embeddings: List[np.ndarray], threshold: float = 0.6) -> List[Dict[str, Any]]:
    """
    Enhanced face matching with improved accuracy
    Uses advanced comparison methods when available
    """
    # Try to get embeddings from local cache first (much faster)
    cached_photo_refs = list_cached_embeddings(user_id)
    results: List[Dict[str, Any]] = []
    
    if not selfie_embeddings:
        return results
    
    print(f"🔍 Searching {len(cached_photo_refs)} cached embeddings for user {user_id}")
    print(f"   Threshold: {threshold:.4f} (lower = more similar)")
    print(f"   Using {'enhanced' if _HAS_ENHANCED_FEATURES else 'original'} comparison method")
    
    # Process cached embeddings first
    for photo_ref in cached_photo_refs:
        embedding_data = load_embedding_from_cache(user_id, photo_ref)
        if embedding_data is not None:
            # Handle both single embeddings and lists of embeddings
            if isinstance(embedding_data, list):
                embeddings = embedding_data
            else:
                embeddings = [embedding_data]
            
            for emb in embeddings:
                if isinstance(emb, np.ndarray):
                    min_dist = 1e9
                    min_idx = -1
                    for i, s in enumerate(selfie_embeddings):
                        # Use enhanced comparison if available
                        d = compare_embeddings_enhanced(s, emb)
                        if d < min_dist:
                            min_dist = d
                            min_idx = i
                    
                    # Debug: Show distance values for all photos (not just matches)
                    if len(results) < 10:  # Show more for debugging
                        status = "✅ MATCH" if min_dist <= threshold else "❌ NO MATCH"
                        print(f"   {status} Distance: {min_dist:.4f} for {os.path.basename(photo_ref)} (threshold: {threshold:.4f})")
                    
                    if min_dist <= threshold:
                        results.append({
                            'photo_reference': photo_ref,
                            'min_distance': float(min_dist),
                            'which_selfie': min_idx,
                            'confidence': 1.0 - min_dist  # Add confidence score
                        })
    
    # If we have results from cache, return them sorted
    if results:
        results.sort(key=lambda x: x['min_distance'])
        print(f"✅ Found {len(results)} matches from local cache")
        return results
    
    # Fallback to Supabase if no local cache results
    print(f"🔄 No local cache results, checking Supabase...")
    records = fetch_embeddings_for_user(user_id)
    
    if not records:
        print(f"⚠️ No embeddings found in Supabase either")
        return results
    
    print(f"🔍 Processing {len(records)} embeddings from Supabase")
    
    for rec in records:
        emb = np.array(rec.get('face_embedding'), dtype=np.float32)
        min_dist = 1e9
        min_idx = -1
        for i, s in enumerate(selfie_embeddings):
            d = compare_embeddings_enhanced(s, emb)
            if d < min_dist:
                min_dist = d
                min_idx = i
        if min_dist <= threshold:
            results.append({
                'photo_reference': rec.get('photo_reference'),
                'min_distance': float(min_dist),
                'which_selfie': min_idx,
                'confidence': 1.0 - min_dist  # Add confidence score
            })
    
    results.sort(key=lambda x: x['min_distance'])
    print(f"✅ Found {len(results)} matches from Supabase")
    return results
'''
    
    with open('search_engine_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print("✅ Created enhanced search_engine.py")

def create_enhanced_search_handler():
    """Create enhanced version of search_handler.py"""
    enhanced_content = '''"""
search_handler.py - Enhanced search handler with improved accuracy
Maintains compatibility with original system while adding improvements
"""

# Try to import enhanced features
try:
    from enhanced_embedding_engine import embed_image_file_enhanced, compare_embeddings_enhanced
    from search_engine import rank_matches_for_user
    _HAS_ENHANCED_FEATURES = True
    print("✅ Enhanced search handler features available")
except ImportError:
    from embedding_engine import embed_image_file, compare_embeddings
    from search_engine import rank_matches_for_user
    _HAS_ENHANCED_FEATURES = False
    print("⚠️ Using original search handler features")

def search_for_person(selfie_path, user_id, match_threshold=0.80):
    """
    Enhanced person search with improved accuracy
    Uses advanced face detection and comparison when available
    """
    print(f"--- Starting enhanced search for person from selfie path: {selfie_path} ---")
    print(f"   Using {'enhanced' if _HAS_ENHANCED_FEATURES else 'original'} features")

    # 1. Generate the fingerprint for the selfie
    if _HAS_ENHANCED_FEATURES:
        selfie_embeddings = embed_image_file_enhanced(selfie_path, use_ai_enhancements=True)
    else:
        selfie_embeddings = embed_image_file(selfie_path)

    if not selfie_embeddings:
        print("❌ Could not find a face in the provided selfie. Please use a clearer photo.")
        return []

    # Use the first face found in the selfie for the search
    selfie_fingerprint = selfie_embeddings[0]
    
    # 2. Use the enhanced Search Engine to find similar faces
    # Convert similarity threshold to appropriate distance threshold
    if match_threshold >= 0.9:  # 90%+ similarity = very strict
        distance_threshold = 0.35
    elif match_threshold >= 0.8:  # 80%+ similarity = strict
        distance_threshold = 0.45
    elif match_threshold >= 0.7:  # 70%+ similarity = medium-strict
        distance_threshold = 0.55
    elif match_threshold >= 0.6:  # 60%+ similarity = medium
        distance_threshold = 0.65
    elif match_threshold >= 0.5:  # 50%+ similarity = medium-lenient
        distance_threshold = 0.75
    elif match_threshold >= 0.4:  # 40%+ similarity = lenient
        distance_threshold = 0.85
    else:  # Very lenient
        distance_threshold = 0.95
    
    results = rank_matches_for_user(
        user_id=user_id,
        selfie_embeddings=selfie_embeddings,
        threshold=distance_threshold
    )

    # 3. Process and return the results
    if results:
        print(f"\\n--- ✅ Found {len(results)} Matches! ---")

        # Return full match data including similarity scores
        matched_results = []

        for match in results:
            photo_name = match.get("photo_reference")
            distance_score = match.get("min_distance", 0)
            confidence = match.get("confidence", 0)
            
            # Convert distance to similarity properly
            if distance_score <= 0.2:
                similarity_score = 0.95  # 95% similarity for very close matches
            elif distance_score <= 0.4:
                similarity_score = 0.85  # 85% similarity for good matches
            elif distance_score <= 0.6:
                similarity_score = 0.70  # 70% similarity for reasonable matches
            elif distance_score <= 0.8:
                similarity_score = 0.50  # 50% similarity for weak matches
            else:
                similarity_score = 0.30  # 30% similarity for poor matches
            
            # Use confidence if available (from enhanced features)
            if confidence > 0:
                similarity_score = max(similarity_score, confidence)
            
            similarity_percent = f"{similarity_score * 100:.2f}%"
            print(f"  - Found in: {photo_name} (Distance: {distance_score:.4f}, Similarity: {similarity_percent}, Confidence: {confidence:.3f})")

            # Store full match data
            matched_results.append({
                "photo_reference": photo_name,
                "similarity_score": similarity_score,
                "similarity_percent": similarity_percent,
                "confidence": confidence
            })

        return matched_results

    else:
        print("\\n--- ❌ No matches found in the database. ---")
        return []

if __name__ == '__main__':
    # Test the enhanced search handler
    selfie_file = 'my_selfie.jpg'
    test_user_id = 'user_placeholder_id'
    
    print("--- 🚀 STARTING ENHANCED SEARCH TEST 🚀 ---")
    print(f"Searching with selfie: {selfie_file}\\n")

    # Test with different thresholds
    for threshold in [0.90, 0.80, 0.70]:
        print(f"--- Test: Threshold {threshold} ---")
        search_for_person(selfie_file, test_user_id, match_threshold=threshold)
        print("-" * 40)
'''
    
    with open('search_handler_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print("✅ Created enhanced search_handler.py")

def integrate_gradually():
    """Gradually integrate enhancements without breaking existing system"""
    print("🚀 Starting Gradual Integration...")
    
    # Step 1: Test the enhanced system
    if not test_enhanced_system():
        print("❌ Integration aborted - tests failed")
        return False
    
    # Step 2: Create enhanced versions
    create_enhanced_search_engine()
    create_enhanced_search_handler()
    
    # Step 3: Create integration instructions
    instructions = """
# Integration Instructions

## Phase 1: Test Enhanced Features (Safe)
1. Run the enhanced modules alongside your existing system
2. Test with: python advanced_face_detector.py
3. Test with: python ai_enhancements.py
4. Test with: python enhanced_embedding_engine.py

## Phase 2: Gradual Integration (Low Risk)
1. Replace search_engine.py with search_engine_enhanced.py
2. Replace search_handler.py with search_handler_enhanced.py
3. Test your existing functionality

## Phase 3: Full Integration (Medium Risk)
1. Update embedding_engine.py to use enhanced features
2. Update facetak_engine.py to use enhanced features
3. Test thoroughly

## Rollback Instructions
If anything breaks:
1. Restore from backup directory
2. Remove enhanced files
3. System returns to original state

## Files Created:
- advanced_face_detector.py (new)
- ai_enhancements.py (new)
- enhanced_embedding_engine.py (new)
- search_engine_enhanced.py (enhanced version)
- search_handler_enhanced.py (enhanced version)
"""
    
    with open('INTEGRATION_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Integration setup complete!")
    print("📋 See INTEGRATION_INSTRUCTIONS.md for next steps")
    return True

def main():
    """Main integration function"""
    print("🔧 CloudFace AI Enhancement Integration")
    print("=" * 50)
    
    # Create backup
    backup_dir = backup_original_files()
    print(f"📁 Backup created in: {backup_dir}")
    
    # Run integration
    if integrate_gradually():
        print("\\n🎉 Integration setup successful!")
        print("\\nNext steps:")
        print("1. Install new dependencies: pip install -r requirements.txt")
        print("2. Test enhanced features individually")
        print("3. Follow INTEGRATION_INSTRUCTIONS.md for gradual integration")
    else:
        print("\\n❌ Integration setup failed")
        print("Your original system is unchanged and safe")

if __name__ == "__main__":
    main()
