# search_handler.py

from embedding_engine import embed_image_file, compare_embeddings
from search_engine import rank_matches_for_user

# --- Configuration ---
# The photo you want to use to search for matches.
SELFIE_TO_SEARCH = 'my_selfie.jpg'
# The user ID to search within (same as in process_photos.py)
USER_ID = '8a5d3f9b-1e2c-3b4d-5e6f-7a8b9c0d1e2f'

def search_for_person(selfie_path, user_id, match_threshold=0.80):
    """
    Finds all photos in the database containing the person from the selfie.
    """
    print(f"--- Starting search for person from selfie path: {selfie_path} ---")

    # 1. Generate the fingerprint for the selfie
    # Embed from the file path
    selfie_embeddings = embed_image_file(selfie_path)

    if not selfie_embeddings:
        print("❌ Could not find a face in the provided selfie. Please use a clearer photo.")
        return []

    # Use the first face found in the selfie for the search
    selfie_fingerprint = selfie_embeddings[0]
    
    # 2. Use the new Search Engine to find similar faces
    # The search_engine uses distance where lower = more similar
    # Convert similarity threshold to appropriate distance threshold
    # Face recognition distances are typically 0.1-0.3 for good matches
    # Use a gradual, logical conversion to avoid dramatic jumps
    # Make it more lenient to find more photos
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
            
            # Convert distance to similarity properly
            # Face recognition: distance 0.0 = perfect match, distance 0.6+ = poor match
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
            
            similarity_percent = f"{similarity_score * 100:.2f}%"
            print(f"  - Found in: {photo_name} (Distance: {distance_score:.4f}, Similarity: {similarity_percent})")

            # Store full match data
            matched_results.append({
                "photo_reference": photo_name,  # Use photo_reference to match backend expectation
                "similarity_score": similarity_score,
                "similarity_percent": similarity_percent
            })

        return matched_results

    else:
        print("\n--- ❌ No matches found in the database. ---")
        # --- ADD THIS FINAL RETURN STATEMENT ---
        return []

if __name__ == '__main__':
    # --- This is our controlled test ---
    
    selfie_file = 'my_selfie.jpg'
    test_user_id = 'user_placeholder_id'
    
    print("--- 🚀 STARTING CONTROLLED TEST 🚀 ---")
    print(f"Searching with selfie: {selfie_file}\n")

    # Test 1: Strict Threshold (should find very few, perfect matches)
    print("--- Test 1: Strict Threshold (0.90) ---")
    search_for_person(selfie_file, test_user_id, match_threshold=0.90)
    print("-" * 40)

    # Test 2: Medium Threshold (should find a few good matches)
    print("\n--- Test 2: Medium Threshold (0.80) ---")
    search_for_person(selfie_file, test_user_id, match_threshold=0.80)
    print("-" * 40)

    # Test 3: Lenient Threshold (should find the most potential matches)
    print("\n--- Test 3: Lenient Threshold (0.70) ---")
    search_for_person(selfie_file, test_user_id, match_threshold=0.70)
    print("-" * 40)

    print("\n--- ✅ TEST COMPLETE ✅ ---")
