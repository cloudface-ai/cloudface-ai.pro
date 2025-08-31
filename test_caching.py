#!/usr/bin/env python3
"""
test_caching.py - Test the local file checking and caching system
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from local_cache import (
    get_user_cache_dir, 
    save_bytes_to_cache, 
    file_exists_in_cache,
    get_cached_file_path,
    save_embedding_to_cache,
    load_embedding_from_cache,
    embedding_exists_in_cache,
    get_cache_stats
)

def test_basic_caching():
    """Test basic file caching functionality."""
    print("🧪 Testing basic file caching...")
    
    # Test user and folder
    test_user = "test@example.com"
    test_folder = "test_folder_123"
    
    # Create test data
    test_filename = "test_image.jpg"
    test_data = b"fake image data for testing"
    
    # Test file doesn't exist initially
    assert not file_exists_in_cache(test_user, test_folder, test_filename), "File should not exist initially"
    
    # Save file to cache
    cache_path = save_bytes_to_cache(test_user, test_folder, test_filename, test_data)
    print(f"✅ Saved test file to: {cache_path}")
    
    # Verify file exists
    assert file_exists_in_cache(test_user, test_folder, test_filename), "File should exist after saving"
    
    # Get cached file path
    retrieved_path = get_cached_file_path(test_user, test_folder, test_filename)
    assert retrieved_path == cache_path, "Retrieved path should match saved path"
    
    # Verify file contents
    with open(retrieved_path, 'rb') as f:
        retrieved_data = f.read()
    assert retrieved_data == test_data, "Retrieved data should match saved data"
    
    print("✅ Basic file caching test passed!")

def test_embedding_caching():
    """Test embedding caching functionality."""
    print("🧪 Testing embedding caching...")
    
    test_user = "test@example.com"
    test_photo_ref = "test_photo.jpg"
    test_embedding = [1.0, 2.0, 3.0, 4.0, 5.0]  # Fake embedding data
    
    # Test embedding doesn't exist initially
    assert not embedding_exists_in_cache(test_user, test_photo_ref), "Embedding should not exist initially"
    
    # Save embedding to cache
    cache_path = save_embedding_to_cache(test_user, test_photo_ref, test_embedding)
    print(f"✅ Saved test embedding to: {cache_path}")
    
    # Verify embedding exists
    assert embedding_exists_in_cache(test_user, test_photo_ref), "Embedding should exist after saving"
    
    # Load embedding from cache
    retrieved_embedding = load_embedding_from_cache(test_user, test_photo_ref)
    assert retrieved_embedding == test_embedding, "Retrieved embedding should match saved embedding"
    
    print("✅ Embedding caching test passed!")

def test_cache_stats():
    """Test cache statistics functionality."""
    print("🧪 Testing cache statistics...")
    
    test_user = "test@example.com"
    
    # Get cache stats
    stats = get_cache_stats(test_user)
    print(f"📊 Cache stats: {stats}")
    
    # Verify stats structure
    required_keys = ['photos_count', 'embeddings_count', 'total_photo_size', 'total_embedding_size']
    for key in required_keys:
        assert key in stats, f"Stats should contain {key}"
        assert isinstance(stats[key], (int, float)), f"{key} should be numeric"
    
    print("✅ Cache statistics test passed!")

def test_cache_directory_structure():
    """Test that cache directories are created correctly."""
    print("🧪 Testing cache directory structure...")
    
    test_user = "test@example.com"
    test_folder = "test_folder_456"
    
    # Get cache directory
    cache_dir = get_user_cache_dir(test_user, test_folder)
    print(f"📁 Cache directory: {cache_dir}")
    
    # Verify directory exists
    assert os.path.exists(cache_dir), "Cache directory should exist"
    assert os.path.isdir(cache_dir), "Cache directory should be a directory"
    
    # Test with another folder
    test_folder2 = "test_folder_789"
    cache_dir2 = get_user_cache_dir(test_user, test_folder2)
    assert os.path.exists(cache_dir2), "Second cache directory should exist"
    
    print("✅ Cache directory structure test passed!")

def cleanup_test_data():
    """Clean up test data."""
    print("🧹 Cleaning up test data...")
    
    test_user = "test@example.com"
    
    # Remove test user's cache directory
    user_base_dir = os.path.join("storage", "data", test_user.replace("/", "_"))
    if os.path.exists(user_base_dir):
        shutil.rmtree(user_base_dir)
        print(f"🗑️ Removed test user cache: {user_base_dir}")
    
    # Remove test user's embedding cache directory
    user_embedding_dir = os.path.join("storage", "embeddings", test_user.replace("/", "_"))
    if os.path.exists(user_embedding_dir):
        shutil.rmtree(user_embedding_dir)
        print(f"🗑️ Removed test user embedding cache: {user_embedding_dir}")
    
    print("✅ Cleanup completed!")

def main():
    """Run all tests."""
    print("🚀 Starting caching system tests...")
    print("=" * 50)
    
    try:
        test_basic_caching()
        test_embedding_caching()
        test_cache_stats()
        test_cache_directory_structure()
        
        print("=" * 50)
        print("🎉 All tests passed! Caching system is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        cleanup_test_data()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
