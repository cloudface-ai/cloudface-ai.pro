# process_photos.py

import os
from facetak_engine import get_face_embeddings
from database_handler import add_face

# --- Configuration ---
# The folder containing the images you want to process.
TARGET_FOLDER = 'test_photos' 
# A unique ID for the user who owns these photos.
# In a real app, this would come from your user authentication system.
# For now, we'll use a placeholder.
USER_ID = '8a5d3f9b-1e2c-3b4d-5e6f-7a8b9c0d1e2f' # Example UUID

def process_image_folder(folder_path, user_id):
    """
    Scans a folder, processes all images, and stores face embeddings.
    """
    print(f"--- Starting photo processing for folder: {folder_path} ---")
    
    # Check if the target folder exists
    if not os.path.isdir(folder_path):
        print(f"❌ Error: Folder '{folder_path}' not found.")
        return

    # Loop through all files in the directory
    for filename in os.listdir(folder_path):
        # Check if the file is a common image type
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            print(f"\nProcessing image: {filename}...")
            
            # 1. Use the Facetak Engine to get face fingerprints
            embeddings = get_face_embeddings(image_path)
            
            # 2. If any faces were found, save them to the database
            if embeddings:
                for embedding in embeddings:
                    # A unique reference for this photo (e.g., filename)
                    photo_reference = filename 
                    
                    # 3. Use the Database Handler to add the face
                    add_face(
                        user_id=user_id,
                        photo_ref=photo_reference,
                        embedding=embedding
                    )
    
    print("\n--- ✅ Photo processing complete! ---")

# This block makes the script runnable
if __name__ == '__main__':
    process_image_folder(TARGET_FOLDER, USER_ID)