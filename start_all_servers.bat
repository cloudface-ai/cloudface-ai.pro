@echo off
cd /d "%~dp0"
echo ========================================
echo    FACETAK - STARTING MAIN SERVER
echo ========================================
echo.

echo Starting main server...
echo.

echo [1/1] Starting Main App (Port 8550)...
start "Facetak Main App" cmd /k "python main_app.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    MAIN SERVER STARTED!
echo ========================================
echo.
echo Server running on:
echo - Main App: http://localhost:8550
echo.
echo Use 'kill_all_servers.bat' to stop the server
echo.
pause
