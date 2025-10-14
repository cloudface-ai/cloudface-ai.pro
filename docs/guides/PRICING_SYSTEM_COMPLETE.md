# 💳 CloudFace Pro - Pricing & Limits System

## ✅ Complete Implementation

---

## 📊 **Pricing Tiers**

### **Free Trial**
- **Price:** ₹0 / $0
- **Storage:** 1 GB
- **Photos:** 1,000 photos
- **Events:** 1 event
- **Features:**
  - Basic face recognition
  - Watermark support

### **Personal - ₹4,999/year**
- **Storage:** 20 GB
- **Photos:** 100,000 photos/year
- **Events:** 10 events
- **Features:**
  - Advanced face recognition
  - Custom watermarks
  - Email support

### **Professional - ₹9,999/year** ⭐ POPULAR
- **Storage:** 50 GB
- **Photos:** 250,000 photos/year
- **Events:** 50 events
- **Features:**
  - Advanced face recognition
  - Custom watermarks
  - Analytics dashboard
  - Priority support
  - Bulk operations

### **Business - ₹16,999/year**
- **Storage:** 100 GB
- **Photos:** 600,000 photos/year
- **Events:** 200 events
- **Features:**
  - Advanced face recognition
  - Custom watermarks
  - Analytics dashboard
  - Team accounts
  - API access
  - 24/7 support

### **Enterprise - Contact Us**
- **Storage:** Unlimited
- **Photos:** Unlimited
- **Events:** Unlimited
- **Features:**
  - All Business features
  - Dedicated support
  - Custom integrations
  - SLA guarantee

---

## 🔒 **Limit Enforcement**

### **Photo Upload Limits**
When admin uploads photos, the system checks:

1. **Photo Count Limit:**
   ```python
   if (photos_used + new_photos) > max_photos:
       return "Photo limit exceeded. Upgrade to upload more."
   ```

2. **Storage Limit:**
   ```python
   if (storage_used + upload_size) > max_storage_gb:
       return "Storage limit exceeded. Upgrade for more storage."
   ```

3. **If Within Limits:**
   - Photos are saved
   - Usage counters updated
   - Face processing begins

---

## 💡 **How It Works**

### **For Admins:**

#### **On Dashboard:**
```
┌──────────────────────────────────────────────────┐
│  Current Plan                    [Upgrade Plan]  │
│  Professional                                    │
│  12,500 / 250,000 photos • 5.2 / 50 GB used     │
└──────────────────────────────────────────────────┘
```

#### **When Uploading Photos:**
```
1. Admin uploads 500 photos (2GB)
2. System checks:
   ✓ Photo count: 12,500 + 500 = 13,000 < 250,000 ✅
   ✓ Storage: 5.2 + 2 = 7.2 GB < 50 GB ✅
3. Upload proceeds
4. Usage updated: 13,000 photos, 7.2 GB
```

#### **If Limit Exceeded:**
```
❌ Photo limit exceeded!
Your Professional plan allows 250,000 photos/year.
You have 249,800 photos.

[Upgrade to Business] → More photos & storage
```

### **For Guests:**
- **FREE access** to all events they're invited to
- No limits on searching or downloading
- Admin pays for the service

---

## 🎯 **Usage Tracking**

### **Automatically Tracked:**
- `photos_used_this_year` - Total photos uploaded in current year
- `storage_used_gb` - Total storage consumed
- Resets annually (Jan 1st)

### **Displayed On:**
- Admin Dashboard (plan banner)
- Pricing Page (current usage)
- Upload Page (before uploading)

---

## 🚀 **URLs**

### **Pricing & Plans:**
```
/admin/pricing          → View all plans & upgrade
/admin/subscribe/<plan> → Subscribe to plan (payment)
```

### **API:**
```
GET /api/user/subscription → Get current plan & usage
POST /api/user/upgrade     → Upgrade plan
```

---

## 📋 **Database Schema**

### **Subscriptions Collection:**
```json
{
  "user_id": "admin@example.com",
  "plan": "professional",
  "status": "active",
  "photos_used_this_year": 12500,
  "storage_used_gb": 5.2,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-10-14T12:00:00",
  "payment_data": {
    "transaction_id": "txn_123",
    "amount": 9999,
    "currency": "INR"
  }
}
```

---

## 💰 **Payment Integration** (Coming Soon)

### **Supported Gateways:**
- **Razorpay** (India) - Recommended
- **Stripe** (International)
- **PayPal** (Alternative)

### **Flow:**
```
Admin clicks "Upgrade Plan"
      ↓
Select Plan (Professional)
      ↓
Payment Gateway (Razorpay)
      ↓
Payment Success
      ↓
Plan Activated Immediately
      ↓
Usage Limits Updated
```

---

## ✨ **Key Features**

✅ **4 Pricing Tiers** (Free, Personal, Professional, Business, Enterprise)  
✅ **Automatic Limit Enforcement** (Photos & Storage)  
✅ **Usage Tracking** (Real-time updates)  
✅ **Dashboard Integration** (Plan banner with usage)  
✅ **Upgrade UI** (One-click access to pricing)  
✅ **Guests Free** (No charges for event attendees)  
✅ **Flexible Plans** (Upgrade/downgrade anytime)  
✅ **SEO Optimized** (/admin/pricing for discoverability)

---

## 🧪 **Testing (TESTING_MODE)**

In testing mode:
- Plans stored in local JSON
- No actual payment required
- Can test all plan upgrades
- Usage tracked locally

**Test Commands:**
```python
# Check current plan
subscription = pricing_manager.get_user_subscription('admin@example.com')
print(subscription['plan'])  # 'free'

# Upgrade plan
pricing_manager.update_subscription('admin@example.com', 'professional')

# Check limits
can_upload = pricing_manager.check_can_upload('admin@example.com', 1000, 1073741824)
print(can_upload['allowed'])  # True/False
```

---

## 📊 **Admin Experience**

### **Dashboard View:**
1. **Plan Banner** at top showing:
   - Current plan name
   - Usage (photos & storage)
   - Upgrade/Change Plan button

2. **Stats showing:**
   - Total events, photos, searches, storage

3. **Upload blocked if:**
   - Photo limit reached → Show upgrade message
   - Storage limit reached → Show upgrade message

### **Pricing Page:**
- View all plans
- See current plan highlighted
- See usage stats
- Click to upgrade
- Contact us for Enterprise

---

## 🎁 **Benefits**

### **For Business:**
- 💰 Recurring revenue model
- 📈 Upsell opportunities
- 🎯 Clear value proposition
- 🔒 Enforced limits = upgrades

### **For Users:**
- 🆓 Free tier to start
- 📊 Clear usage visibility
- ⬆️ Easy upgrades
- 💪 Flexible plans

### **For Guests:**
- 🎉 100% FREE
- 🚫 No hidden charges
- ✅ Admin pays for everything

---

**Status:** ✅ Fully Implemented  
**Payment Integration:** 🔜 Coming Soon (Razorpay)  
**Last Updated:** October 14, 2025

