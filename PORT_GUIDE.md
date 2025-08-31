# Port Management Guide for Facetak Themes

## Available Ports:
- **Port 8550**: `main_app.py` (Original app)
- **Port 8551**: `retro_theme.py` (DOS + Windows 98 theme)
- **Port 8552**: `effects_demo.py` (Hacker UI effects demo)
- **Port 8553**: `ai_hunter_enhanced.py` (Enhanced AI Hunter with glitch effects)
- **Port 8554**: `ai_hunter_theme.py` (Original AI Hunter theme)

## How to Avoid Port Conflicts:

### Option 1: Kill All Python Processes
```bash
taskkill /f /im python.exe
```

### Option 2: Use Different Ports
Edit the port number in any theme file:
```python
ft.app(target=main, port=8555, view=ft.AppView.WEB_BROWSER)
```

### Option 3: Run One at a Time
- Close browser tab
- Stop current theme (Ctrl+C)
- Start new theme

## Quick Commands:
```bash
# Kill all Python processes
taskkill /f /im python.exe

# Test effects demo
python effects_demo.py

# Test enhanced AI Hunter
python ai_hunter_enhanced.py

# Test original AI Hunter
python ai_hunter_theme.py

# Test retro theme
python retro_theme.py

# Test main app
python main_app.py
```

## Current Status:
- ✅ `effects_demo.py` - Port 8552 (Hacker UI effects)
- ✅ `ai_hunter_enhanced.py` - Port 8553 (Enhanced AI Hunter)
- ⚠️ Need to add glitch.mp3 and glitch.gif to assets folder for full experience
