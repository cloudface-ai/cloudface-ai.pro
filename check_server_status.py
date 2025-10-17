#!/usr/bin/env python3
"""
Check server status and identify what's causing upload freezes
"""
import os
import json
import psutil
import time
from datetime import datetime

def check_system_resources():
    """Check system resources"""
    print("💻 System Resources")
    print("=" * 50)
    
    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"   CPU Usage: {cpu_percent}%")
    
    # Memory Usage
    memory = psutil.virtual_memory()
    print(f"   RAM Usage: {memory.percent}% ({memory.used/1024/1024/1024:.1f}GB / {memory.total/1024/1024/1024:.1f}GB)")
    
    # Disk Usage
    disk = psutil.disk_usage('/')
    print(f"   Disk Usage: {(disk.used/disk.total)*100:.1f}% ({disk.used/1024/1024/1024:.1f}GB / {disk.total/1024/1024/1024:.1f}GB)")
    
    # Check if resources are high
    if cpu_percent > 80:
        print("   ⚠️  HIGH CPU USAGE!")
    if memory.percent > 80:
        print("   ⚠️  HIGH MEMORY USAGE!")
    if (disk.used/disk.total)*100 > 90:
        print("   ⚠️  LOW DISK SPACE!")

def check_running_processes():
    """Check running processes"""
    print(f"\n🔄 Running Processes")
    print("=" * 50)
    
    # Find Python processes
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                python_processes.append(proc.info)
        except:
            pass
    
    if python_processes:
        print("   Python processes:")
        for proc in python_processes:
            cmdline = ' '.join(proc['cmdline']) if proc['cmdline'] else 'N/A'
            print(f"      PID {proc['pid']}: {proc['cpu_percent']:.1f}% CPU, {proc['memory_percent']:.1f}% RAM")
            print(f"         Command: {cmdline}")
    else:
        print("   No Python processes found")

def check_cloudface_pro_status():
    """Check CloudFace Pro service status"""
    print(f"\n🚀 CloudFace Pro Service")
    print("=" * 50)
    
    try:
        import subprocess
        
        # Check service status
        result = subprocess.run(['systemctl', 'is-active', 'cloudface-pro'], 
                              capture_output=True, text=True)
        status = result.stdout.strip()
        print(f"   Service Status: {status}")
        
        if status == 'active':
            # Check if it's responding
            try:
                import requests
                response = requests.get('http://localhost:5002/', timeout=5)
                print(f"   HTTP Response: {response.status_code}")
            except Exception as e:
                print(f"   HTTP Response: ERROR - {e}")
        
        # Check recent logs
        result = subprocess.run(['journalctl', '-u', 'cloudface-pro', '--since', '5 minutes ago', '--no-pager'], 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"   Recent logs:")
            lines = result.stdout.split('\n')[-10:]  # Last 10 lines
            for line in lines:
                if line.strip():
                    print(f"      {line}")
        else:
            print(f"   No recent logs")
            
    except Exception as e:
        print(f"   Error checking service: {e}")

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

def check_memory_usage():
    """Check memory usage by CloudFace Pro"""
    print(f"\n🧠 Memory Usage Analysis")
    print("=" * 50)
    
    try:
        # Check if there are memory-heavy processes
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower() and 'cloudface' in ' '.join(proc.info['cmdline']):
                    memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                    print(f"   CloudFace Pro Process: {memory_mb:.1f}MB RAM")
                    
                    if memory_mb > 1000:  # More than 1GB
                        print("   ⚠️  HIGH MEMORY USAGE!")
            except:
                pass
    except Exception as e:
        print(f"   Error checking memory: {e}")

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

def main():
    print("🔍 CloudFace Pro - Server Status Check")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_system_resources()
    check_running_processes()
    check_cloudface_pro_status()
    check_upload_performance()
    check_memory_usage()
    check_recent_uploads()
    
    print(f"\n" + "=" * 60)
    print("✅ Status check complete!")

if __name__ == '__main__':
    main()
