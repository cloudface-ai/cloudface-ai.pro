# 🚨 Troubleshooting Guide

This guide helps you resolve common issues when using **CloudFace AI**. If you encounter a problem, check this page first before seeking additional help.

## 🔍 Quick Diagnosis

### **Check System Status**
```bash
# Verify Python installation
python --version

# Check if dependencies are installed
pip list | grep -E "(flask|supabase|face-recognition|opencv)"

# Test basic functionality
python facetak_engine.py
```

### **Check Application Logs**
```bash
# Web server logs
python web_server.py 2>&1 | tee server.log

# Desktop app logs
python main_app.py 2>&1 | tee app.log
```

## 🚨 Common Issues & Solutions

### **1. Application Won't Start**

#### **Problem**: `ModuleNotFoundError` or import errors
**Solution**:
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or install manually
pip install flask supabase face-recognition opencv-python numpy python-dotenv flet
```

#### **Problem**: Port already in use
**Solution**:
```bash
# Check what's using port 8550
netstat -ano | findstr :8550  # Windows
lsof -i :8550                 # macOS/Linux

# Kill the process or change port in web_server.py
```

#### **Problem**: Permission denied errors
**Solution**:
```bash
# Use virtual environment instead of system Python
python -m venv cloudface-env
source cloudface-env/bin/activate  # macOS/Linux
cloudface-env\Scripts\activate     # Windows
```

### **2. Authentication Issues**

#### **Problem**: Google OAuth not working
**Solutions**:
1. **Check credentials in `.env`**:
   ```bash
   # Verify these values are correct
   GOOGLE_CLIENT_ID=your_actual_client_id
   GOOGLE_CLIENT_SECRET=your_actual_client_secret
   ```

2. **Verify redirect URIs** in Google Cloud Console:
   - `http://localhost:8550/auth/callback`
   - `http://127.0.0.1:8550/auth/callback`

3. **Clear browser cache and cookies**

4. **Check if Google APIs are enabled**:
   - Google+ API
   - Google Drive API

#### **Problem**: "Invalid redirect_uri" error
**Solution**:
- Add your exact callback URL to Google OAuth credentials
- Ensure no trailing slashes or typos
- Check if using `localhost` vs `127.0.0.1`

#### **Problem**: Session not persisting
**Solution**:
```python
# In web_server.py, ensure secret key is set
app.secret_key = 'your-secret-key-here'
```

### **3. Database Connection Issues**

#### **Problem**: Supabase connection failed
**Solutions**:
1. **Verify credentials in `.env`**:
   ```bash
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_actual_anon_key
   ```

2. **Check Supabase project status**:
   - Ensure project is active
   - Check billing status
   - Verify IP restrictions

3. **Test connection manually**:
   ```python
   from supabase import create_client
   url = "your_supabase_url"
   key = "your_supabase_key"
   supabase = create_client(url, key)
   result = supabase.table('faces').select('*').limit(1).execute()
   print(result)
   ```

#### **Problem**: "Table 'faces' does not exist"
**Solution**:
Run the SQL setup commands in Supabase SQL Editor:
```sql
CREATE TABLE IF NOT EXISTS faces (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    photo_reference TEXT NOT NULL,
    face_embedding JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_faces_user_id ON faces(user_id);
CREATE INDEX IF NOT EXISTS idx_faces_embedding ON faces USING GIN (face_embedding);
ALTER TABLE faces ENABLE ROW LEVEL SECURITY;
```

### **4. Face Recognition Issues**

#### **Problem**: No faces detected in photos
**Solutions**:
1. **Check photo quality**:
   - Ensure faces are clearly visible
   - Good lighting conditions
   - Front-facing faces work best

2. **Verify image format**:
   - Supported: JPG, PNG, JPEG
   - Avoid: HEIC, WebP (convert first)

3. **Check face_recognition installation**:
   ```bash
   pip uninstall face-recognition
   pip install cmake dlib face-recognition
   ```

#### **Problem**: Face recognition crashes
**Solutions**:
1. **Memory issues** - Reduce photo resolution
2. **OpenCV issues** - Reinstall OpenCV:
   ```bash
   pip uninstall opencv-python
   pip install opencv-python-headless
   ```

3. **dlib compilation issues**:
   ```bash
   # On Windows, use pre-compiled wheels
   pip install dlib-binary
   
   # On macOS/Linux
   brew install cmake  # macOS
   sudo apt-get install cmake  # Ubuntu
   ```

#### **Problem**: Slow face recognition
**Solutions**:
1. **Reduce image resolution** before processing
2. **Use GPU acceleration** if available
3. **Process photos in smaller batches**
4. **Enable local caching** for repeated searches

### **5. Photo Processing Issues**

#### **Problem**: Photos not uploading
**Solutions**:
1. **Check file size limits**:
   ```python
   # In web_server.py, increase max file size
   app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
   ```

2. **Verify file permissions**:
   ```bash
   # Ensure upload directory is writable
   chmod 755 storage/temp/selfies
   ```

3. **Check disk space**:
   ```bash
   df -h  # macOS/Linux
   dir     # Windows
   ```

#### **Problem**: Processing stuck or hanging
**Solutions**:
1. **Check for infinite loops** in processing code
2. **Add timeout handling**:
   ```python
   import signal
   
   def timeout_handler(signum, frame):
       raise TimeoutError("Processing timeout")
   
   signal.signal(signal.SIGALRM, timeout_handler)
   signal.alarm(300)  # 5 minutes timeout
   ```

3. **Monitor system resources**:
   ```bash
   top        # macOS/Linux
   tasklist   # Windows
   ```

### **6. Search Issues**

#### **Problem**: No search results
**Solutions**:
1. **Lower similarity threshold** (try 0.8 or higher)
2. **Check if photos were processed** successfully
3. **Verify face embeddings** were generated
4. **Test with known similar photos**

#### **Problem**: Search too slow
**Solutions**:
1. **Enable local caching**:
   ```python
   # In search_engine.py, prioritize cache
   cached_results = search_local_cache(user_id, selfie_embeddings)
   if cached_results:
       return cached_results
   ```

2. **Optimize database queries**:
   ```sql
   -- Add composite indexes
   CREATE INDEX idx_faces_user_threshold ON faces(user_id, face_embedding);
   ```

3. **Use approximate search** for large datasets

### **7. Performance Issues**

#### **Problem**: High memory usage
**Solutions**:
1. **Process photos in batches**:
   ```python
   BATCH_SIZE = 10
   for i in range(0, len(photos), BATCH_SIZE):
       batch = photos[i:i+BATCH_SIZE]
       process_batch(batch)
   ```

2. **Clear memory after processing**:
   ```python
   import gc
   gc.collect()
   ```

3. **Use generators** for large datasets

#### **Problem**: Slow startup
**Solutions**:
1. **Lazy load** non-critical components
2. **Optimize imports** - only import when needed
3. **Use connection pooling** for database
4. **Enable compression** for static files

### **8. Web Interface Issues**

#### **Problem**: Pages not loading
**Solutions**:
1. **Check Flask routes** in `web_server.py`
2. **Verify template files** exist in `templates/` folder
3. **Check for JavaScript errors** in browser console
4. **Verify static files** are in `public/` folder

#### **Problem**: Styling broken
**Solutions**:
1. **Check CSS file paths** in templates
2. **Verify static file serving** is configured
3. **Clear browser cache**
4. **Check for CSS syntax errors**

#### **Problem**: JavaScript not working
**Solutions**:
1. **Check browser console** for errors
2. **Verify JavaScript file paths**
3. **Check for syntax errors** in JS files
4. **Ensure jQuery/other libraries** are loaded

### **9. Desktop App Issues**

#### **Problem**: Flet app not starting
**Solutions**:
1. **Check Flet installation**:
   ```bash
   pip install --upgrade flet
   ```

2. **Verify Python version** (3.8+ required)
3. **Check for missing dependencies**
4. **Run with verbose logging**:
   ```bash
   python main_app.py --verbose
   ```

#### **Problem**: UI elements not displaying
**Solutions**:
1. **Check Flet version compatibility**
2. **Verify UI component imports**
3. **Check for layout errors**
4. **Test with minimal UI first**

### **10. Environment & Configuration Issues**

#### **Problem**: Environment variables not loading
**Solutions**:
1. **Check `.env` file location** (should be in project root)
2. **Verify file format** (no spaces around `=`)
3. **Restart application** after changing `.env`
4. **Check for typos** in variable names

#### **Problem**: Different behavior in different environments
**Solutions**:
1. **Use virtual environments** consistently
2. **Check Python version** differences
3. **Verify dependency versions** match
4. **Use requirements.txt** for consistent versions

## 🔧 Advanced Troubleshooting

### **Debug Mode**
```python
# Enable Flask debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1

# Or in code
app.debug = True
```

### **Logging Configuration**
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloudface.log'),
        logging.StreamHandler()
    ]
)
```

### **Performance Profiling**
```python
import cProfile
import pstats

def profile_function(func):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    return result
```

## 📞 Getting Additional Help

### **Before Contacting Support**
1. ✅ Check this troubleshooting guide
2. ✅ Search [GitHub Issues](https://github.com/nerdykeeda/cloudface-ai.com/issues)
3. ✅ Check application logs
4. ✅ Verify system requirements

### **When Contacting Support**
Include:
- **Error messages** (copy exactly)
- **System information** (OS, Python version)
- **Steps to reproduce** the issue
- **Application logs** if available
- **Screenshots** if relevant

### **Contact Information**
- **GitHub Issues**: [Create new issue](https://github.com/nerdykeeda/cloudface-ai.com/issues/new)
- **Email**: nerdykeeda@gmail.com
- **Response Time**: Usually within 24 hours

## 🚀 Prevention Tips

### **Regular Maintenance**
- Keep dependencies updated
- Monitor disk space and memory usage
- Regular backup of face embeddings
- Test functionality after system updates

### **Best Practices**
- Use virtual environments
- Test with small datasets first
- Monitor application performance
- Keep logs for debugging

---

**Still having issues?** Check the [Configuration](Configuration.md) page for advanced settings, or explore the [Development Setup](Development-Setup.md) for building from source.
