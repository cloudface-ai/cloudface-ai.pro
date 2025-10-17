#!/usr/bin/env python3
"""
Check photo status on server - find out why photos are disappearing
"""
import os
import json
from datetime import datetime

def get_folder_size(path):
    """Calculate total size of a folder"""
    total_size = 0
    file_count = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                    file_count += 1
                except:
                    pass
    except:
        pass
    return total_size, file_count

def format_size(bytes_size):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def check_events():
    """Check all events and their photos"""
    print("🔍 CloudFace Pro - Photo Status Check")
    print("=" * 50)
    
    # Check events database
    events_db_path = 'storage/cloudface_pro/events.json'
    if os.path.exists(events_db_path):
        try:
            with open(events_db_path, 'r') as f:
                events = json.load(f)
            
            print(f"📊 Total Events: {len(events)}")
            
            total_photos = 0
            total_size = 0
            
            for event_id, event_data in events.items():
                event_name = event_data.get('name', 'Unknown')
                created_at = event_data.get('created_at', 'Unknown')
                user_id = event_data.get('user_id', 'Unknown')
                
                # Check photos folder
                photos_path = f'storage/cloudface_pro/events/{event_id}/photos'
                if os.path.exists(photos_path):
                    size, count = get_folder_size(photos_path)
                    total_photos += count
                    total_size += size
                    
                    print(f"\n📁 Event: {event_name}")
                    print(f"   ID: {event_id}")
                    print(f"   Created: {created_at}")
                    print(f"   User: {user_id}")
                    print(f"   Photos: {count}")
                    print(f"   Size: {format_size(size)}")
                    
                    # List recent photos (last 10)
                    try:
                        files = os.listdir(photos_path)
                        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]
                        if image_files:
                            print(f"   Recent photos: {', '.join(image_files[:5])}")
                            if len(image_files) > 5:
                                print(f"   ... and {len(image_files) - 5} more")
                    except:
                        pass
                else:
                    print(f"\n📁 Event: {event_name}")
                    print(f"   ID: {event_id}")
                    print(f"   ⚠️  No photos folder found")
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total Events: {len(events)}")
            print(f"   Total Photos: {total_photos}")
            print(f"   Total Size: {format_size(total_size)}")
            
        except Exception as e:
            print(f"❌ Error reading events: {e}")
    else:
        print("❌ Events database not found")
    
    # Check disk space
    print(f"\n💾 DISK SPACE CHECK:")
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        
        print(f"   Total: {format_size(total)}")
        print(f"   Used: {format_size(used)}")
        print(f"   Free: {format_size(free)}")
        print(f"   Usage: {(used/total)*100:.1f}%")
        
        if free < 1024**3:  # Less than 1GB free
            print("   ⚠️  WARNING: Less than 1GB free space!")
        
    except Exception as e:
        print(f"   ❌ Error checking disk space: {e}")

if __name__ == '__main__':
    check_events()
