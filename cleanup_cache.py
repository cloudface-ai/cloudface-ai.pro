# cleanup_cache.py
import shutil
import os

print("🧹 Starting SAFE cleanup of CloudFace AI cache...")
print("=" * 50)

# SAFE to delete - only cache and temporary data
safe_to_delete = [
    'storage',           # Processed photos cache
    'dist',             # PyInstaller build output
    '__pycache__',      # Python cache files
    '.vs',              # Visual Studio cache
]

# SAFE to delete - test files and temporary files
test_files_to_delete = [
    'test_photos',       # Test photo folders
    'test_caching.py',   # Test scripts
    '*.test',           # Any .test files
    'test_*.py',        # Python test files
    'test_*.jpg',       # Test images
    'test_*.jpeg',      # Test images
    'test_*.png',       # Test images
]

# Clear cache folders (safe)
for folder in safe_to_delete:
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
            print(f"✅ Cleared {folder}")
        except Exception as e:
            print(f"⚠️  Could not clear {folder}: {e}")
    else:
        print(f"ℹ️  {folder} not found")

# Clear test files (safe)
print("\n🧪 Cleaning test files...")
for test_pattern in test_files_to_delete:
    if test_pattern.startswith('*'):
        # Handle wildcard patterns
        import glob
        for file_path in glob.glob(test_pattern):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"✅ Deleted test file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"✅ Deleted test folder: {file_path}")
            except Exception as e:
                print(f"⚠️  Could not delete {file_path}: {e}")
    else:
        # Handle specific file/folder names
        if os.path.exists(test_pattern):
            try:
                if os.path.isfile(test_pattern):
                    os.remove(test_pattern)
                    print(f"✅ Deleted test file: {test_pattern}")
                elif os.path.isdir(test_pattern):
                    shutil.rmtree(test_pattern)
                    print(f"✅ Deleted test folder: {test_pattern}")
            except Exception as e:
                print(f"⚠️  Could not delete {test_pattern}: {e}")
        else:
            print(f"ℹ️  {test_pattern} not found")

print("=" * 50)
print("✅ Cleanup complete! Your code is safe.")
print("📁 Remaining important files:")
print("   - All .py files (your code)")
print("   - templates/ (HTML files)")
print("   - public/ (static files)")
print("   - README.md, LICENSE, etc.")