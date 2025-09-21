@echo off
title Facetak App Deployment Tool
color 0A
echo.
echo  ███████╗ █████╗  ██████╗███████╗████████╗ █████╗ ██╗  ██╗
echo  ██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██║ ██╔╝
echo  █████╗  ███████║██║     █████╗     ██║   ███████║█████╔╝ 
echo  ██╔══╝  ██╔══██║██║     ██╔══╝     ██║   ██╔══██║██╔═██╗ 
echo  ██║     ██║  ██║╚██████╗███████╗   ██║   ██║  ██║██║  ██╗
echo  ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
echo.
echo  🚀 Professional Face Recognition App Deployment
echo  🎯 FBI-Grade Accuracy • Lightning Fast • Smart Caching
echo.

REM Check if this is a fresh deployment
if not exist requirements.txt (
    echo ❌ Error: This doesn't appear to be a Facetak app directory
    echo Please run this script from the extracted Facetak backup folder
    pause
    exit /b 1
)

echo 📋 Deployment Checklist:
echo.

REM Step 1: Check Python
echo [1/6] 🐍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+ first
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version') do echo ✅ Python %%i detected
)

REM Step 2: Install dependencies
echo.
echo [2/6] 📦 Installing Python dependencies...
echo This may take a few minutes for first-time setup...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Dependency installation failed
    pause
    exit /b 1
) else (
    echo ✅ All dependencies installed successfully
)

REM Step 3: Create directories
echo.
echo [3/6] 📁 Creating necessary directories...
if not exist storage mkdir storage
if not exist storage\downloads mkdir storage\downloads
if not exist storage\temp mkdir storage\temp
if not exist storage\temp\selfies mkdir storage\temp\selfies
if not exist storage\cache mkdir storage\cache
if not exist storage\search_cache mkdir storage\search_cache
if not exist storage\folder_cache mkdir storage\folder_cache
if not exist models mkdir models
echo ✅ Directory structure created

REM Step 4: Check configuration
echo.
echo [4/6] ⚙️  Checking configuration...
if exist .env (
    echo ✅ Environment file (.env) found
) else (
    if exist example.env (
        echo ⚠️  Copying example.env to .env - PLEASE CONFIGURE YOUR CREDENTIALS
        copy example.env .env >nul
        echo ❗ IMPORTANT: Edit .env file with your Google OAuth credentials
    ) else (
        echo ❌ No environment configuration found
        echo Please create .env file with your Google OAuth credentials
    )
)

REM Step 5: Check Firebase credentials
echo.
echo [5/6] 🔑 Checking Firebase credentials...
if exist credentials\firebase-adminsdk.json (
    echo ✅ Firebase admin credentials found
) else (
    echo ⚠️  Firebase admin credentials not found
    echo Place your firebase-adminsdk.json in credentials\ folder
)

REM Step 6: Ready to launch
echo.
echo [6/6] 🚀 Deployment Summary:
echo.
echo ✅ Python environment ready
echo ✅ Dependencies installed  
echo ✅ Directory structure created
if exist .env (echo ✅ Configuration file ready) else (echo ⚠️  Configuration needs setup)
if exist credentials\firebase-adminsdk.json (echo ✅ Firebase credentials ready) else (echo ⚠️  Firebase credentials needed)
echo.

echo 🎯 Next Steps:
echo 1. Configure .env file with your Google OAuth credentials
echo 2. Add Firebase credentials to credentials\firebase-adminsdk.json
echo 3. Run: python web_server.py
echo 4. Open: http://localhost:8550
echo.

echo 🌟 Your Facetak app is ready to launch!
echo Press any key to start the server, or Ctrl+C to exit and configure first...
pause

REM Start the server
echo.
echo 🚀 Starting Facetak server...
echo 🌐 Open http://localhost:8550 in your browser
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Set UTF-8 encoding for emoji support
chcp 65001 >nul

REM Set environment variables if Firebase credentials exist
if exist credentials\firebase-adminsdk.json (
    set GOOGLE_APPLICATION_CREDENTIALS=credentials\firebase-adminsdk.json
    set FIREBASE_PROJECT_ID=cloudface-ai
)

REM Launch the app
python web_server.py
