"""
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
        print(f"\n--- ✅ Found {len(results)} Matches! ---")

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
        print("\n--- ❌ No matches found in the database. ---")
        return []

if __name__ == '__main__':
    # Test the enhanced search handler
    selfie_file = 'my_selfie.jpg'
    test_user_id = 'user_placeholder_id'
    
    print("--- 🚀 STARTING ENHANCED SEARCH TEST 🚀 ---")
    print(f"Searching with selfie: {selfie_file}\n")

    # Test with different thresholds
    for threshold in [0.90, 0.80, 0.70]:
        print(f"--- Test: Threshold {threshold} ---")
        search_for_person(selfie_file, test_user_id, match_threshold=threshold)
        print("-" * 40)
