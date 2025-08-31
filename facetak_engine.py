# facetak_engine.py

import face_recognition
import cv2
import numpy as np

def get_face_embeddings(image_path):
    """
    This function takes the path to an image, finds all faces,
    and returns a list of their vector embeddings (fingerprints).

    Args:
        image_path (str): The file path to the image.

    Returns:
        list: A list of face embeddings. Each embedding is a NumPy array.
              Returns an empty list if no faces are found.
    """
    try:
        # Load the image using face_recognition
        image = face_recognition.load_image_file(image_path)
        
        # The face_encodings function detects faces AND creates embeddings
        # It's a very efficient all-in-one command.
        embeddings = face_recognition.face_encodings(image)
        
        if not embeddings:
            print(f"⚠️ No face detected in {image_path}. Skipping.")
            return []

        print(f"✅ Found {len(embeddings)} face(s) in {image_path}")
        return embeddings

    except Exception as e:
        print(f"❌ An error occurred while processing {image_path}: {e}")
        return []

# --- Example Usage (for testing the engine) ---
if __name__ == '__main__':
    test_image_file = 'test_image.jpg'
    
    # Check if a test image exists
    try:
        # Create a simple blank image for the test if one doesn't exist
        img = np.zeros((512, 512, 3), dtype=np.uint8)
        cv2.imwrite(test_image_file, img)
        print(f"Created a dummy image: {test_image_file}")
    except:
        pass

    print("\n--- Testing Facetak Engine ---")
    face_fingerprints = get_face_embeddings(test_image_file)
    
    if face_fingerprints:
        print(f"\nSuccessfully generated {len(face_fingerprints)} fingerprint(s).")
        print(f"First fingerprint starts with: {face_fingerprints[0][:5]}...")
    else:
        print("\nCould not generate any fingerprints from the test image.")