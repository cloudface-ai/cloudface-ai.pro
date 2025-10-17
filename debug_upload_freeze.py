#!/usr/bin/env python3
"""
Debug upload freeze issues
"""
import os
import json
import time
import psutil
from datetime import datetime

def check_upload_limits():
    """Check if upload limits are causing issues"""
    print("📊 Upload Limits Check")
    print("=" * 50)
    
    try:
        from cloudface_pro_pricing import pricing_manager
        
        # Test different batch sizes
        test_cases = [10, 25, 50, 100, 200]
        user = 'sp.vinod@jacpl.com'
        
        for batch_size in test_cases:
            size_bytes = batch_size * 2 * 1024 * 1024  # Assume 2MB per photo
            
            result = pricing_manager.check_can_upload(user, batch_size, size_bytes)
            
            status = "✅ ALLOWED" if result['allowed'] else "❌ BLOCKED"
            print(f"   {batch_size} photos: {status}")
            
            if not result['allowed']:
                print(f"      Reason: {result['reason']}")
        
    except Exception as e:
        print(f"   Error: {e}")

def check_memory_during_processing():
    """Check memory usage during photo processing"""
    print(f"\n🧠 Memory Usage During Processing")
    print("=" * 50)
    
    # Check if there are any large photo processing operations
    events_path = 'storage/cloudface_pro/events'
    if os.path.exists(events_path):
        for event_id in os.listdir(events_path):
            event_path = os.path.join(events_path, event_id)
            if os.path.isdir(event_path):
                photos_path = os.path.join(event_path, 'photos')
                
                if os.path.exists(photos_path):
                    photos = [f for f in os.listdir(photos_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]
                    
                    if photos:
                        # Calculate total size
                        total_size = 0
                        large_files = 0
                        
                        for photo in photos:
                            try:
                                size = os.path.getsize(os.path.join(photos_path, photo))
                                total_size += size
                                
                                if size > 10 * 1024 * 1024:  # Larger than 10MB
                                    large_files += 1
                            except:
                                pass
                        
                        size_mb = total_size / 1024 / 1024
                        
                        if size_mb > 500:  # More than 500MB
                            print(f"   Event {event_id}: {len(photos)} photos, {size_mb:.1f}MB total")
                            if large_files > 0:
                                print(f"      ⚠️  {large_files} large files (>10MB)")

def check_processing_status():
    """Check if background processing is stuck"""
    print(f"\n🔄 Background Processing Status")
    print("=" * 50)
    
    events_path = 'storage/cloudface_pro/events'
    if os.path.exists(events_path):
        stuck_events = []
        
        for event_id in os.listdir(events_path):
            event_path = os.path.join(events_path, event_id)
            if os.path.isdir(event_path):
                completion_file = os.path.join(event_path, 'processing_complete.json')
                
                if not os.path.exists(completion_file):
                    # Check if photos exist but no completion
                    photos_path = os.path.join(event_path, 'photos')
                    if os.path.exists(photos_path):
                        photos = [f for f in os.listdir(photos_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]
                        
                        if photos:
                            # Check when photos were uploaded
                            latest_photo = max(photos, key=lambda f: os.path.getmtime(os.path.join(photos_path, f)))
                            latest_time = os.path.getmtime(os.path.join(photos_path, latest_photo))
                            time_diff = time.time() - latest_time
                            
                            if time_diff > 300:  # More than 5 minutes
                                stuck_events.append({
                                    'event_id': event_id,
                                    'photos': len(photos),
                                    'minutes_stuck': int(time_diff / 60)
                                })
        
        if stuck_events:
            print("   ⚠️  Stuck processing events:")
            for event in stuck_events:
                print(f"      Event {event['event_id']}: {event['photos']} photos, stuck for {event['minutes_stuck']} minutes")
                
            print(f"\n   🔧 Fix: Restart the service to clear stuck processes:")
            print(f"      sudo systemctl restart cloudface-pro")
        else:
            print("   ✅ No stuck processing events")

def check_system_load():
    """Check system load and performance"""
    print(f"\n⚡ System Performance")
    print("=" * 50)
    
    # CPU Load
    cpu_percent = psutil.cpu_percent(interval=2)
    print(f"   CPU Usage: {cpu_percent}%")
    
    # Memory
    memory = psutil.virtual_memory()
    print(f"   RAM Usage: {memory.percent}% ({memory.used/1024/1024/1024:.1f}GB / {memory.total/1024/1024/1024:.1f}GB)")
    
    # Load Average
    load_avg = os.getloadavg()
    print(f"   Load Average: {load_avg[0]:.2f} (1min), {load_avg[1]:.2f} (5min), {load_avg[2]:.2f} (15min)")
    
    # Check if system is overloaded
    if cpu_percent > 90:
        print("   ⚠️  HIGH CPU USAGE - This could cause freezes!")
    if memory.percent > 90:
        print("   ⚠️  HIGH MEMORY USAGE - This could cause freezes!")
    if load_avg[0] > 4:
        print("   ⚠️  HIGH LOAD AVERAGE - System overloaded!")

def suggest_fixes():
    """Suggest fixes for upload freeze issues"""
    print(f"\n🔧 Suggested Fixes")
    print("=" * 50)
    
    print("   If uploads are freezing, try these solutions:")
    print()
    print("   1. Reduce batch size:")
    print("      - Try uploading 10-15 photos at a time")
    print("      - Instead of 25 photos, try 10 photos")
    print()
    print("   2. Check file sizes:")
    print("      - Use smaller/resized photos (under 5MB each)")
    print("      - Avoid very high resolution images")
    print()
    print("   3. Restart the service:")
    print("      sudo systemctl restart cloudface-pro")
    print()
    print("   4. Check for stuck processes:")
    print("      sudo pkill -f cloudface_pro")
    print("      sudo systemctl start cloudface-pro")
    print()
    print("   5. Monitor during upload:")
    print("      - Open another terminal")
    print("      - Run: watch -n 1 'ps aux | grep python'")
    print("      - Watch memory usage during upload")

def main():
    print("🔍 Upload Freeze Debug Tool")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_upload_limits()
    check_memory_during_processing()
    check_processing_status()
    check_system_load()
    suggest_fixes()
    
    print(f"\n" + "=" * 60)
    print("✅ Debug complete!")

if __name__ == '__main__':
    main()
