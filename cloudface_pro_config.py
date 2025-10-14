"""
CloudFace Pro - Configuration File
Single source of truth for all app settings
Change values here once, updates everywhere automatically
"""

# ===========================
# COMPANY INFORMATION
# ===========================
COMPANY_NAME = "CloudFace Pro"
COMPANY_TAGLINE = "AI-Powered Event Photography Platform"
COMPANY_DESCRIPTION = "Professional face recognition for events. Find your photos instantly."

# ===========================
# CONTACT INFORMATION
# ===========================
CONTACT_EMAIL = "support@cloudface.pro"
CONTACT_PHONE = "+91 98765 43210"
CONTACT_PHONE_DISPLAY = "+91 98765 43210"
SUPPORT_HOURS = "9 AM - 6 PM IST, Monday - Saturday"

# ===========================
# SOCIAL MEDIA
# ===========================
SOCIAL_LINKS = {
    'facebook': 'https://facebook.com/cloudfacepro',
    'instagram': 'https://instagram.com/cloudfacepro',
    'twitter': 'https://twitter.com/cloudfacepro',
    'linkedin': 'https://linkedin.com/company/cloudfacepro'
}

# ===========================
# STORAGE CONFIGURATION
# ===========================
STORAGE_TYPE = "VPS"  # Options: "VPS", "CLOUDFLARE_R2", "AWS_S3", "BACKBLAZE_B2"

# VPS Storage Settings
VPS_STORAGE_PATH = "storage/cloudface_pro"
VPS_MAX_SIZE_GB = 50  # Switch to cloud storage after this

# Cloud Storage Settings (for future migration)
CLOUDFLARE_R2_CONFIG = {
    'account_id': '',
    'access_key': '',
    'secret_key': '',
    'bucket_name': 'cloudface-pro-events'
}

AWS_S3_CONFIG = {
    'access_key': '',
    'secret_key': '',
    'bucket_name': 'cloudface-pro-events',
    'region': 'us-east-1'
}

# ===========================
# FILE UPLOAD LIMITS
# ===========================
MAX_PHOTOS_PER_EVENT = 1000
MAX_FILE_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'heic']
THUMBNAIL_SIZE = (400, 400)  # Width x Height

# ===========================
# FACE RECOGNITION SETTINGS
# ===========================
FACE_DETECTION_MODEL = "RetinaFace"
FACE_EMBEDDING_MODEL = "ArcFace"
SIMILARITY_THRESHOLD = 0.6  # 0.0 to 1.0
MIN_FACE_SIZE = 50  # Minimum face size in pixels

# ===========================
# EVENT SETTINGS
# ===========================
DEFAULT_EVENT_EXPIRY_DAYS = 30  # Auto-delete old events after X days
MAX_EVENTS_PER_USER = 100
EVENT_URL_PREFIX = "e"  # https://cloudface.pro/e/ABC123

# ===========================
# PRICING & PLANS
# ===========================
PRICING_PLANS = {
    'free': {
        'name': 'Free Trial',
        'max_events': 3,
        'max_photos_per_event': 100,
        'storage_gb': 1,
        'price_monthly': 0
    },
    'starter': {
        'name': 'Starter',
        'max_events': 10,
        'max_photos_per_event': 500,
        'storage_gb': 10,
        'price_monthly': 999  # INR
    },
    'professional': {
        'name': 'Professional',
        'max_events': 50,
        'max_photos_per_event': 1000,
        'storage_gb': 50,
        'price_monthly': 2999  # INR
    },
    'enterprise': {
        'name': 'Enterprise',
        'max_events': -1,  # Unlimited
        'max_photos_per_event': -1,  # Unlimited
        'storage_gb': -1,  # Unlimited
        'price_monthly': 9999  # INR
    }
}

# ===========================
# UI/UX SETTINGS
# ===========================
THEME_COLORS = {
    'primary': '#4285F4',  # Google Blue
    'primary_dark': '#1a73e8',
    'secondary': '#FF9800',  # Firebase Orange
    'success': '#10B981',
    'danger': '#EF4444',
    'text_dark': '#1F2937',
    'text_light': '#6B7280',
    'background': '#F8F9FA',
    'card_bg': '#FFFFFF'
}

# ===========================
# SECURITY SETTINGS
# ===========================
SECRET_KEY = "your-secret-key-here-change-in-production"  # Flask secret key
SESSION_LIFETIME_HOURS = 24
ALLOWED_DOMAINS = []  # Empty = allow all domains
RATE_LIMIT_SEARCHES_PER_HOUR = 100

# ===========================
# ANALYTICS & TRACKING
# ===========================
ENABLE_ANALYTICS = True
TRACK_USER_BEHAVIOR = True
GOOGLE_ANALYTICS_ID = ""  # Add your GA4 ID

# ===========================
# EMAIL SETTINGS (for notifications)
# ===========================
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASSWORD = ""
EMAIL_FROM = "noreply@cloudface.pro"

# ===========================
# FEATURE FLAGS
# ===========================
FEATURES = {
    'enable_whatsapp_share': True,
    'enable_email_share': True,
    'enable_qr_codes': True,
    'enable_bulk_download': True,
    'enable_event_password': True,
    'enable_custom_branding': True,
    'enable_watermarks': False,  # Coming soon
    'enable_video_search': False  # Coming soon
}

# ===========================
# LEGAL & COMPLIANCE
# ===========================
PRIVACY_POLICY_URL = "/privacy"
TERMS_OF_SERVICE_URL = "/terms"
DATA_RETENTION_DAYS = 90  # Keep deleted events for X days
GDPR_COMPLIANT = True
CCPA_COMPLIANT = True

# ===========================
# ADMIN SETTINGS
# ===========================
ADMIN_EMAILS = ["admin@cloudface.pro"]  # List of admin emails
ENABLE_ADMIN_NOTIFICATIONS = True
ADMIN_DASHBOARD_PATH = "/admin/dashboard"

# ===========================
# HELPER FUNCTIONS
# ===========================

def get_storage_path(event_id: str, file_type: str = "photos") -> str:
    """Generate storage path for event files"""
    return f"{VPS_STORAGE_PATH}/events/{event_id}/{file_type}"

def get_thumbnail_path(event_id: str) -> str:
    """Generate thumbnail storage path"""
    return f"{VPS_STORAGE_PATH}/events/{event_id}/thumbnails"

def get_event_url(event_id: str) -> str:
    """Generate public event URL"""
    return f"/{EVENT_URL_PREFIX}/{event_id}"

def is_storage_limit_reached() -> bool:
    """Check if VPS storage limit is reached"""
    import os
    total_size = 0
    if os.path.exists(VPS_STORAGE_PATH):
        for dirpath, dirnames, filenames in os.walk(VPS_STORAGE_PATH):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
    
    size_gb = total_size / (1024 ** 3)
    return size_gb >= VPS_MAX_SIZE_GB

def get_plan_limits(plan_name: str) -> dict:
    """Get limits for a specific pricing plan"""
    return PRICING_PLANS.get(plan_name, PRICING_PLANS['free'])

