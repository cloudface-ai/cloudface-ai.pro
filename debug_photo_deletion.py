#!/usr/bin/env python3
"""
Debug script to find out why photos are being deleted
"""
import os
import json
import time
from datetime import datetime

def monitor_photos():
    """Monitor photo folder for changes"""
    print("🔍 Photo Deletion Monitor")
    print("=" * 50)
    
    # Check all event folders
    events_base = 'storage/cloudface_pro/events'
    if not os.path.exists(events_base):
        print("❌ Events folder not found")
        return
    
    total_photos = 0
    total_size = 0
    
    for event_id in os.listdir(events_base):
        event_path = os.path.join(events_base, event_id)
        if os.path.isdir(event_path):
            photos_path = os.path.join(event_path, 'photos')
            
            if os.path.exists(photos_path):
                photos = [f for f in os.listdir(photos_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]
                total_photos += len(photos)
                
                # Calculate size
                size = 0
                for photo in photos:
                    try:
                        size += os.path.getsize(os.path.join(photos_path, photo))
                    except:
                        pass
                total_size += size
                
                print(f"📁 Event {event_id}: {len(photos)} photos ({size/1024/1024:.1f}MB)")
    
    print(f"\n📊 TOTAL: {total_photos} photos ({total_size/1024/1024:.1f}MB)")
    
    # Check for any cleanup scripts or cron jobs
    print(f"\n🔍 CHECKING FOR CLEANUP MECHANISMS:")
    
    # Check if cleanup script exists
    cleanup_script = 'cleanup_vps_storage.py'
    if os.path.exists(cleanup_script):
        print(f"   ⚠️  Found cleanup script: {cleanup_script}")
        print(f"      This script can delete all photos!")
    
    # Check system cron jobs
    try:
        import subprocess
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            cron_jobs = result.stdout
            if 'cleanup' in cron_jobs.lower() or 'delete' in cron_jobs.lower():
                print(f"   ⚠️  Found cleanup cron jobs:")
                for line in cron_jobs.split('\n'):
                    if 'cleanup' in line.lower() or 'delete' in line.lower():
                        print(f"      {line}")
        else:
            print(f"   ✅ No cron jobs found")
    except:
        print(f"   ❌ Could not check cron jobs")
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)
        
        print(f"\n💾 DISK SPACE:")
        print(f"   Free: {free_gb:.1f}GB")
        
        if free_gb < 1:
            print(f"   ⚠️  WARNING: Very low disk space! This might cause issues.")
        elif free_gb < 5:
            print(f"   ⚠️  CAUTION: Low disk space. Monitor closely.")
        else:
            print(f"   ✅ Disk space looks good")
            
    except Exception as e:
        print(f"   ❌ Error checking disk space: {e}")
    
    # Check for any error logs
    print(f"\n📋 CHECKING LOGS:")
    log_files = [
        '/var/log/syslog',
        '/var/log/auth.log',
        'logs.txt'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                # Check last few lines for any deletion activity
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-50:] if len(lines) > 50 else lines
                    
                    for line in recent_lines:
                        if 'delete' in line.lower() or 'remove' in line.lower() or 'cleanup' in line.lower():
                            print(f"   ⚠️  Found deletion activity in {log_file}:")
                            print(f"      {line.strip()}")
                            break
                    else:
                        print(f"   ✅ No deletion activity in {log_file}")
                        
            except Exception as e:
                print(f"   ❌ Error reading {log_file}: {e}")
        else:
            print(f"   ℹ️  {log_file} not found")

if __name__ == '__main__':
    monitor_photos()
