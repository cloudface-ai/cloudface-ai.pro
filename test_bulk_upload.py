#!/usr/bin/env python3
"""
Test bulk upload functionality
"""
import os
import json
from cloudface_pro_pricing import pricing_manager

def test_upload_limits():
    """Test upload limits for different users"""
    print("🧪 Testing Upload Limits")
    print("=" * 50)
    
    # Test different users and batch sizes
    test_cases = [
        {'user': 'sp.vinod@jacpl.com', 'photos': 50, 'size_mb': 100},
        {'user': 'sp.vinod@jacpl.com', 'photos': 100, 'size_mb': 200},
        {'user': 'sp.vinod@jacpl.com', 'photos': 200, 'size_mb': 400},
        {'user': 'test@example.com', 'photos': 50, 'size_mb': 100},
        {'user': 'test@example.com', 'photos': 100, 'size_mb': 200},
    ]
    
    for case in test_cases:
        user = case['user']
        photos = case['photos']
        size_bytes = case['size_mb'] * 1024 * 1024
        
        print(f"\n📊 Testing: {user}")
        print(f"   Photos: {photos}")
        print(f"   Size: {case['size_mb']}MB")
        
        # Get subscription
        subscription = pricing_manager.get_user_subscription(user)
        plan = subscription.get('plan', 'free')
        plan_details = subscription.get('plan_details', {})
        
        print(f"   Plan: {plan} ({plan_details.get('name', 'Unknown')})")
        print(f"   Max batch: {plan_details.get('max_upload_batch', 50)}")
        print(f"   Max photos: {plan_details.get('max_photos', 1000)}")
        print(f"   Max storage: {plan_details.get('storage_gb', 1)}GB")
        
        # Check upload limits
        result = pricing_manager.check_can_upload(user, photos, size_bytes)
        
        if result['allowed']:
            print(f"   ✅ ALLOWED")
        else:
            print(f"   ❌ BLOCKED: {result['reason']}")
        
        print(f"   Current usage: {result['current_usage']}")

def check_storage_space():
    """Check available storage space"""
    print(f"\n💾 Storage Space Check")
    print("=" * 50)
    
    try:
        import shutil
        total, used, free = shutil.disk_usage("/var/www/cloudface-pro")
        
        print(f"   Total: {total/1024/1024/1024:.1f}GB")
        print(f"   Used: {used/1024/1024/1024:.1f}GB")
        print(f"   Free: {free/1024/1024/1024:.1f}GB")
        print(f"   Usage: {(used/total)*100:.1f}%")
        
        if free < 1024**3:  # Less than 1GB
            print(f"   ⚠️  WARNING: Low disk space!")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_nginx_config():
    """Check Nginx upload limits"""
    print(f"\n🌐 Nginx Upload Limits")
    print("=" * 50)
    
    nginx_config = '/etc/nginx/sites-available/cloudface-pro'
    
    if os.path.exists(nginx_config):
        try:
            with open(nginx_config, 'r') as f:
                content = f.read()
                
            # Look for upload-related settings
            lines = content.split('\n')
            upload_settings = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in ['client_max_body_size', 'client_body_timeout', 'proxy_read_timeout']):
                    upload_settings.append(line.strip())
            
            if upload_settings:
                print("   Found upload settings:")
                for setting in upload_settings:
                    print(f"      {setting}")
            else:
                print("   ⚠️  No upload settings found")
                
        except Exception as e:
            print(f"   ❌ Error reading config: {e}")
    else:
        print(f"   ❌ Config file not found: {nginx_config}")

def check_recent_uploads():
    """Check recent upload activity"""
    print(f"\n📁 Recent Upload Activity")
    print("=" * 50)
    
    # Check events folder
    events_path = 'storage/cloudface_pro/events'
    if os.path.exists(events_path):
        events = os.listdir(events_path)
        
        for event_id in events:
            event_path = os.path.join(events_path, event_id)
            if os.path.isdir(event_path):
                photos_path = os.path.join(event_path, 'photos')
                
                if os.path.exists(photos_path):
                    photos = [f for f in os.listdir(photos_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]
                    
                    # Check modification times
                    if photos:
                        latest_photo = max(photos, key=lambda f: os.path.getmtime(os.path.join(photos_path, f)))
                        latest_time = os.path.getmtime(os.path.join(photos_path, latest_photo))
                        
                        from datetime import datetime
                        latest_str = datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %H:%M:%S')
                        
                        print(f"   Event {event_id}: {len(photos)} photos (latest: {latest_str})")
    else:
        print("   ❌ Events folder not found")

if __name__ == '__main__':
    test_upload_limits()
    check_storage_space()
    check_nginx_config()
    check_recent_uploads()
