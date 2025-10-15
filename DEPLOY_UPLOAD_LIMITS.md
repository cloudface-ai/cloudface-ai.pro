# Deploy Upload Batch Limits Update

## Summary of Changes

### 1. Upload Batch Limits Added
- **Free**: 50 photos at once
- **Personal**: 100 photos at once
- **Professional**: 200 photos at once
- **Business**: 300 photos at once
- **Business Plus**: 500 photos at once
- **Enterprise**: 1000 photos at once

### 2. Plan Assignment
- `sp.vinod@jacpl.com` needs to be assigned to **Personal plan**

---

## Deployment Steps

### Step 1: SSH to Server
```bash
ssh root@69.62.85.241
```

### Step 2: Pull Latest Code
```bash
cd /var/www/cloudface-pro
git pull origin main
```

### Step 3: Assign Personal Plan to sp.vinod@jacpl.com
```bash
cd /var/www/cloudface-pro
source venv/bin/activate
python assign_personal_plan.py
```

Expected output:
```
✅ Updated subscription for sp.vinod@jacpl.com: personal
✅ Assignment complete!
User: sp.vinod@jacpl.com
Plan: personal
Plan Name: Personal
Storage: 10 GB
Photos: 20,000
Upload Batch: 100 photos at once
Status: active
```

### Step 4: Restart CloudFace Pro Service
```bash
sudo systemctl restart cloudface-pro
```

### Step 5: Verify Service is Running
```bash
sudo systemctl status cloudface-pro
```

Should show `Active: active (running)`

### Step 6: Test Upload Limits
1. Login as Free user (spvinodmandan@gmail.com) - can upload max 50 photos
2. Login as Personal user (sp.vinod@jacpl.com) - can upload max 100 photos

---

## How It Works

### Backend Enforcement
The `check_can_upload()` method in `cloudface_pro_pricing.py` now checks:
1. **Batch size**: `photo_count > max_upload_batch`
2. **Total photos limit**: `photos_used + photo_count > max_photos`
3. **Storage limit**: `storage_used_gb + size_gb > max_storage_gb`

If batch size exceeds the limit, users see:
```
"Upload batch limit exceeded. Your plan allows uploading 50 photos at once. 
You selected 150 photos. Please upgrade or upload in smaller batches."
```

### Plan Features Display
The pricing page now shows:
- Free: "Upload 50 photos at once"
- Personal: "Upload 100 photos at once"
- Professional: "Upload 200 photos at once"
- Business: "Upload 300 photos at once"
- Business Plus: "Upload 500 photos at once"
- Enterprise: "Upload 1000+ photos at once"

---

## Testing

### Test 1: Free Plan (50 limit)
1. Login as spvinodmandan@gmail.com
2. Try to upload 60 photos
3. Should see error: "Upload batch limit exceeded..."
4. Upload 40 photos - should work

### Test 2: Personal Plan (100 limit)
1. Login as sp.vinod@jacpl.com
2. Try to upload 150 photos
3. Should see error: "Upload batch limit exceeded..."
4. Upload 90 photos - should work

---

## Notes
- Upload limits are enforced **per upload**, not per day/month
- Users can upload multiple batches (e.g., Personal can upload 100 photos, then 100 more)
- Total photo limit (20,000 for Personal) still applies across all uploads
- Storage limit (10 GB for Personal) still applies

---

## Rollback (if needed)
If there are issues, rollback to previous commit:
```bash
cd /var/www/cloudface-pro
git log --oneline -5  # Find previous commit hash
git reset --hard <previous-commit-hash>
sudo systemctl restart cloudface-pro
```

