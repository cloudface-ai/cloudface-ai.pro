@echo off
echo ========================================
echo    FACETAK - KILLING ALL SERVERS
echo ========================================
echo.

echo Stopping all Facetak servers...
echo.

echo [1/3] Stopping Python processes on Facetak ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :855') do (
    echo Stopping process on port 855%%a
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo [2/3] Force killing all Python processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1

echo.
echo [3/3] Cleaning up any remaining processes...
wmic process where "name='python.exe'" delete >nul 2>&1
wmic process where "name='pythonw.exe'" delete >nul 2>&1

echo.
echo ========================================
echo    ALL SERVERS STOPPED!
echo ========================================
echo.
echo All Facetak servers have been terminated.
echo You can now run 'start_all_servers.bat' to restart them.
echo.
pause
