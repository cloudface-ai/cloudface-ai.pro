# 📥 Installation Guide

This guide will walk you through setting up **CloudFace AI** on your system. Follow these steps carefully to ensure a successful installation.

## 🎯 Prerequisites

Before you begin, make sure you have:

- **Python 3.8 or higher** installed on your system
- **Git** for cloning the repository
- **pip** (Python package installer)
- **A Supabase account** (free tier available)
- **Google OAuth API credentials** (for authentication)

### **Checking Python Version**
```bash
python --version
# or
python3 --version
```

### **Checking Git Installation**
```bash
git --version
```

## 🚀 Step-by-Step Installation

### **Step 1: Clone the Repository**

```bash
# Clone the CloudFace AI repository
git clone https://github.com/nerdykeeda/cloudface-ai.com.git

# Navigate to the project directory
cd cloudface-ai.com
```

### **Step 2: Create Virtual Environment (Recommended)**

```bash
# Create a virtual environment
python -m venv cloudface-env

# Activate the virtual environment
# On Windows:
cloudface-env\Scripts\activate

# On macOS/Linux:
source cloudface-env/bin/activate
```

### **Step 3: Install Dependencies**

```bash
# Install required packages
pip install -r requirements.txt

# If requirements.txt doesn't exist, install manually:
pip install flask
pip install supabase
pip install face-recognition
pip install opencv-python
pip install numpy
pip install python-dotenv
pip install flet
pip install requests
pip install werkzeug
```

### **Step 4: Set Up Supabase**

1. **Create a Supabase Account**
   - Go to [supabase.com](https://supabase.com)
   - Sign up for a free account
   - Create a new project

2. **Get Your Credentials**
   - Go to Project Settings → API
   - Copy your Project URL and anon/public key

3. **Set Up Database Tables**
   - Go to SQL Editor in your Supabase dashboard
   - Run the following SQL commands:

```sql
-- Create faces table
CREATE TABLE IF NOT EXISTS faces (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    photo_reference TEXT NOT NULL,
    face_embedding JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_faces_user_id ON faces(user_id);
CREATE INDEX IF NOT EXISTS idx_faces_embedding ON faces USING GIN (face_embedding);

-- Enable Row Level Security
ALTER TABLE faces ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for users to access their own data
CREATE POLICY "Users can access their own faces" ON faces
    FOR ALL USING (auth.jwt() ->> 'email' = user_id);
```

### **Step 5: Set Up Google OAuth**

1. **Go to Google Cloud Console**
   - Visit [console.cloud.google.com](https://console.cloud.google.com)
   - Create a new project or select existing one

2. **Enable APIs**
   - Go to APIs & Services → Library
   - Enable "Google+ API" and "Google Drive API"

3. **Create OAuth Credentials**
   - Go to APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8550/auth/callback`
     - `http://127.0.0.1:8550/auth/callback`

4. **Get Your Credentials**
   - Copy the Client ID and Client Secret

### **Step 6: Configure Environment Variables**

```bash
# Copy the example environment file
cp example.env .env

# Edit the .env file with your credentials
```

**Edit `.env` file with your actual values:**
```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Flask Configuration
FLASK_SECRET_KEY=your_random_secret_key
FLASK_ENV=development
```

### **Step 7: Test the Installation**

```bash
# Test the face recognition engine
python facetak_engine.py

# Test the search engine
python search_engine.py

# Test photo processing
python process_photos.py
```

## 🧪 Verification

### **Check if Everything is Working**

1. **Start the Web Server**
   ```bash
   python web_server.py
   ```

2. **Open Your Browser**
   - Go to `http://localhost:8550`
   - You should see the CloudFace AI landing page

3. **Test Authentication**
   - Click "Sign in with Google"
   - Complete the OAuth flow
   - You should be redirected back to the app

## 🚨 Common Installation Issues

### **Python Version Issues**
```bash
# If you get "python command not found"
python3 --version
# Use python3 instead of python in all commands
```

### **Permission Issues (Linux/macOS)**
```bash
# If you get permission errors
sudo pip install -r requirements.txt
# Or better, use virtual environment
```

### **OpenCV Installation Issues**
```bash
# If face-recognition fails to install
pip install cmake
pip install dlib
pip install face-recognition
```

### **Supabase Connection Issues**
- Verify your URL and key are correct
- Check if your Supabase project is active
- Ensure the faces table was created successfully

## 🔧 Post-Installation Setup

### **Create Test Photos Directory**
```bash
# Create a directory for test photos
mkdir test_photos

# Add some test images to test_photos/
# (JPG, PNG, JPEG formats supported)
```

### **Set Up Local Storage**
```bash
# Create storage directories
mkdir -p storage/cache
mkdir -p storage/data
mkdir -p storage/temp/selfies
```

## 📱 Next Steps

After successful installation:

1. **Read the [Quick Start Tutorial](Quick-Start-Tutorial.md)** to learn basic usage
2. **Explore the [Web Application Guide](Web-Application-Guide.md)** for detailed features
3. **Check [Configuration](Configuration.md)** for advanced settings
4. **Visit [Troubleshooting](Troubleshooting.md)** if you encounter issues

## 🆘 Need Help?

If you encounter any issues during installation:

- **Check the [Troubleshooting](Troubleshooting.md)** page
- **Search [GitHub Issues](https://github.com/nerdykeeda/cloudface-ai.com/issues)**
- **Email support**: nerdykeeda@gmail.com

---

**🎉 Congratulations!** You've successfully installed CloudFace AI. Now let's get started with the [Quick Start Tutorial](Quick-Start-Tutorial.md)!
