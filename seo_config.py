"""
SEO Configuration for CloudFace AI
This file contains all SEO-related configurations and meta tag templates.
"""

# Base URL configuration
BASE_URL = "https://cloudface-ai.com"
SITE_NAME = "CloudFace AI"
SITE_DESCRIPTION = "AI-powered face recognition technology that helps you discover and organize photos across your digital life."

# Default meta tags
DEFAULT_META = {
    "author": "CloudFace AI",
    "robots": "index, follow",
    "language": "English",
    "revisit-after": "7 days",
    "theme-color": "#1a73e8",
    "msapplication-TileColor": "#1a73e8",
    "apple-mobile-web-app-capable": "yes",
    "apple-mobile-web-app-status-bar-style": "default",
    "apple-mobile-web-app-title": "CloudFace AI"
}

# Page-specific meta configurations
PAGE_META = {
    "home": {
        "title": "CloudFace AI - AI-Powered Face Recognition & Photo Organization App",
        "description": "Find anyone in your photos instantly with AI-powered face recognition. Organize photos across Google Drive with privacy-first technology. Upload a selfie and discover every photo of that person.",
        "keywords": "face recognition, AI photo organization, Google Drive photos, photo search, facial recognition software, photo management, AI photo finder, cloud photo organization",
        "og_type": "website",
        "twitter_card": "summary_large_image"
    },
    "about": {
        "title": "About CloudFace AI - AI Face Recognition Technology & Team",
        "description": "Learn about CloudFace AI's mission to revolutionize photo organization with AI-powered face recognition. Discover our team, technology, and commitment to privacy.",
        "keywords": "about CloudFace AI, AI face recognition company, photo organization technology, privacy-first AI, CloudFace AI team, facial recognition software company",
        "og_type": "website",
        "twitter_card": "summary_large_image"
    },
    "blog": {
        "title": "CloudFace AI Blog - AI Face Recognition Insights & Photo Organization Tips",
        "description": "Stay updated with the latest AI face recognition technology, photo organization tips, and insights from CloudFace AI. Expert articles on photo management and AI technology.",
        "keywords": "AI face recognition blog, photo organization tips, facial recognition technology, CloudFace AI blog, photo management articles, AI technology insights",
        "og_type": "website",
        "twitter_card": "summary_large_image"
    },
    "contact": {
        "title": "Contact CloudFace AI - Get Support & Contact Information",
        "description": "Contact CloudFace AI for support, questions, or feedback about our AI face recognition technology. Get in touch with our team for technical assistance and inquiries.",
        "keywords": "contact CloudFace AI, CloudFace AI support, AI face recognition support, technical assistance, customer service, contact information",
        "og_type": "website",
        "twitter_card": "summary_large_image"
    }
}

# Structured data templates
STRUCTURED_DATA = {
    "organization": {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "CloudFace AI",
        "url": BASE_URL,
        "logo": f"{BASE_URL}/assets/logo.png",
        "description": "AI-powered face recognition technology for photo organization",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Gurugram",
            "addressCountry": "IN"
        },
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+1-234-567-890",
            "contactType": "customer service",
            "email": "info@cloudface-ai.com"
        },
        "sameAs": [
            "https://twitter.com/cloudfaceai",
            "https://linkedin.com/company/cloudfaceai",
            "https://youtube.com/channel/cloudfaceai"
        ]
    },
    "software_application": {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "CloudFace AI",
        "description": "AI-powered face recognition app that helps you discover and organize photos across your Google Drive",
        "url": BASE_URL,
        "applicationCategory": "PhotographyApplication",
        "operatingSystem": "Web Browser",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
            "description": "Free trial available"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.8",
            "ratingCount": "127"
        },
        "author": {
            "@type": "Organization",
            "name": "CloudFace AI",
            "url": BASE_URL
        },
        "featureList": [
            "AI-Powered Face Recognition",
            "Google Drive Integration",
            "Photo Organization",
            "Privacy-First Technology",
            "Local Processing",
            "Smart Caching"
        ]
    }
}

# Performance optimization settings
PERFORMANCE_CONFIG = {
    "enable_gzip": True,
    "enable_browser_caching": True,
    "enable_image_optimization": True,
    "enable_minification": True,
    "enable_cdn": False,
    "cdn_url": "",
    "critical_css": True,
    "lazy_loading": True
}

# Analytics configuration
ANALYTICS_CONFIG = {
    "google_analytics": {
        "enabled": True,
        "tracking_id": "GA_MEASUREMENT_ID",  # Replace with actual GA4 ID
        "anonymize_ip": True,
        "respect_dnt": True
    },
    "google_tag_manager": {
        "enabled": False,
        "container_id": "GTM-XXXXXXX"  # Replace with actual GTM ID
    },
    "facebook_pixel": {
        "enabled": False,
        "pixel_id": "XXXXXXXXXX"  # Replace with actual Pixel ID
    }
}

# Social media configuration
SOCIAL_MEDIA = {
    "twitter": {
        "username": "@cloudfaceai",
        "card_type": "summary_large_image"
    },
    "facebook": {
        "app_id": "",  # Add Facebook App ID if needed
        "page_id": ""
    },
    "linkedin": {
        "company_id": ""
    }
}

# SEO monitoring and reporting
SEO_MONITORING = {
    "enable_sitemap_generation": True,
    "enable_robots_txt": True,
    "enable_structured_data": True,
    "enable_meta_tags": True,
    "enable_canonical_urls": True,
    "enable_social_meta_tags": True,
    "enable_analytics": True,
    "enable_performance_monitoring": True
}

def get_page_meta(page_name):
    """Get meta configuration for a specific page"""
    return PAGE_META.get(page_name, PAGE_META["home"])

def get_structured_data(data_type):
    """Get structured data for a specific type"""
    return STRUCTURED_DATA.get(data_type, {})

def generate_canonical_url(page_path=""):
    """Generate canonical URL for a page"""
    if page_path.startswith("/"):
        page_path = page_path[1:]
    return f"{BASE_URL}/{page_path}" if page_path else BASE_URL

def get_social_meta_tags(page_name):
    """Get social media meta tags for a page"""
    page_meta = get_page_meta(page_name)
    return {
        "og:type": page_meta.get("og_type", "website"),
        "og:title": page_meta.get("title"),
        "og:description": page_meta.get("description"),
        "og:url": generate_canonical_url(page_name if page_name != "home" else ""),
        "og:site_name": SITE_NAME,
        "og:locale": "en_US",
        "twitter:card": page_meta.get("twitter_card", "summary_large_image"),
        "twitter:title": page_meta.get("title"),
        "twitter:description": page_meta.get("description"),
        "twitter:url": generate_canonical_url(page_name if page_name != "home" else "")
    }
