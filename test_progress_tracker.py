#!/usr/bin/env python3
"""
Test Progress Tracker
This file demonstrates how the progress tracker works without modifying main files
"""

import time
import threading
from progress_tracker import *

def simulate_google_drive_processing():
    """Simulate the Google Drive processing workflow"""
    print("🚀 Starting Google Drive processing simulation...")
    
    # Start progress tracking
    start_progress()
    
    # Step 1: Download files
    print("\n📥 Step 1: Downloading files from Google Drive")
    set_status('download', 'Starting download...')
    set_total('download', 25)  # 25 files to download
    
    for i in range(25):
        time.sleep(0.1)  # Simulate download time
        increment('download')
        set_status('download', f'Downloaded {i+1}/25 files')
        print(f"  📥 Downloaded file {i+1}/25")
    
    # Step 2: Processing photos
    print("\n🖼️ Step 2: Processing photos")
    set_status('processing', 'Starting photo processing...')
    set_total('processing', 25)
    
    for i in range(25):
        time.sleep(0.15)  # Simulate processing time
        increment('processing')
        set_status('processing', f'Processed {i+1}/25 photos')
        print(f"  🖼️ Processed photo {i+1}/25")
    
    # Step 3: Face detection
    print("\n👤 Step 3: Face detection")
    set_status('face_detection', 'Starting face detection...')
    set_total('face_detection', 25)
    
    for i in range(25):
        time.sleep(0.2)  # Simulate face detection time
        increment('face_detection')
        set_status('face_detection', f'Detected faces in {i+1}/25 photos')
        print(f"  👤 Detected faces in photo {i+1}/25")
    
    # Step 4: Creating embeddings
    print("\n🧠 Step 4: Creating face embeddings")
    set_status('embedding', 'Starting embedding creation...')
    set_total('embedding', 25)
    
    for i in range(25):
        time.sleep(0.25)  # Simulate embedding time
        increment('embedding')
        set_status('embedding', f'Created embeddings for {i+1}/25 faces')
        print(f"  🧠 Created embeddings for face {i+1}/25")
    
    # Step 5: Storing in database
    print("\n💾 Step 5: Storing in database")
    set_status('storage', 'Starting database storage...')
    set_total('storage', 25)
    
    for i in range(25):
        time.sleep(0.1)  # Simulate storage time
        increment('storage')
        set_status('storage', f'Stored {i+1}/25 records')
        print(f"  💾 Stored record {i+1}/25")
    
    # Complete
    print("\n✅ All steps completed!")
    stop_progress()

def monitor_progress():
    """Monitor and display progress updates"""
    print("📊 Progress Monitor Started")
    
    while True:
        progress = get_progress()
        
        # Clear screen (simple approach)
        print("\n" * 10)
        
        # Display overall progress
        print("=" * 60)
        print(f"🎯 OVERALL PROGRESS: {progress['overall']}%")
        if progress['estimated_time']:
            print(f"⏱️  {progress['estimated_time']}")
        print("=" * 60)
        
        # Display each step
        for step_name, step_data in progress['steps'].items():
            step_name_display = step_name.replace('_', ' ').title()
            progress_bar = "█" * (step_data['progress'] // 5) + "░" * (20 - (step_data['progress'] // 5))
            
            print(f"\n{step_name_display}:")
            print(f"  Progress: [{progress_bar}] {step_data['progress']}%")
            print(f"  Status: {step_data['status']}")
            if step_data['total_files'] > 0:
                print(f"  Files: {step_data['processed_files']}/{step_data['total_files']}")
        
        # Display errors and warnings
        if progress['errors']:
            print(f"\n❌ Errors ({len(progress['errors'])}):")
            for error in progress['errors'][-3:]:  # Show last 3 errors
                print(f"  - {error['message']}")
        
        if progress['warnings']:
            print(f"\n⚠️  Warnings ({len(progress['warnings'])}):")
            for warning in progress['warnings'][-3:]:  # Show last 3 warnings
                print(f"  - {warning['message']}")
        
        # Check if completed
        if progress['overall'] >= 100:
            print("\n🎉 PROCESSING COMPLETED!")
            break
        
        time.sleep(0.5)  # Update every 500ms

def main():
    """Main test function"""
    print("🧪 Progress Tracker Test")
    print("This demonstrates real progress tracking without modifying main files")
    print("\nPress Enter to start simulation...")
    input()
    
    # Start progress monitoring in separate thread
    monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
    monitor_thread.start()
    
    # Start the simulation
    simulate_google_drive_processing()
    
    # Wait for monitor to finish
    monitor_thread.join(timeout=2)
    
    print("\n✅ Test completed! Progress tracker is working correctly.")
    print("\nTo use in your main app:")
    print("1. Import: from progress_tracker import *")
    print("2. Start: start_progress()")
    print("3. Update: increment('download') or set_status('download', 'message')")
    print("4. Stop: stop_progress()")

if __name__ == "__main__":
    main()
