# 🎯 CloudFace Pro - AI-Powered Event Photography Platform

**Professional photo delivery system with AI face recognition**

---

## 🚀 **Quick Start**

### **Run Locally:**
```bash
cd /Volumes/MAC-Studio/cloudface_ai
python cloudface_pro_server.py
```

Visit: `http://localhost:5002`

---

## 📁 **Project Structure**

### **Core Application Files:**
```
cloudface_pro_server.py        # Main Flask server
cloudface_pro_auth.py          # Admin authentication
cloudface_pro_guest_auth.py    # Guest authentication
cloudface_pro_events.py        # Event management
cloudface_pro_processor.py     # Photo processing & AI
cloudface_pro_storage.py       # Storage abstraction
cloudface_pro_pricing.py       # Pricing & limits
cloudface_pro_email.py         # Email verification & notifications
cloudface_pro_watermark.py     # Watermark processing
cloudface_pro_config.py        # Configuration
real_face_recognition_engine.py # InsightFace AI engine
```

### **Templates:**
```
templates/cloudface_pro/
├── landing.html           # Landing page
├── login.html             # Admin login
├── signup.html            # Admin signup
├── verify_email.html      # Email verification
├── dashboard.html         # Admin dashboard
├── create_event.html      # Create event
├── view_event.html        # Event details
├── upload_photos.html     # Photo upload
├── pricing.html           # Pricing plans
├── guest_login.html       # Guest login
├── guest_signup.html      # Guest signup
├── guest_dashboard.html   # Guest dashboard
├── capture_selfie.html    # Selfie capture
└── public_event.html      # Public event page
```

### **Storage:**
```
storage/cloudface_pro/
├── events/                # Event data & photos
├── guests/                # Guest selfies
├── users_db.json          # Admin accounts
├── guests_db.json         # Guest accounts
├── events_db.json         # Events database
└── subscriptions_db.json  # Pricing subscriptions
```

### **Documentation:**
```
docs/
├── guides/                # Implementation guides
│   ├── ACCESS_CONTROL_SYSTEM.md
│   ├── ROUTING_STRUCTURE.md
│   ├── GUEST_LOGIN_GUIDE.md
│   ├── PRICING_SYSTEM_COMPLETE.md
│   └── EMAIL_VERIFICATION_SYSTEM.md
├── email-previews/        # Email template previews
└── archive/               # Old docs & files
```

### **Old Files (Archived):**
```
old_scripts/               # Legacy Python scripts
old_batch_files/           # Windows batch files
blog_templates/            # Blog content (for main site)
wiki/                      # Documentation
```

---

## 🎯 **Key Features**

### **Admin Side:**
- ✅ Event creation & management
- ✅ Photo upload with AI face detection
- ✅ Watermark customization
- ✅ Analytics dashboard
- ✅ Pricing plans & limits
- ✅ Email verification

### **Guest Side:**
- ✅ Guest login/signup
- ✅ Selfie capture & storage
- ✅ AI face search (real-time streaming)
- ✅ Auto-save found photos
- ✅ Lightbox gallery
- ✅ Download with watermarks
- ✅ AI feedback system

### **Technology:**
- 🤖 **AI:** InsightFace (RetinaFace + ArcFace)
- 🔍 **Search:** FAISS vector search
- 🖼️ **Images:** PIL, OpenCV, NumPy
- 🌐 **Backend:** Python Flask
- 🎨 **Frontend:** HTML, CSS, JavaScript
- 💾 **Storage:** Local VPS (scalable to cloud)

---

## 🌐 **Deployment**

### **Recommended:** IONOS VPS + Cloudflare

**Domain Structure:**
```
cloudface-ai.com         → Main website (current)
pro.cloudface-ai.com     → CloudFace Pro (this app)
```

**See:** `docs/guides/` for deployment guides

---

## 📊 **Pricing**

- **Personal:** ₹4,999/year - 20GB, 100K photos
- **Professional:** ₹9,999/year - 50GB, 250K photos
- **Business:** ₹16,999/year - 100GB, 600K photos
- **Enterprise:** Contact - Unlimited

**Guests:** FREE (admin pays)

---

## 🔐 **Access Control**

### **Admin Routes:** `/admin/*`
- Dashboard, events, pricing
- Requires admin authentication
- Ownership verification

### **Guest Routes:** `/guest/*`
- Login, dashboard, my events
- Requires guest authentication
- Event-specific access

### **Public Routes:** `/e/*`
- Event pages (shareable)
- No authentication required
- Face search & download

---

## 📧 **Email System**

### **Testing Mode:** (Current)
- Emails printed to terminal
- No SMTP required
- Full flow testing

### **Production Mode:**
```bash
export SMTP_SERVER="smtp.sendgrid.net"
export SMTP_USER="apikey"
export SMTP_PASSWORD="your-api-key"
export TESTING_MODE="false"
```

---

## 📝 **Environment Variables**

```bash
# Mode
export TESTING_MODE="true"          # true = local, false = production

# Email (Production only)
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export FROM_EMAIL="noreply@cloudface.pro"

# Server
export PORT="5002"
export HOST="0.0.0.0"
```

---

## 🛠️ **Development**

### **Install Dependencies:**
```bash
pip install -r requirements.txt
```

### **Run Server:**
```bash
python cloudface_pro_server.py
```

### **Access Points:**
- Admin: `http://localhost:5002/admin/login`
- Guest: `http://localhost:5002/guest/login`
- Landing: `http://localhost:5002/`

---

## 📱 **Contact**

- **Email:** support@cloudface.pro
- **Phone:** +91 98765 43210
- **Website:** https://pro.cloudface-ai.com (when deployed)

---

## 📄 **License**

See `LICENSE` file

---

**Built with ❤️ using Python, Flask, and InsightFace**  
**Version:** 1.0.0  
**Last Updated:** October 14, 2025

