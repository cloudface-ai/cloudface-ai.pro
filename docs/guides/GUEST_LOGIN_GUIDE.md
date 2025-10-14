# 🎫 Guest Login Guide - CloudFace Pro

## How Guests Access Events and Find Their Photos

---

## 📱 **Step-by-Step Guide**

### **Step 1: Get Event Link from Admin**
The admin (photographer/event organizer) shares the event link with guests:
```
Example: http://localhost:5002/e/abc123
         http://yoursite.com/e/abc123
```

---

### **Step 2: Visit Event Page**
When guests click the link, they see the **public event page** with:

```
┌─────────────────────────────────────┐
│     [Event Logo]                    │
│                                     │
│     Wedding 2025                    │
│     October 15, 2025                │
├─────────────────────────────────────┤
│                                     │
│           🔐                        │
│   Sign Up to Find Your Photos       │
│                                     │
│   Create an account to search       │
│   and save your photos              │
│                                     │
│   [  Create Account  ]              │
│                                     │
│   Already have an account? Log in   │
│                                     │
├─────────────────────────────────────┤
│   Why Sign Up?                      │
│                                     │
│   💾 Your photos auto-save          │
│   🚫 No re-upload needed            │
│   🔒 Protects everyone's privacy    │
└─────────────────────────────────────┘
```

---

### **Step 3: Guest Signup** (First Time Users)

**URL**: `/guest/signup/<event_id>`

Click **"Create Account"** to see the signup form:

```
┌─────────────────────────────────────┐
│   Create Your Account               │
│                                     │
│   Name: [John Doe        ]          │
│   Email: [john@example.com]         │
│   Phone: [+1234567890    ]          │
│   Password: [********    ]          │
│                                     │
│   [  Sign Up  ]                     │
│                                     │
│   Already registered? Log in        │
└─────────────────────────────────────┘
```

**Form Fields:**
- Name (required)
- Email (required, must be unique)
- Phone (optional)
- Password (required)

**What happens after signup:**
1. Account created → `session['guest_id']` set
2. Redirected to → `/guest/capture-selfie/<event_id>`

---

### **Step 4: Capture Selfie** (During Signup)

**URL**: `/guest/capture-selfie/<event_id>`

After signup, guests capture their selfie:

```
┌─────────────────────────────────────┐
│   Capture Your Selfie               │
│                                     │
│   Selfie Quality Guide:             │
│   ✓ Look directly at camera         │
│   ✓ Good lighting                   │
│   ✓ Clear face visible              │
│   ✓ Remove sunglasses               │
│                                     │
│   ┌─────────────────────┐           │
│   │  [Live Camera Feed] │           │
│   │                     │           │
│   └─────────────────────┘           │
│                                     │
│   [📸 Capture]  [📁 Upload]         │
│                                     │
│   [Preview will appear here]        │
│                                     │
│   [↩️ Retake]  [✅ Confirm]          │
└─────────────────────────────────────┘
```

**Two Options:**
1. **Capture from Camera** - Use device camera (webcam/phone)
2. **Upload from Gallery** - Select existing photo

**What happens after capture:**
1. Selfie stored securely → Linked to guest account
2. Redirected to → `/e/<event_id>` (event page)
3. **Auto-search enabled** for future logins!

---

### **Step 5: Guest Login** (Returning Users)

**URL**: `/guest/login/<event_id>`

If guest already has an account, click **"Log in"**:

```
┌─────────────────────────────────────┐
│   Welcome Back!                     │
│                                     │
│   Email: [john@example.com]         │
│   Password: [********    ]          │
│                                     │
│   [  Log In  ]                      │
│                                     │
│   Don't have an account? Sign up    │
└─────────────────────────────────────┘
```

**What happens after login:**
1. Credentials verified
2. `session['guest_id']` set
3. Redirected to → `/e/<event_id>`
4. **Auto-search button appears** (uses stored selfie!)

---

### **Step 6: Find Photos** (After Login)

Once logged in, guests see:

```
┌─────────────────────────────────────┐
│           👋                        │
│   Welcome, John Doe!                │
│   Ready to find your photos?        │
│                                     │
│   [  🔍 Find My Photos  ]           │
│                                     │
│   Using your saved selfie • Logout  │
└─────────────────────────────────────┘
```

**Click "🔍 Find My Photos"** to:
1. Auto-load stored selfie (no re-upload!)
2. Start real-time face search
3. See results instantly as they're found

---

## 🔐 **Technical Details**

### **Guest Signup API**
```http
POST /guest/signup/<event_id>
Content-Type: application/x-www-form-urlencoded

name=John+Doe
email=john@example.com
phone=+1234567890
password=secretpass123
```

**Response:**
```json
{
  "success": true,
  "redirect": "/guest/capture-selfie/abc123"
}
```

---

### **Guest Login API**
```http
POST /guest/login/<event_id>
Content-Type: application/x-www-form-urlencoded

email=john@example.com
password=secretpass123
```

**Response:**
```json
{
  "success": true,
  "redirect": "/e/abc123"
}
```

---

### **Selfie Capture API**
```http
POST /guest/capture-selfie/<event_id>
Content-Type: multipart/form-data

selfie: [image file]
```

**Response:**
```json
{
  "success": true,
  "redirect": "/e/abc123"
}
```

---

### **Session Data Stored**
After successful login:
```python
session['guest_id'] = 'g_abc123xyz'
session['guest_email'] = 'john@example.com'
session['guest_name'] = 'John Doe'
session['last_event_id'] = 'abc123'
```

---

## 🎯 **Complete User Journey**

### **First-Time Guest**
```
1. Click event link → /e/abc123
2. See signup/login page
3. Click "Create Account"
4. Fill signup form → Submit
5. Capture/upload selfie → Confirm
6. Redirected to event page (logged in)
7. Click "🔍 Find My Photos"
8. See search results in real-time
9. Download photos with watermark
```

### **Returning Guest**
```
1. Click event link → /e/abc123
2. See signup/login page
3. Click "Log in"
4. Enter email + password → Submit
5. Redirected to event page (logged in)
6. Click "🔍 Find My Photos" (uses stored selfie!)
7. See search results instantly
8. Download photos
```

---

## 🔗 **Quick Access URLs**

| Action | URL |
|--------|-----|
| View Event | `/e/<event_id>` |
| Guest Signup | `/guest/signup/<event_id>` |
| Guest Login | `/guest/login/<event_id>` |
| Capture Selfie | `/guest/capture-selfie/<event_id>` |
| Guest Logout | `/guest/logout` |

---

## 🚀 **How to Test**

### **1. Start the server**
```bash
cd /Volumes/MAC-Studio/cloudface_ai
python cloudface_pro_server.py
```

### **2. Create an event as admin**
- Login as admin: http://localhost:5002/login
- Create event: http://localhost:5002/events/create
- Upload photos
- Copy event ID (e.g., `abc123`)

### **3. Test guest flow**
- Open incognito/private window
- Visit: http://localhost:5002/e/abc123
- Click "Create Account"
- Fill form and submit
- Capture selfie
- Search for photos!

---

## 💡 **Key Benefits for Guests**

1. **No Re-Upload** - Selfie stored once, reused forever
2. **Auto-Save** - Found photos saved in browser (localStorage)
3. **Privacy** - Selfie only used for their searches
4. **Easy Access** - Just email + password to login
5. **Instant Search** - One click to find all their photos

---

## 🔒 **Security Features**

✅ Password hashing (secure storage)  
✅ Session-based authentication  
✅ Selfie privacy (only accessible to guest)  
✅ Event-specific access tracking  
✅ No cross-guest data access  

---

**Last Updated**: October 14, 2025  
**Status**: ✅ Fully Functional

