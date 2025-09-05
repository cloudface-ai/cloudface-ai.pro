"""
test_2048d_engine.py - Test the Ultimate 2048D Engine
"""

import os
import sys
from ultimate_2048d_engine import get_ultimate_2048d_embeddings, compare_embeddings_ultimate_2048d

def test_2048d_engine():
    """Test the 2048D engine with available images"""
    print("🔥 Testing ULTIMATE 2048D ENGINE...")
    
    # Find test images
    test_images = []
    if os.path.exists('storage/data'):
        for root, dirs, files in os.walk('storage/data'):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_images.append(os.path.join(root, file))
                    if len(test_images) >= 3:  # Test with 3 images
                        break
            if len(test_images) >= 3:
                break
    
    if not test_images:
        print("❌ No test images found in storage/data")
        return
    
    print(f"📸 Found {len(test_images)} test images")
    
    # Test each image
    embeddings = []
    for i, image_path in enumerate(test_images):
        print(f"\n🖼️  Testing image {i+1}: {os.path.basename(image_path)}")
        
        try:
            emb = get_ultimate_2048d_embeddings(image_path)
            if emb:
                embeddings.append(emb[0])
                print(f"   ✅ Generated 2048D embedding: {len(emb[0])} dimensions")
                print(f"   📊 Sample values: {emb[0][:5]}...")
            else:
                print(f"   ❌ No embeddings generated")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test comparisons
    if len(embeddings) >= 2:
        print(f"\n🔍 Testing comparisons...")
        for i in range(len(embeddings)):
            for j in range(i+1, len(embeddings)):
                similarity = compare_embeddings_ultimate_2048d(embeddings[i], embeddings[j])
                print(f"   Image {i+1} vs Image {j+1}: {similarity:.4f}")
    
    print(f"\n✅ 2048D Engine test completed!")
    print(f"   Generated {len(embeddings)} embeddings")
    print(f"   All embeddings are {len(embeddings[0]) if embeddings else 0}D")

if __name__ == "__main__":
    test_2048d_engine()
