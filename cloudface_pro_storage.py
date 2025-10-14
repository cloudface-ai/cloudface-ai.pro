"""
CloudFace Pro - Storage Abstraction Layer
Works with VPS now, easily switch to cloud later with zero code changes
"""

import os
import shutil
from abc import ABC, abstractmethod
from typing import Optional, List, BinaryIO
from pathlib import Path
import cloudface_pro_config as config


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def save_file(self, file_path: str, file_data: BinaryIO) -> bool:
        """Save a file to storage"""
        pass
    
    @abstractmethod
    def get_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve a file from storage"""
        pass
    
    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    def list_files(self, directory: str) -> List[str]:
        """List all files in a directory"""
        pass
    
    @abstractmethod
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        pass


class VPSStorage(StorageBackend):
    """Local VPS storage implementation"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or config.VPS_STORAGE_PATH
        os.makedirs(self.base_path, exist_ok=True)
    
    def _get_full_path(self, file_path: str) -> str:
        """Convert relative path to full path"""
        return os.path.join(self.base_path, file_path.lstrip('/'))
    
    def save_file(self, file_path: str, file_data: BinaryIO) -> bool:
        """Save file to local VPS storage"""
        try:
            full_path = self._get_full_path(file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'wb') as f:
                shutil.copyfileobj(file_data, f)
            
            print(f"✅ Saved file: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving file {file_path}: {e}")
            return False
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """Read file from local VPS storage"""
        try:
            full_path = self._get_full_path(file_path)
            with open(full_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from local VPS storage"""
        try:
            full_path = self._get_full_path(file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"🗑️ Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting file {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in local VPS storage"""
        full_path = self._get_full_path(file_path)
        return os.path.exists(full_path)
    
    def list_files(self, directory: str) -> List[str]:
        """List all files in a directory"""
        try:
            full_path = self._get_full_path(directory)
            if not os.path.exists(full_path):
                return []
            
            files = []
            for root, dirs, filenames in os.walk(full_path):
                for filename in filenames:
                    rel_path = os.path.relpath(
                        os.path.join(root, filename),
                        full_path
                    )
                    files.append(rel_path)
            return files
        except Exception as e:
            print(f"❌ Error listing files in {directory}: {e}")
            return []
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            full_path = self._get_full_path(file_path)
            return os.path.getsize(full_path)
        except Exception as e:
            print(f"❌ Error getting file size {file_path}: {e}")
            return 0
    
    def get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        try:
            full_path = self._get_full_path(directory)
            total_size = 0
            for root, dirs, files in os.walk(full_path):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    total_size += os.path.getsize(filepath)
            return total_size
        except Exception as e:
            print(f"❌ Error getting directory size {directory}: {e}")
            return 0


class CloudflareR2Storage(StorageBackend):
    """Cloudflare R2 storage implementation (for future migration)"""
    
    def __init__(self):
        # Initialize Cloudflare R2 client
        # boto3 with custom endpoint
        pass
    
    def save_file(self, file_path: str, file_data: BinaryIO) -> bool:
        # TODO: Implement Cloudflare R2 upload
        raise NotImplementedError("Cloudflare R2 not yet implemented")
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        # TODO: Implement Cloudflare R2 download
        raise NotImplementedError("Cloudflare R2 not yet implemented")
    
    def delete_file(self, file_path: str) -> bool:
        # TODO: Implement Cloudflare R2 delete
        raise NotImplementedError("Cloudflare R2 not yet implemented")
    
    def file_exists(self, file_path: str) -> bool:
        # TODO: Implement Cloudflare R2 exists check
        raise NotImplementedError("Cloudflare R2 not yet implemented")
    
    def list_files(self, directory: str) -> List[str]:
        # TODO: Implement Cloudflare R2 list
        raise NotImplementedError("Cloudflare R2 not yet implemented")
    
    def get_file_size(self, file_path: str) -> int:
        # TODO: Implement Cloudflare R2 size check
        raise NotImplementedError("Cloudflare R2 not yet implemented")


class StorageManager:
    """
    Main storage manager - automatically uses correct backend
    Switch storage by changing config.STORAGE_TYPE
    """
    
    def __init__(self):
        storage_type = config.STORAGE_TYPE
        
        if storage_type == "VPS":
            self.backend = VPSStorage()
            print(f"📦 Storage: VPS (Local Disk)")
        elif storage_type == "CLOUDFLARE_R2":
            self.backend = CloudflareR2Storage()
            print(f"📦 Storage: Cloudflare R2 (Cloud)")
        else:
            # Default to VPS
            self.backend = VPSStorage()
            print(f"⚠️  Unknown storage type '{storage_type}', using VPS")
    
    # ===========================
    # DELEGATE ALL CALLS TO BACKEND
    # ===========================
    
    def save_file(self, file_path: str, file_data: BinaryIO) -> bool:
        return self.backend.save_file(file_path, file_data)
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        return self.backend.get_file(file_path)
    
    def delete_file(self, file_path: str) -> bool:
        return self.backend.delete_file(file_path)
    
    def file_exists(self, file_path: str) -> bool:
        return self.backend.file_exists(file_path)
    
    def list_files(self, directory: str) -> List[str]:
        return self.backend.list_files(directory)
    
    def get_file_size(self, file_path: str) -> int:
        return self.backend.get_file_size(file_path)
    
    # ===========================
    # HIGH-LEVEL HELPER METHODS
    # ===========================
    
    def save_event_photo(self, event_id: str, filename: str, file_data: BinaryIO) -> bool:
        """Save a photo for an event"""
        file_path = f"events/{event_id}/photos/{filename}"
        return self.save_file(file_path, file_data)
    
    def save_event_thumbnail(self, event_id: str, filename: str, file_data: BinaryIO) -> bool:
        """Save a thumbnail for an event"""
        file_path = f"events/{event_id}/thumbnails/{filename}"
        return self.save_file(file_path, file_data)
    
    def save_event_logo(self, event_id: str, filename: str, file_data: BinaryIO) -> bool:
        """Save company logo for an event"""
        file_path = f"events/{event_id}/logo/{filename}"
        return self.save_file(file_path, file_data)
    
    def save_event_watermark_logo(self, event_id: str, filename: str, file_data: BinaryIO) -> bool:
        """Save watermark logo for an event"""
        file_path = f"events/{event_id}/watermark/{filename}"
        return self.save_file(file_path, file_data)
    
    def get_event_photo(self, event_id: str, filename: str) -> Optional[bytes]:
        """Get a photo from an event"""
        file_path = f"events/{event_id}/photos/{filename}"
        return self.get_file(file_path)
    
    def get_event_thumbnail(self, event_id: str, filename: str) -> Optional[bytes]:
        """Get a thumbnail from an event"""
        file_path = f"events/{event_id}/thumbnails/{filename}"
        return self.get_file(file_path)
    
    def get_event_watermark_logo(self, event_id: str, filename: str) -> Optional[bytes]:
        """Get event watermark logo"""
        file_path = f"events/{event_id}/watermark/{filename}"
        return self.get_file(file_path)
    
    def list_event_photos(self, event_id: str) -> List[str]:
        """List all photos in an event"""
        directory = f"events/{event_id}/photos"
        return self.list_files(directory)
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an entire event (all photos, thumbnails, etc)"""
        try:
            if isinstance(self.backend, VPSStorage):
                # For VPS, delete the entire event directory
                event_dir = self.backend._get_full_path(f"events/{event_id}")
                if os.path.exists(event_dir):
                    shutil.rmtree(event_dir)
                    print(f"🗑️ Deleted event: {event_id}")
                    return True
            return False
        except Exception as e:
            print(f"❌ Error deleting event {event_id}: {e}")
            return False
    
    def get_event_size(self, event_id: str) -> int:
        """Get total size of an event in bytes"""
        if isinstance(self.backend, VPSStorage):
            return self.backend.get_directory_size(f"events/{event_id}")
        return 0
    
    def get_total_storage_used(self) -> dict:
        """Get total storage usage statistics"""
        if isinstance(self.backend, VPSStorage):
            total_bytes = self.backend.get_directory_size("events")
            total_gb = total_bytes / (1024 ** 3)
            
            return {
                'total_bytes': total_bytes,
                'total_gb': round(total_gb, 2),
                'limit_gb': config.VPS_MAX_SIZE_GB,
                'used_percentage': round((total_gb / config.VPS_MAX_SIZE_GB) * 100, 2),
                'remaining_gb': round(config.VPS_MAX_SIZE_GB - total_gb, 2)
            }
        return {}


# ===========================
# GLOBAL INSTANCE
# ===========================

# Create a single instance to be used throughout the app
storage = StorageManager()


# ===========================
# USAGE EXAMPLE
# ===========================

if __name__ == "__main__":
    print("🧪 Testing Storage Manager...")
    
    # Test file operations
    test_event_id = "test-event-123"
    test_content = b"Hello CloudFace Pro!"
    
    # Save file
    from io import BytesIO
    storage.save_event_photo(test_event_id, "test.txt", BytesIO(test_content))
    
    # Read file
    content = storage.get_event_photo(test_event_id, "test.txt")
    print(f"Read content: {content}")
    
    # List files
    files = storage.list_event_photos(test_event_id)
    print(f"Files: {files}")
    
    # Get storage stats
    stats = storage.get_total_storage_used()
    print(f"Storage: {stats}")
    
    # Clean up
    storage.delete_event(test_event_id)
    
    print("✅ Storage Manager test complete!")

