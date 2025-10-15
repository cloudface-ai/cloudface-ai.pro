"""
CloudFace Pro - Email Service
Handles email verification, notifications, and communications
"""

import smtplib
import secrets
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict
import cloudface_pro_config as config

# Email testing mode - separate from auth testing
# Use EMAIL_TESTING_MODE to control email behavior independently
EMAIL_TESTING_MODE = os.environ.get('EMAIL_TESTING_MODE', os.environ.get('TESTING_MODE', 'true')).lower() == 'true'


class EmailService:
    """Manage email sending and verification"""
    
    def __init__(self):
        self.verification_db_path = 'storage/cloudface_pro/email_verifications.json'
        os.makedirs(os.path.dirname(self.verification_db_path), exist_ok=True)
        
        # Email config (for production)
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_user = os.environ.get('SMTP_USER', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', config.CONTACT_EMAIL)
        
        if EMAIL_TESTING_MODE:
            print("🧪 Email Service: Testing Mode (emails printed, not sent)")
        else:
            print(f"📧 Email Service: Production Mode ({self.smtp_server})")
    
    def _load_verification_db(self) -> Dict:
        """Load verification codes database"""
        if os.path.exists(self.verification_db_path):
            with open(self.verification_db_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_verification_db(self, data: Dict):
        """Save verification codes database"""
        with open(self.verification_db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_verification_code(self, email: str) -> str:
        """
        Generate 6-digit verification code
        Stores code with expiry (15 minutes)
        """
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Store code with expiry
        db = self._load_verification_db()
        db[email] = {
            'code': code,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=15)).isoformat(),
            'verified': False
        }
        self._save_verification_db(db)
        
        print(f"✅ Generated verification code for {email}: {code}")
        return code
    
    def verify_code(self, email: str, code: str) -> bool:
        """
        Verify the code matches and hasn't expired
        """
        db = self._load_verification_db()
        
        if email not in db:
            return False
        
        verification = db[email]
        
        # Check expiry
        expires_at = datetime.fromisoformat(verification['expires_at'])
        if datetime.now() > expires_at:
            print(f"❌ Verification code expired for {email}")
            return False
        
        # Check code
        if verification['code'] != code:
            print(f"❌ Invalid verification code for {email}")
            return False
        
        # Mark as verified
        db[email]['verified'] = True
        db[email]['verified_at'] = datetime.now().isoformat()
        self._save_verification_db(db)
        
        print(f"✅ Email verified: {email}")
        return True
    
    def send_verification_email(self, email: str, code: str) -> bool:
        """
        Send verification code email
        """
        subject = f"Your CloudFace Pro Verification Code: {code}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; margin: 0; padding: 40px 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                .content {{ padding: 40px 30px; }}
                .code {{ font-size: 48px; font-weight: 700; color: #2D2D2D; text-align: center; letter-spacing: 8px; margin: 30px 0; padding: 20px; background: #F3F4F6; border-radius: 8px; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #6B7280; border-top: 1px solid #E5E7EB; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;">Welcome to CloudFace Pro!</h1>
                    <p style="margin: 10px 0 0; opacity: 0.9;">Verify your email to get started</p>
                </div>
                
                <div class="content">
                    <p style="font-size: 16px; color: #2D2D2D; margin-bottom: 20px;">
                        Hi there! 👋
                    </p>
                    <p style="font-size: 15px; color: #4B5563; line-height: 1.6; margin-bottom: 30px;">
                        Thank you for signing up for CloudFace Pro. To complete your registration, please enter the verification code below:
                    </p>
                    
                    <div class="code">{code}</div>
                    
                    <p style="font-size: 13px; color: #6B7280; text-align: center; margin-top: 20px;">
                        This code expires in 15 minutes
                    </p>
                    
                    <p style="font-size: 14px; color: #4B5563; line-height: 1.6; margin-top: 40px;">
                        If you didn't create an account, you can safely ignore this email.
                    </p>
                </div>
                
                <div class="footer">
                    <p>© 2025 CloudFace Pro - AI-Powered Event Photography</p>
                    <p style="margin-top: 8px;">
                        <a href="https://cloudface.pro" style="color: #667eea; text-decoration: none;">cloudface.pro</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        if EMAIL_TESTING_MODE:
            # Testing mode - just print the email
            print("\n" + "="*70)
            print("📧 EMAIL (Testing Mode - Not Actually Sent)")
            print("="*70)
            print(f"To: {email}")
            print(f"Subject: {subject}")
            print(f"Code: {code}")
            print("="*70 + "\n")
            return True
        else:
            # Production - actually send email
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.from_email
                msg['To'] = email
                
                # Attach HTML
                msg.attach(MIMEText(html_body, 'html'))
                
                # Send via SMTP
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                
                print(f"✅ Verification email sent to {email}")
                return True
                
            except Exception as e:
                print(f"❌ Failed to send email to {email}: {e}")
                return False
    
    def send_welcome_email(self, email: str, name: str = None):
        """Send welcome email after successful verification"""
        subject = "Welcome to CloudFace Pro! 🎉"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; margin: 0; padding: 40px 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                .content {{ padding: 40px 30px; }}
                .btn {{ display: inline-block; background: #667eea; color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; margin-top: 20px; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #6B7280; border-top: 1px solid #E5E7EB; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 32px;">🎉 Welcome to CloudFace Pro!</h1>
                </div>
                
                <div class="content">
                    <p style="font-size: 16px; color: #2D2D2D; margin-bottom: 20px;">
                        Hi{' ' + name if name else ''}! 👋
                    </p>
                    <p style="font-size: 15px; color: #4B5563; line-height: 1.6; margin-bottom: 20px;">
                        Your account is now verified and ready to use! You can now:
                    </p>
                    
                    <ul style="font-size: 15px; color: #4B5563; line-height: 1.8; margin: 20px 0;">
                        <li>Create events</li>
                        <li>Upload photos with AI face recognition</li>
                        <li>Share with guests instantly</li>
                        <li>Track analytics and engagement</li>
                    </ul>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="https://cloudface.pro/admin/dashboard" class="btn">
                            Go to Dashboard →
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>© 2025 CloudFace Pro - AI-Powered Event Photography</p>
                    <p style="margin-top: 8px;">Need help? Contact us at {config.CONTACT_EMAIL}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        if EMAIL_TESTING_MODE:
            print(f"📧 Welcome email would be sent to {email}")
            return True
        else:
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.from_email
                msg['To'] = email
                msg.attach(MIMEText(html_body, 'html'))
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                
                print(f"✅ Welcome email sent to {email}")
                return True
            except Exception as e:
                print(f"❌ Failed to send welcome email: {e}")
                return False


# Global instance
email_service = EmailService()


if __name__ == "__main__":
    print("🧪 Testing Email Service...")
    
    # Test generate code
    code = email_service.generate_verification_code("test@example.com")
    print(f"Code: {code}")
    
    # Test send email
    email_service.send_verification_email("test@example.com", code)
    
    # Test verify
    is_valid = email_service.verify_code("test@example.com", code)
    print(f"Verification: {is_valid}")
    
    print("✅ Email Service test complete!")

