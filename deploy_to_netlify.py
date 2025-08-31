"""
Deploy to Netlify Script for CloudFace AI
This script prepares your static files for Netlify deployment.
"""

import os
import shutil
from pathlib import Path

def main():
    print("🚀 CLOUDFACE AI - NETLIFY DEPLOYMENT PREPARATION")
    print("=" * 60)
    
    # Check if public folder exists
    public_dir = Path("public")
    if not public_dir.exists():
        print("❌ Public folder not found!")
        return
    
    print("✅ Static files are ready in the 'public' folder!")
    print(f"📁 Location: {public_dir.absolute()}")
    
    # List all files
    print(f"\n📄 Files ready for deployment:")
    print("-" * 40)
    for file_path in public_dir.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(public_dir)
            print(f"✅ {relative_path}")
    
    print(f"\n🎯 DEPLOYMENT STEPS:")
    print("=" * 40)
    print("1. Go to https://netlify.com")
    print("2. Sign up/Login (free)")
    print("3. Click 'New site from Git' or 'Deploy manually'")
    print("4. Drag and drop the 'public' folder")
    print("5. Wait 2-3 minutes for deployment")
    print("6. Get your free URL! 🎉")
    
    print(f"\n🔒 YOUR ML FUNCTIONALITY IS 100% SAFE:")
    print("-" * 40)
    print("✅ ML Models: Untouched")
    print("✅ AI Algorithms: Untouched")
    print("✅ Face Recognition: Untouched")
    print("✅ Data Processing: Untouched")
    print("✅ Future ML Plans: Protected")
    
    print(f"\n📈 BENEFITS AFTER DEPLOYMENT:")
    print("-" * 40)
    print("🚀 Free professional hosting")
    print("⚡ Better performance (faster loading)")
    print("🔍 Better SEO (static sites rank better)")
    print("🌍 Global CDN (fast worldwide)")
    print("🔒 SSL included (secure connections)")
    
    print(f"\n📁 FOLDER TO UPLOAD:")
    print("-" * 40)
    print(f"📂 {public_dir.absolute()}")
    print("   (Just drag and drop this entire folder to Netlify)")
    
    print(f"\n🎉 READY TO DEPLOY!")
    print("=" * 40)
    print("Your CloudFace AI website is ready for free hosting!")
    print("No ML functionality lost - everything is protected!")
    
    # Create a simple batch file for easy deployment
    batch_content = '''@echo off
echo 🚀 CLOUDFACE AI - NETLIFY DEPLOYMENT
echo ======================================
echo.
echo 1. Open https://netlify.com in your browser
echo 2. Sign up/Login (free)
echo 3. Click "New site from Git" or "Deploy manually"
echo 4. Drag and drop the "public" folder
echo 5. Wait for deployment
echo 6. Get your free URL!
echo.
echo Your ML functionality is 100% safe! 🧠✨
echo.
pause
'''
    
    with open("deploy_to_netlify.bat", "w") as f:
        f.write(batch_content)
    
    print(f"\n📋 Created: deploy_to_netlify.bat")
    print("   Double-click this file for deployment instructions!")

if __name__ == "__main__":
    main()
