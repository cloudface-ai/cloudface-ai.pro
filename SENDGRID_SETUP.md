# SendGrid Configuration for CloudFace Pro

## Environment Variables

Add these to your `.env` file on the server:

```bash
# Email Configuration (SendGrid)
TESTING_MODE=false
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=YOUR_SENDGRID_API_KEY_HERE
FROM_EMAIL=noreply@cloudface-ai.pro
```

## Setup Steps

### 1. SSH to Server
```bash
ssh root@69.62.85.241
cd /var/www/cloudface-pro
```

### 2. Edit .env File
```bash
nano .env
```

Add or update these lines:
```
TESTING_MODE=false
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<YOUR_SENDGRID_API_KEY>
FROM_EMAIL=noreply@cloudface-ai.pro
```

**Note**: 
- `SMTP_USER` is literally the word "apikey" (not your username)
- `SMTP_PASSWORD` is your SendGrid API key (starts with "SG.")
- `FROM_EMAIL` must match the verified sender email in SendGrid

Save and exit (Ctrl+X, then Y, then Enter)

### 3. Restart CloudFace Pro
```bash
sudo systemctl restart cloudface-pro
sudo systemctl status cloudface-pro
```

### 4. Test Email Sending

Create a test script on the server:

```bash
cat > /var/www/cloudface-pro/test_email.py << 'EOF'
from cloudface_pro_email import email_service

# Test verification email
test_email = "YOUR_EMAIL@gmail.com"  # Replace with your email
code = email_service.generate_verification_code(test_email)
success = email_service.send_verification_email(test_email, code)

if success:
    print(f"✅ Email sent successfully! Check {test_email}")
    print(f"Verification code: {code}")
else:
    print("❌ Email failed to send. Check logs above.")
EOF
```

Run the test:
```bash
source venv/bin/activate
python test_email.py
```

Check your email inbox (and spam folder).

## Troubleshooting

### Issue: Email not received
- Check SendGrid Activity Feed: https://app.sendgrid.com/email_activity
- Verify sender email is approved in SendGrid
- Check spam/junk folder
- Verify FROM_EMAIL matches verified sender

### Issue: "Authentication failed"
- Ensure SMTP_USER is exactly "apikey" (lowercase)
- Verify API key is correct (no extra spaces)
- Check API key has "Mail Send" permission

### Issue: "550 The from address does not match"
- FROM_EMAIL must match the verified sender in SendGrid
- Go to Settings → Sender Authentication
- Verify the sender email you're using

## SendGrid Dashboard Links

- **API Keys**: https://app.sendgrid.com/settings/api_keys
- **Sender Authentication**: https://app.sendgrid.com/settings/sender_auth
- **Email Activity**: https://app.sendgrid.com/email_activity
- **Statistics**: https://app.sendgrid.com/statistics

## Email Templates

CloudFace Pro uses these email templates:

1. **Verification Email**: 6-digit code for admin signup
2. **Welcome Email**: Sent after email verification

Both are in `cloudface_pro_email.py` with beautiful HTML styling.

## SendGrid Free Tier Limits

- **100 emails/day** forever free
- Upgrade for more volume if needed
- Monitor usage: https://app.sendgrid.com/statistics

## Next Steps

After setup:
1. Test admin signup flow with real email
2. Monitor SendGrid activity feed
3. Set up domain authentication for better deliverability (optional)

