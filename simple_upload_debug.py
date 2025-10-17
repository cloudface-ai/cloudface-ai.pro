#!/usr/bin/env python3
"""
Simple upload debug script - no external dependencies
"""
import os
import json
import time
import subprocess
from datetime import datetime

def check_system_resources():
    """Check system resources using basic commands"""
    print("💻 System Resources")
    print("=" * 50)
    
    try:
        # Check memory
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
        
        for line in meminfo.split('\n'):
            if 'MemTotal:' in line:
                total_kb = int(line.split()[1])
                total_gb = total_kb / 1024 / 1024
                print(f"   Total RAM: {total_gb:.1f}GB")
            elif 'MemAvailable:' in line:
                avail_kb = int(line.split()[1])
                avail_gb = avail_kb / 1024 / 1024
                print(f"   Available RAM: {avail_gb:.1f}GB")
                break
        
        # Check disk space
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    print(f"   Disk Usage: {parts[4]} ({parts[2]} used of {parts[1]})")
        
    except Exception as e:
        print(f"   Error: {e}")

def check_cloudface_pro_status():
    """Check CloudFace Pro service status"""
    print(f"\n🚀 CloudFace Pro Service")
    print("=" * 50)
    
    try:
        # Check service status
        result = subprocess.run(['systemctl', 'is-active', 'cloudface-pro'], 
                              capture_output=True, text=True)
        status = result.stdout.strip()
        print(f"   Service Status: {status}")
        
        # Check recent logs
        result = subprocess.run(['journalctl', '-u', 'cloudface-pro', '--since', '10 minutes ago', '--no-pager', '-n', '20'], 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"   Recent logs (last 10 minutes):")
            lines = result.stdout.split('\n')
            for line in lines[-10:]:  # Last 10 lines
                if line.strip():
                    print(f"      {line}")
        else:
            print(f"   No recent logs")
            
    except Exception as e:
        print(f"   Error: {e}")

def check_upload_performance():
    """Check upload performance issues"""
    print(f"\n📤 Upload Performance Check")
    print("=" * 50)
    
    # Check if there are stuck upload processes
    events_path = 'storage/cloudface_pro/events'
    if os.path.exists(events_path):
        processing_events = []
        
        for event_id in os.listdir(events_path):
            event_path = os.path.join(events_path, event_id)
            if os.path.isdir(event_path):
                # Check for processing completion file
                completion_file = os.path.join(event_path, 'processing_complete.json')
                
                if not os.path.exists(completion_file):
                    # Check when photos were last uploaded
                    photos_path = os.path.join(event_path, 'photos')
                    if os.path.exists(photos_path):
                        photos = [f for f in os.listdir(photos_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]
                        
                        if photos:
                            latest_photo = max(photos, key=lambda f: os.path.getmtime(os.path.join(photos_path, f)))
                            latest_time = os.path.getmtime(os.path.join(photos_path, latest_photo))
                            time_diff = time.time() - latest_time
                            
                            # If photos uploaded more than 10 minutes ago but no completion file
                            if time_diff > 600:  # 10 minutes
                                processing_events.append({
                                    'event_id': event_id,
                                    'photos': len(photos),
                                    'minutes_ago': int(time_diff / 60)
                                })
        
        if processing_events:
            print("   ⚠️  Stuck processing events:")
            for event in processing_events:
                print(f"      Event {event['event_id']}: {event['photos']} photos, {event['minutes_ago']} minutes ago")
        else:
            print("   ✅ No stuck processing events")

def check_recent_uploads():
    """Check recent upload activity"""
    print(f"\n📁 Recent Upload Activity")
    print("=" * 50)
    
    events_path = 'storage/cloudface_pro/events'
    if os.path.exists(events_path):
        recent_uploads = []
        
        for event_id in os.listdir(events_path):
            event_path = os.path.join(events_path, event_id)
            if os.path.isdir(event_path):
                photos_path = os.path.join(event_path, 'photos')
                
                if os.path.exists(photos_path):
                    photos = [f for f in os.listdir(photos_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]
                    
                    if photos:
                        # Get latest photo timestamp
                        latest_photo = max(photos, key=lambda f: os.path.getmtime(os.path.join(photos_path, f)))
                        latest_time = os.path.getmtime(os.path.join(photos_path, latest_photo))
                        time_diff = time.time() - latest_time
                        
                        # Only show uploads from last 30 minutes
                        if time_diff < 1800:  # 30 minutes
                            recent_uploads.append({
                                'event_id': event_id,
                                'photos': len(photos),
                                'minutes_ago': int(time_diff / 60),
                                'latest_photo': latest_photo
                            })
        
        if recent_uploads:
            print("   Recent uploads (last 30 minutes):")
            for upload in sorted(recent_uploads, key=lambda x: x['minutes_ago']):
                print(f"      Event {upload['event_id']}: {upload['photos']} photos ({upload['minutes_ago']} min ago)")
        else:
            print("   No recent uploads")

def check_file_sizes():
    """Check file sizes in recent uploads"""
    print(f"\n📏 File Size Analysis")
    print("=" * 50)
    
    events_path = 'storage/cloudface_pro/events'
    if os.path.exists(events_path):
        for event_id in os.listdir(events_path):
            event_path = os.path.join(events_path, event_id)
            if os.path.isdir(event_path):
                photos_path = os.path.join(event_path, 'photos')
                
                if os.path.exists(photos_path):
                    photos = [f for f in os.listdir(photos_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]
                    
                    if photos:
                        # Check file sizes
                        large_files = 0
                        total_size = 0
                        max_size = 0
                        
                        for photo in photos:
                            try:
                                size = os.path.getsize(os.path.join(photos_path, photo))
                                total_size += size
                                max_size = max(max_size, size)
                                
                                if size > 10 * 1024 * 1024:  # Larger than 10MB
                                    large_files += 1
                            except:
                                pass
                        
                        size_mb = total_size / 1024 / 1024
                        max_size_mb = max_size / 1024 / 1024
                        
                        if size_mb > 100:  # More than 100MB total
                            print(f"   Event {event_id}: {len(photos)} photos, {size_mb:.1f}MB total")
                            print(f"      Largest file: {max_size_mb:.1f}MB")
                            if large_files > 0:
                                print(f"      ⚠️  {large_files} large files (>10MB)")

def suggest_fixes():
    """Suggest fixes for upload freeze issues"""
    print(f"\n🔧 Suggested Fixes")
    print("=" * 50)
    
    print("   If uploads are freezing, try these solutions:")
    print()
    print("   1. Reduce batch size:")
    print("      - Try uploading 5-10 photos at a time")
    print("      - Instead of 25 photos, try 10 photos")
    print()
    print("   2. Check file sizes:")
    print("      - Use smaller photos (under 5MB each)")
    print("      - Resize large images before uploading")
    print()
    print("   3. Restart the service:")
    print("      sudo systemctl restart cloudface-pro")
    print()
    print("   4. Clear stuck processes:")
    print("      sudo pkill -f cloudface_pro")
    print("      sudo systemctl start cloudface-pro")
    print()
    print("   5. Monitor system during upload:")
    print("      - Open another terminal")
    print("      - Run: top")
    print("      - Watch CPU and memory usage")

def main():
    print("🔍 Simple Upload Debug Tool")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_system_resources()
    check_cloudface_pro_status()
    check_upload_performance()
    check_recent_uploads()
    check_file_sizes()
    suggest_fixes()
    
    print(f"\n" + "=" * 60)
    print("✅ Debug complete!")

if __name__ == '__main__':
    main()
