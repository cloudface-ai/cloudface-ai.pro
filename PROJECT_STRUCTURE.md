# 📁 CloudFace Pro - Clean Project Structure

## ✅ Organized and Production-Ready

---

## 🎯 **Core Application** (11 files)

### **Main Server:**
- `cloudface_pro_server.py` - Flask web server, routes, API endpoints

### **Authentication:**
- `cloudface_pro_auth.py` - Admin authentication
- `cloudface_pro_guest_auth.py` - Guest authentication

### **Business Logic:**
- `cloudface_pro_events.py` - Event management
- `cloudface_pro_processor.py` - Photo processing pipeline
- `cloudface_pro_pricing.py` - Subscription & limits
- `cloudface_pro_email.py` - Email verification & notifications

### **Infrastructure:**
- `cloudface_pro_storage.py` - Storage abstraction layer
- `cloudface_pro_watermark.py` - Watermark processing
- `cloudface_pro_config.py` - Configuration & settings

### **AI Engine:**
- `real_face_recognition_engine.py` - InsightFace integration

---

## 📂 **Directory Structure**

```
/Volumes/MAC-Studio/cloudface_ai/
│
├── 🔧 CORE FILES (11 Python modules)
│   └── cloudface_pro_*.py + real_face_recognition_engine.py
│
├── 📄 CONFIGURATION
│   ├── requirements.txt      # Python dependencies
│   ├── README.md             # Project documentation
│   └── LICENSE               # MIT License
│
├── 🎨 TEMPLATES
│   └── templates/cloudface_pro/
│       ├── landing.html           # Landing page
│       ├── login.html             # Admin login
│       ├── signup.html            # Admin signup
│       ├── verify_email.html      # Email verification
│       ├── dashboard.html         # Admin dashboard
│       ├── create_event.html      # Create event
│       ├── view_event.html        # Event details
│       ├── upload_photos.html     # Photo upload
│       ├── pricing.html           # Pricing plans
│       ├── guest_login.html       # Guest login
│       ├── guest_signup.html      # Guest signup
│       ├── guest_dashboard.html   # Guest events
│       ├── capture_selfie.html    # Selfie capture
│       ├── public_event.html      # Event search page
│       └── base.html              # Base template
│
├── 💾 STORAGE (Runtime data)
│   └── storage/cloudface_pro/
│       ├── events/               # Event photos & data
│       ├── guests/               # Guest selfies
│       ├── users_db.json         # Admin accounts
│       ├── guests_db.json        # Guest accounts
│       ├── events_db.json        # Events
│       └── subscriptions_db.json # Pricing plans
│
├── 📚 DOCUMENTATION
│   └── docs/
│       ├── guides/               # Implementation guides
│       │   ├── ACCESS_CONTROL_SYSTEM.md
│       │   ├── ROUTING_STRUCTURE.md
│       │   ├── GUEST_LOGIN_GUIDE.md
│       │   ├── PRICING_SYSTEM_COMPLETE.md
│       │   └── EMAIL_VERIFICATION_SYSTEM.md
│       ├── email-previews/       # Email template previews
│       │   ├── EMAIL_PREVIEW_VERIFICATION.html
│       │   └── EMAIL_PREVIEW_WELCOME.html
│       ├── DEPLOYMENT_GUIDE_PRO_SUBDOMAIN.md
│       └── archive/              # Old documentation
│
├── 🗂️ ARCHIVED (Old files)
│   ├── old_scripts/             # Legacy Python scripts
│   ├── old_batch_files/         # Windows batch files
│   ├── blog_templates/          # Blog content
│   └── wiki/                    # Old wiki
│
├── 🖼️ STATIC ASSETS
│   ├── static/                  # Static files (logo, etc.)
│   └── assets/                  # Other assets
│
└── 📋 OTHER
    ├── .htaccess               # Apache config (if needed)
    └── build/                  # Build artifacts
```

---

## 🚀 **Essential Files for Deployment**

### **Must Deploy:**
```
✅ cloudface_pro_*.py (10 files)
✅ real_face_recognition_engine.py
✅ requirements.txt
✅ templates/cloudface_pro/
✅ static/
```

### **Not Needed on Server:**
```
❌ docs/
❌ old_scripts/
❌ old_batch_files/
❌ blog_templates/
❌ wiki/
❌ __pycache__/
❌ build/
```

---

## 📊 **File Count Summary**

| Category | Count | Location |
|----------|-------|----------|
| Core Python Files | 11 | Root directory |
| Templates | 15+ | templates/cloudface_pro/ |
| Documentation | 10+ | docs/ |
| Old Scripts | 15+ | old_scripts/ |
| Old Batch Files | 8+ | old_batch_files/ |

**Total Core Files:** ~26 (clean and focused!)

---

## 🎯 **Quick Access**

### **Start Server:**
```bash
cd /Volumes/MAC-Studio/cloudface_ai
python cloudface_pro_server.py
```

### **View Docs:**
```bash
open docs/guides/
open docs/email-previews/
open docs/DEPLOYMENT_GUIDE_PRO_SUBDOMAIN.md
```

### **View Email Templates:**
```bash
open docs/email-previews/EMAIL_PREVIEW_VERIFICATION.html
open docs/email-previews/EMAIL_PREVIEW_WELCOME.html
```

---

## ✨ **Project Status**

✅ **Core App:** Complete and working  
✅ **Documentation:** Organized in docs/  
✅ **Old Files:** Archived (safe to delete later)  
✅ **Clean Structure:** Production ready  
✅ **Easy to Navigate:** Clear folder names  

---

## 🚀 **Next Steps**

1. **Test locally:** Everything still works
2. **Deploy to:** `pro.cloudface-ai.com`
3. **Archive cleanup:** Delete old_* folders if not needed
4. **Go live!** 🎉

---

**Status:** ✅ Project Cleaned & Organized  
**Ready for:** Deployment  
**Last Updated:** October 14, 2025

