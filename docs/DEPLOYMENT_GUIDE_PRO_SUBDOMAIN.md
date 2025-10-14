# 🚀 Deployment Guide: pro.cloudface-ai.com

## Complete guide to deploy CloudFace Pro on subdomain

---

## 📋 **Prerequisites**

- ✅ Domain: `cloudface-ai.com` (you already have this)
- ✅ Cloudflare account (for DNS & CDN)
- ⬜ IONOS VPS L server ($10-12/month)
- ⬜ SSH access to VPS

---

## 🎯 **Architecture**

```
cloudface-ai.com
    ↓ (DNS A record)
    Server 1 (Your current site)

pro.cloudface-ai.com  
    ↓ (DNS A record)
    Server 2 (IONOS VPS - CloudFace Pro)
        ↓
    Nginx → Flask (port 5002) → CloudFace Pro
```

---

## 📝 **Step-by-Step Deployment**

### **STEP 1: Buy IONOS VPS** (5 minutes)

1. Go to: https://www.ionos.com/hosting/vps-hosting
2. Select: **VPS L**
   - 4 vCores CPU
   - 8 GB RAM
   - 240 GB SSD
   - Price: ~$10-12/month
3. Choose: **Ubuntu 22.04 LTS**
4. Complete purchase
5. Save SSH credentials

---

### **STEP 2: DNS Setup in Cloudflare** (2 minutes)

1. Login to Cloudflare
2. Select domain: `cloudface-ai.com`
3. Go to **DNS** section
4. Add A record:
   ```
   Type: A
   Name: pro
   IPv4: [Your IONOS VPS IP]
   Proxy: ✅ Proxied (Orange cloud)
   TTL: Auto
   ```
5. Save

**DNS will propagate in 5-30 minutes**

---

### **STEP 3: Connect to VPS** (2 minutes)

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y
```

---

### **STEP 4: Install Dependencies** (10 minutes)

```bash
# Install Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# Install Nginx
apt install -y nginx

# Install system dependencies for OpenCV & InsightFace
apt install -y libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx

# Install Git
apt install -y git

# Install certbot for SSL (optional, Cloudflare provides SSL)
apt install -y certbot python3-certbot-nginx
```

---

### **STEP 5: Upload Code** (5 minutes)

**Option A: Git (Recommended)**
```bash
cd /var/www
git clone https://github.com/your-repo/cloudface_ai.git cloudface-pro
cd cloudface-pro
```

**Option B: SCP Upload**
```bash
# On your Mac:
scp -r /Volumes/MAC-Studio/cloudface_ai root@your-vps-ip:/var/www/cloudface-pro
```

---

### **STEP 6: Setup Python Environment** (5 minutes)

```bash
cd /var/www/cloudface-pro

# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Download InsightFace models
python setup_real_face_recognition.py
```

---

### **STEP 7: Configure Environment** (3 minutes)

```bash
# Create .env file
cat > /var/www/cloudface-pro/.env << 'EOF'
TESTING_MODE=false
SECRET_KEY=your-secret-key-here-change-this
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=noreply@cloudface-ai.com
PORT=5002
HOST=127.0.0.1
EOF

# Set permissions
chmod 600 .env
```

---

### **STEP 8: Create Systemd Service** (3 minutes)

```bash
# Create service file
cat > /etc/systemd/system/cloudface-pro.service << 'EOF'
[Unit]
Description=CloudFace Pro - AI Event Photography
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/cloudface-pro
Environment="PATH=/var/www/cloudface-pro/venv/bin"
EnvironmentFile=/var/www/cloudface-pro/.env
ExecStart=/var/www/cloudface-pro/venv/bin/python cloudface_pro_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set permissions on storage
chown -R www-data:www-data /var/www/cloudface-pro/storage

# Enable and start service
systemctl enable cloudface-pro
systemctl start cloudface-pro

# Check status
systemctl status cloudface-pro
```

---

### **STEP 9: Configure Nginx** (5 minutes)

```bash
# Create Nginx config
cat > /etc/nginx/sites-available/cloudface-pro << 'EOF'
server {
    listen 80;
    server_name pro.cloudface-ai.com;
    
    client_max_body_size 500M;  # Allow large photo uploads
    
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # For file uploads
        proxy_request_buffering off;
        proxy_buffering off;
        
        # Timeouts for long processing
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/cloudface-pro /etc/nginx/sites-enabled/

# Test config
nginx -t

# Reload Nginx
systemctl reload nginx
```

---

### **STEP 10: Firewall Setup** (2 minutes)

```bash
# Allow HTTP, HTTPS, SSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable

# Check status
ufw status
```

---

### **STEP 11: Test Deployment** (1 minute)

```bash
# Check if Flask is running
curl http://localhost:5002

# Check Nginx
curl http://pro.cloudface-ai.com
```

---

## ✅ **Verification Checklist**

After deployment, verify:

- [ ] DNS resolves: `ping pro.cloudface-ai.com`
- [ ] Site loads: `https://pro.cloudface-ai.com`
- [ ] SSL works (Cloudflare provides)
- [ ] Admin login works: `https://pro.cloudface-ai.com/admin/login`
- [ ] Guest login works: `https://pro.cloudface-ai.com/guest/login`
- [ ] Photo upload works
- [ ] Face search works
- [ ] Email verification works (if SMTP configured)

---

## 🔒 **SSL/HTTPS**

### **Option 1: Cloudflare SSL (Recommended - Free)**
- Already enabled if using Cloudflare proxy
- No configuration needed
- Auto-renews

### **Option 2: Let's Encrypt (Alternative)**
```bash
certbot --nginx -d pro.cloudface-ai.com
```

---

## 📊 **Monitoring**

### **Check Logs:**
```bash
# Flask app logs
journalctl -u cloudface-pro -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### **Restart Service:**
```bash
systemctl restart cloudface-pro
```

---

## 🔄 **Updates & Maintenance**

### **Deploy New Version:**
```bash
cd /var/www/cloudface-pro
git pull origin main  # or upload new files
systemctl restart cloudface-pro
```

### **Backup Data:**
```bash
# Backup storage folder
tar -czf backup-$(date +%Y%m%d).tar.gz storage/

# Download to local
scp root@vps-ip:/var/www/cloudface-pro/backup-*.tar.gz ~/Downloads/
```

---

## 💰 **Estimated Costs**

| Service | Cost | Notes |
|---------|------|-------|
| IONOS VPS L | $10-12/mo | Server hosting |
| Cloudflare | FREE | DNS, CDN, SSL |
| Domain | $0 | Already own cloudface-ai.com |
| SendGrid | FREE | 100 emails/day free tier |
| **Total** | **~$12/mo** | Very affordable! |

---

## 🎯 **Final URLs**

After deployment:

### **Production URLs:**
```
https://pro.cloudface-ai.com/                 → Landing
https://pro.cloudface-ai.com/admin/login      → Admin
https://pro.cloudface-ai.com/guest/login      → Guest
https://pro.cloudface-ai.com/admin/pricing    → Pricing
https://pro.cloudface-ai.com/e/abc123         → Event (shareable)
```

### **Main Site (Unchanged):**
```
https://cloudface-ai.com/                     → Your current site
```

---

## ✨ **Next Steps**

1. **Buy IONOS VPS L** (~$10/mo)
2. **Add DNS record** in Cloudflare (2 min)
3. **Follow steps 3-9** above
4. **Test everything**
5. **Go live!** 🚀

---

**Status:** 📝 Ready to Deploy  
**Estimated Time:** 45-60 minutes total  
**Difficulty:** Medium  
**Cost:** ~$12/month

