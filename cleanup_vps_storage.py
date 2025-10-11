#!/usr/bin/env python3
"""
Cleanup script for VPS - Remove all downloaded/cached files AND Firebase data
Use this to free up disk space and clean test data
"""
import os
import shutil
from firebase_store import db

def get_folder_size(path):
    """Calculate total size of a folder"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
    except:
        pass
    return total_size

def format_size(bytes_size):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def cleanup_firebase():
    """Clean up Firebase face embeddings"""
    print("\n🔥 Firebase Cleanup")
    print("=" * 50)
    
    try:
        # Get all face embeddings from Firebase
        faces_ref = db.collection('face_embeddings')
        
        # Count documents
        all_docs = list(faces_ref.stream())
        total_docs = len(all_docs)
        
        print(f"📊 Total face embeddings in Firebase: {total_docs:,}")
        
        if total_docs == 0:
            print("✅ Firebase is already clean!")
            return 0
        
        # Show breakdown by user
        user_counts = {}
        for doc in all_docs:
            data = doc.to_dict()
            user_id = data.get('user_id', 'unknown')
            user_counts[user_id] = user_counts.get(user_id, 0) + 1
        
        print(f"\n📋 Breakdown by user:")
        for user_id, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {user_id}: {count:,} embeddings")
        
        # Ask for confirmation
        print(f"\n⚠️  WARNING: This will delete ALL {total_docs:,} face embeddings from Firebase!")
        print("   Users will need to reprocess ALL photos from scratch.")
        response = input(f"\n   Delete all Firebase data? (type 'DELETE ALL' to confirm): ").strip()
        
        if response == 'DELETE ALL':
            deleted_count = 0
            print(f"\n🔥 Deleting {total_docs:,} documents...")
            
            # Delete in batches (Firestore limit: 500 per batch)
            batch = db.batch()
            batch_count = 0
            
            for doc in all_docs:
                batch.delete(doc.reference)
                batch_count += 1
                deleted_count += 1
                
                # Commit every 500 docs
                if batch_count >= 500:
                    batch.commit()
                    print(f"   Progress: {deleted_count:,}/{total_docs:,} deleted...")
                    batch = db.batch()
                    batch_count = 0
            
            # Commit remaining
            if batch_count > 0:
                batch.commit()
            
            print(f"   ✅ Deleted {deleted_count:,} face embeddings from Firebase")
            return deleted_count
        else:
            print(f"   ⏭️  Skipped Firebase cleanup")
            return 0
            
    except Exception as e:
        print(f"❌ Firebase cleanup error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def cleanup_storage():
    """Clean up all storage folders"""
    
    print("🧹 CloudFace AI Storage Cleanup Tool")
    print("=" * 50)
    
    folders_to_clean = [
        'storage/downloads',      # Google Drive cached photos
        'storage/uploads',        # Local uploaded files
        'uploads',                # Temp uploads folder
        'storage/cache',          # General cache
    ]
    
    total_freed = 0
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            folder_size = get_folder_size(folder)
            print(f"\n📁 {folder}")
            print(f"   Current size: {format_size(folder_size)}")
            
            # Count files
            file_count = sum([len(files) for _, _, files in os.walk(folder)])
            print(f"   Files: {file_count:,}")
            
            # Ask for confirmation
            response = input(f"   Delete this folder? (yes/no): ").strip().lower()
            
            if response == 'yes':
                try:
                    shutil.rmtree(folder)
                    os.makedirs(folder, exist_ok=True)  # Recreate empty folder
                    print(f"   ✅ Deleted {format_size(folder_size)}")
                    total_freed += folder_size
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            else:
                print(f"   ⏭️  Skipped")
        else:
            print(f"\n📁 {folder}")
            print(f"   ⚠️  Folder doesn't exist (already clean)")
    
    print("\n" + "=" * 50)
    print(f"🎉 Storage cleanup complete!")
    print(f"💾 Total disk space freed: {format_size(total_freed)}")
    
    return total_freed

if __name__ == '__main__':
    # Safety check
    print("\n⚠️  WARNING: This will delete ALL test data!")
    print("   - Downloaded Google Drive photos")
    print("   - Uploaded local files")
    print("   - Temp processing files")
    print("   - Face embeddings in Firebase")
    print("\n❌ This is IRREVERSIBLE! All data will be permanently deleted.")
    print("✅ Only do this if you want to clean all test data completely.")
    
    confirm = input("\n🤔 Are you sure you want to continue? (type 'CLEAN' to confirm): ")
    
    if confirm == 'CLEAN':
        # Clean storage folders first
        storage_freed = cleanup_storage()
        
        # Then clean Firebase
        firebase_deleted = cleanup_firebase()
        
        # Final summary
        print("\n" + "=" * 50)
        print("🎉 COMPLETE CLEANUP FINISHED!")
        print(f"💾 Disk space freed: {format_size(storage_freed)}")
        print(f"🔥 Firebase embeddings deleted: {firebase_deleted:,}")
        print("\n✅ Your VPS is now clean and ready for production!")
    else:
        print("\n❌ Cleanup cancelled.")

