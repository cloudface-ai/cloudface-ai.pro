@echo off
title Facetak App Backup Tool
echo 🚀 Facetak Quick Backup Tool

REM Get timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,8%_%dt:~8,6%"

REM Create backup directory
set "backup_dir=D:\Backups\Facetak_%timestamp%"
echo 📁 Creating backup: %backup_dir%

REM Use robocopy for professional backup
echo 📋 Copying files with robocopy...
robocopy "." "%backup_dir%" /MIR /XD node_modules __pycache__ build storage\downloads storage\temp /XF *.log *.tmp /R:3 /W:1

REM Create ZIP archive
echo 📦 Creating ZIP archive...
powershell -Command "Compress-Archive -Path '%backup_dir%\*' -DestinationPath '%backup_dir%.zip' -Force"

REM Create backup info
echo # Facetak App Backup > "%backup_dir%\BACKUP_INFO.txt"
echo Created: %date% %time% >> "%backup_dir%\BACKUP_INFO.txt"
echo Version: Face Recognition V2 with Real Engine >> "%backup_dir%\BACKUP_INFO.txt"
echo Features: FAISS search, Smart caching, Progress tracking >> "%backup_dir%\BACKUP_INFO.txt"
echo. >> "%backup_dir%\BACKUP_INFO.txt"
echo Deployment: >> "%backup_dir%\BACKUP_INFO.txt"
echo 1. Extract to target location >> "%backup_dir%\BACKUP_INFO.txt"
echo 2. Run: pip install -r requirements.txt >> "%backup_dir%\BACKUP_INFO.txt"
echo 3. Configure .env file >> "%backup_dir%\BACKUP_INFO.txt"
echo 4. Run: python web_server.py >> "%backup_dir%\BACKUP_INFO.txt"

echo.
echo ✅ Backup completed successfully!
echo 📂 Directory: %backup_dir%
echo 📦 ZIP: %backup_dir%.zip
echo.
echo 🚀 To deploy elsewhere:
echo 1. Copy the ZIP file
echo 2. Extract and run: pip install -r requirements.txt
echo 3. Configure .env file
echo 4. Run: python web_server.py
echo.
pause
