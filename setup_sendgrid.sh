#!/bin/bash
# SendGrid Setup Script for CloudFace Pro

echo "📧 SendGrid Configuration for CloudFace Pro"
echo "==========================================="
echo ""
echo "Please provide the following information:"
echo ""

# Get SendGrid API Key
read -p "Enter your SendGrid API Key (starts with SG.): " SENDGRID_API_KEY

# Get FROM_EMAIL
read -p "Enter verified sender email (default: noreply@cloudface-ai.pro): " FROM_EMAIL
FROM_EMAIL=${FROM_EMAIL:-noreply@cloudface-ai.pro}

echo ""
echo "Creating .env configuration..."
echo ""

# SSH to server and configure
ssh root@69.62.85.241 << ENDSSH
cd /var/www/cloudface-pro

# Backup existing .env
cp .env .env.backup.\$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# Update .env with SendGrid settings
echo "# Email Configuration (SendGrid)" >> .env
echo "TESTING_MODE=false" >> .env
echo "SMTP_SERVER=smtp.sendgrid.net" >> .env
echo "SMTP_PORT=587" >> .env
echo "SMTP_USER=apikey" >> .env
echo "SMTP_PASSWORD=${SENDGRID_API_KEY}" >> .env
echo "FROM_EMAIL=${FROM_EMAIL}" >> .env

# Set correct permissions
chmod 640 .env
chown www-data:www-data .env

echo "✅ .env updated with SendGrid configuration"

# Restart CloudFace Pro
echo "🔄 Restarting CloudFace Pro service..."
systemctl restart cloudface-pro
sleep 2

# Check status
systemctl status cloudface-pro --no-pager

echo ""
echo "✅ SendGrid setup complete!"
echo ""
echo "To test email sending, run:"
echo "  ssh root@69.62.85.241"
echo "  cd /var/www/cloudface-pro"
echo "  source venv/bin/activate"
echo "  python -c 'from cloudface_pro_email import email_service; print(email_service)'"
ENDSSH

echo ""
echo "🎉 Configuration deployed to server!"
echo ""
echo "Next steps:"
echo "1. Go to https://cloudface-ai.pro/admin/signup"
echo "2. Sign up with a new email"
echo "3. Check your email for the verification code"
echo ""

