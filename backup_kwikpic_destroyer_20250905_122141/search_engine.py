"""
search_engine.py - ULTIMATE face matching that DESTROYS Kwikpic
"""

from typing import List, Dict, Any
import numpy as np
import os
from supabase_store import fetch_embeddings_for_user
from local_cache import load_embedding_from_cache, list_cached_embeddings

# Try to import ULTIMATE features
try:
    from final_kwikpic_destroyer import final_destroyer
    from enhanced_embedding_engine import compare_embeddings_enhanced
    _HAS_ULTIMATE_FEATURES = True
    print("🔥 ULTIMATE KWIKPIC DESTROYER FEATURES ACTIVE!")
except ImportError:
    from embedding_engine import compare_embeddings as compare_embeddings_enhanced
    _HAS_ULTIMATE_FEATURES = False
    print("⚠️ Using standard features")

def rank_matches_for_user(user_id: str, selfie_embeddings: List[np.ndarray], threshold: float = 0.6) -> List[Dict[str, Any]]:
    """
    ULTIMATE face matching that DESTROYS Kwikpic
    Uses ensemble detection + killer features for maximum accuracy
    """
    # Try to get embeddings from local cache first (much faster)
    cached_photo_refs = list_cached_embeddings(user_id)
    results: List[Dict[str, Any]] = []
    
    if not selfie_embeddings:
        return results
    
    print(f"🔥 ULTIMATE SEARCH: {len(cached_photo_refs)} cached embeddings for user {user_id}")
    print(f"   Threshold: {threshold:.4f} (lower = more similar)")
    print(f"   Using {'ULTIMATE' if _HAS_ULTIMATE_FEATURES else 'standard'} comparison method")
    
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
                        # Use ULTIMATE comparison if available
                        d = compare_embeddings_enhanced(s, emb)
                        if d < min_dist:
                            min_dist = d
                            min_idx = i
                    
                    # Debug: Show distance values for all photos (not just matches)
                    if len(results) < 10:  # Show more for debugging
                        status = "🔥 ULTIMATE MATCH" if min_dist <= threshold else "❌ NO MATCH"
                        print(f"   {status} Distance: {min_dist:.4f} for {os.path.basename(photo_ref)} (threshold: {threshold:.4f})")
                    
                    if min_dist <= threshold:
                        # Calculate ULTIMATE confidence
                        ultimate_confidence = 1.0 - min_dist
                        if ultimate_confidence > 0.95:
                            ultimate_confidence = 1.0  # Cap at 100%
                        
                        results.append({
                            'photo_reference': photo_ref,
                            'min_distance': float(min_dist),
                            'which_selfie': min_idx,
                            'ultimate_confidence': ultimate_confidence,
                            'kwikpic_destroyer_score': ultimate_confidence * 100
                        })
    
    # If we have results from cache, return them sorted
    if results:
        results.sort(key=lambda x: x['ultimate_confidence'], reverse=True)
        print(f"🔥 ULTIMATE RESULTS: {len(results)} matches from local cache")
        return results
    
    # Fallback to Supabase if no local cache results
    print(f"🔄 No local cache results, checking Supabase...")
    records = fetch_embeddings_for_user(user_id)
    
    if not records:
        print(f"⚠️ No embeddings found in Supabase either")
        return results
    
    print(f"🔥 Processing {len(records)} embeddings from Supabase")
    
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
            ultimate_confidence = 1.0 - min_dist
            if ultimate_confidence > 0.95:
                ultimate_confidence = 1.0
            
            results.append({
                'photo_reference': rec.get('photo_reference'),
                'min_distance': float(min_dist),
                'which_selfie': min_idx,
                'ultimate_confidence': ultimate_confidence,
                'kwikpic_destroyer_score': ultimate_confidence * 100
            })
    
    results.sort(key=lambda x: x['ultimate_confidence'], reverse=True)
    print(f"🔥 ULTIMATE RESULTS: {len(results)} matches from Supabase")
    return results
