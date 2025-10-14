# 🚀 Deploy CloudFace Pro to GitHub

## Quick Setup Guide

---

## 📋 **Your Repository**

```
HTTPS: https://github.com/cloudface-ai/cloudface-ai.pro.git
SSH:   git@github.com:cloudface-ai/cloudface-ai.pro.git
```

---

## 🔧 **Step 1: Initial Git Setup** (5 minutes)

### **On Your Mac:**

```bash
cd /Volumes/MAC-Studio/cloudface_ai

# Check git status
git status

# Add remote (use SSH for easier push)
git remote add origin git@github.com:cloudface-ai/cloudface-ai.pro.git

# Or if using HTTPS:
# git remote add origin https://github.com/cloudface-ai/cloudface-ai.pro.git

# Verify remote
git remote -v
```

---

## 📦 **Step 2: Prepare Files for Commit**

```bash
# Add core files
git add cloudface_pro_*.py
git add real_face_recognition_engine.py
git add cleanup_vps_storage.py

# Add config & docs
git add requirements.txt
git add README.md
git add LICENSE
git add PROJECT_STRUCTURE.md
git add .gitignore

# Add templates & static
git add templates/
git add static/

# Add documentation
git add docs/

# Check what will be committed
git status
```

---

## 💾 **Step 3: Commit & Push**

```bash
# Commit
git commit -m "CloudFace Pro - Production Ready

Features:
- Admin & Guest authentication with email verification
- AI face recognition (InsightFace)
- Real-time photo search
- Pricing & subscription system
- Event management
- Watermark support
- Guest dashboard
- Complete access control

Ready for deployment to pro.cloudface-ai.com"

# Push to GitHub
git push -u origin main

# If branch is 'master' instead of 'main':
# git branch -M main
# git push -u origin main
```

---

## 🖥️ **Step 4: Deploy on VPS**

### **SSH to Your VPS:**

```bash
ssh root@YOUR_VPS_IP
```

### **Clone Repository:**

```bash
# Navigate to web directory
cd /var/www

# Clone from GitHub
git clone git@github.com:cloudface-ai/cloudface-ai.pro.git cloudface-pro

# Or using HTTPS:
# git clone https://github.com/cloudface-ai/cloudface-ai.pro.git cloudface-pro

cd cloudface-pro
```

### **Setup Python Environment:**

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create storage directories
mkdir -p storage/cloudface_pro/events
mkdir -p storage/cloudface_pro/guests

# Set permissions
chown -R www-data:www-data storage/
```

### **Configure Environment:**

```bash
# Create .env file
nano .env

# Add these:
TESTING_MODE=false
SECRET_KEY=your-secret-random-key-here
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=noreply@cloudface-ai.com

# Save (Ctrl+X, Y, Enter)
chmod 600 .env
```

### **Download AI Models:**

```bash
# This creates ~/.insightface/models/buffalo_l/
python -c "
from real_face_recognition_engine import RealFaceRecognitionEngine
engine = RealFaceRecognitionEngine()
print('✅ Models downloaded')
"
```

---

## 🔄 **Future Updates** (Super Easy!)

### **On Your Mac (Make Changes):**

```bash
cd /Volumes/MAC-Studio/cloudface_ai

# Make your changes...

# Commit and push
git add .
git commit -m "Description of changes"
git push origin main
```

### **On VPS (Deploy Changes):**

```bash
ssh root@YOUR_VPS_IP

cd /var/www/cloudface-pro
git pull origin main
systemctl restart cloudface-pro

# Done! (Takes 10 seconds)
```

---

## 🔑 **SSH Key Setup** (For Easier Git)

### **Generate SSH Key on VPS:**

```bash
# On VPS
ssh-keygen -t ed25519 -C "cloudface-pro-vps"

# Copy public key
cat ~/.ssh/id_ed25519.pub
```

### **Add to GitHub:**

1. Go to: https://github.com/cloudface-ai/cloudface-ai.pro
2. Settings → Deploy keys
3. Add new deploy key
4. Paste public key
5. ✅ Allow write access (if you want to push from VPS)

---

## 📊 **What Gets Committed to GitHub**

### **✅ Included:**
- All `cloudface_pro_*.py` files
- `real_face_recognition_engine.py`
- `requirements.txt`
- `README.md`, `LICENSE`
- `templates/` folder
- `static/` folder
- `docs/` folder

### **❌ Excluded (.gitignore):**
- `storage/` - User data (sensitive)
- `.env` - Secrets & API keys
- `__pycache__/` - Python cache
- `old_scripts/` - Not needed
- `old_batch_files/` - Not needed
- `models/` - Too large (download on VPS)
- `*.log` - Log files

---

## 🎯 **Quick Command Reference**

### **First Time Push:**
```bash
git remote add origin git@github.com:cloudface-ai/cloudface-ai.pro.git
git add cloudface_pro_*.py real_face_recognition_engine.py requirements.txt README.md LICENSE templates/ static/ docs/ .gitignore
git commit -m "CloudFace Pro - Initial commit"
git push -u origin main
```

### **Deploy on VPS:**
```bash
cd /var/www
git clone git@github.com:cloudface-ai/cloudface-ai.pro.git cloudface-pro
cd cloudface-pro
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Update (After Changes):**
```bash
# Local
git push origin main

# VPS
git pull origin main && systemctl restart cloudface-pro
```

---

## ✨ **Recommendation**

**Use Git deployment!** 

**Advantages:**
- 🔄 Updates in 10 seconds
- 🔒 Secure (SSH keys)
- 📊 Track all changes
- ⏮️ Easy rollback
- 🤝 Professional workflow

**Ready to push to GitHub?** The `.gitignore` is set up, just run the git commands! 🚀
