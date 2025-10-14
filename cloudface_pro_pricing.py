"""
CloudFace Pro - Pricing & Plan Management
Handles subscription plans, limits, and enforcement
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict

# Testing mode - use local JSON instead of payment gateway
TESTING_MODE = os.environ.get('TESTING_MODE', 'true').lower() == 'true'


# ===========================
# PRICING TIERS
# ===========================

PLANS = {
    'free': {
        'name': 'Free Trial',
        'price_inr': 0,
        'price_usd': 0,
        'storage_gb': 1,
        'max_photos': 1000,
        'max_events': 1,
        'features': [
            '1 GB storage',
            '1,000 photos',
            '1 event',
            'Basic face recognition',
            'Watermark support'
        ]
    },
    'personal': {
        'name': 'Personal',
        'price_inr': 4999,
        'price_usd': 60,
        'storage_gb': 20,
        'max_photos': 100000,
        'max_events': 10,
        'features': [
            '20 GB storage',
            '100,000 photos',
            '10 events',
            'Advanced face recognition',
            'Custom watermarks',
            'Email support'
        ]
    },
    'professional': {
        'name': 'Professional',
        'price_inr': 9999,
        'price_usd': 120,
        'storage_gb': 50,
        'max_photos': 250000,
        'max_events': 50,
        'features': [
            '50 GB storage',
            '250,000 photos',
            '50 events',
            'Advanced face recognition',
            'Custom watermarks',
            'Analytics dashboard',
            'Priority support',
            'Bulk operations'
        ]
    },
    'business': {
        'name': 'Business',
        'price_inr': 16999,
        'price_usd': 200,
        'storage_gb': 100,
        'max_photos': 600000,
        'max_events': 200,
        'features': [
            '100 GB storage',
            '600,000 photos',
            '200 events',
            'Advanced face recognition',
            'Custom watermarks',
            'Analytics dashboard',
            'Team accounts',
            'API access',
            '24/7 support'
        ]
    },
    'enterprise': {
        'name': 'Enterprise',
        'price_inr': None,  # Contact us
        'price_usd': None,
        'storage_gb': -1,  # Unlimited
        'max_photos': -1,  # Unlimited
        'max_events': -1,  # Unlimited
        'features': [
            'Unlimited storage',
            'Unlimited photos',
            'Unlimited events',
            'Advanced face recognition',
            'Custom watermarks',
            'Advanced analytics',
            'Team accounts',
            'API access',
            'Dedicated support',
            'Custom integrations',
            'SLA guarantee'
        ]
    }
}


class PricingManager:
    """Manage user subscriptions and plan limits"""
    
    def __init__(self):
        if TESTING_MODE:
            self.db = None
            self.local_db_path = 'storage/cloudface_pro/subscriptions_db.json'
            os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)
            print("🧪 Testing Mode: Using local subscription DB")
        else:
            from firebase_store import initialize_firebase
            self.db = initialize_firebase()
            print("🔥 Production Mode: Using Firebase for subscriptions")
        
        self.collection = 'cloudface_pro_subscriptions'
    
    def _load_local_db(self) -> Dict:
        """Load local JSON database"""
        if os.path.exists(self.local_db_path):
            with open(self.local_db_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_local_db(self, data: Dict):
        """Save local JSON database"""
        with open(self.local_db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_subscription(self, user_id: str) -> Dict:
        """
        Get user's current subscription
        Returns plan details with limits
        """
        if TESTING_MODE:
            db = self._load_local_db()
            subscription = db.get(user_id, {
                'user_id': user_id,
                'plan': 'free',
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'photos_used_this_year': 0,
                'storage_used_gb': 0
            })
        else:
            doc = self.db.collection(self.collection).document(user_id).get()
            if doc.exists:
                subscription = doc.to_dict()
            else:
                subscription = {
                    'user_id': user_id,
                    'plan': 'free',
                    'status': 'active',
                    'created_at': datetime.now().isoformat(),
                    'photos_used_this_year': 0,
                    'storage_used_gb': 0
                }
        
        # Add plan details
        plan = subscription.get('plan', 'free')
        subscription['plan_details'] = PLANS.get(plan, PLANS['free'])
        
        return subscription
    
    def update_subscription(self, user_id: str, plan: str, payment_data: Dict = None):
        """
        Update user's subscription plan
        """
        subscription = {
            'user_id': user_id,
            'plan': plan,
            'status': 'active',
            'updated_at': datetime.now().isoformat(),
            'payment_data': payment_data or {}
        }
        
        if TESTING_MODE:
            db = self._load_local_db()
            if user_id in db:
                db[user_id].update(subscription)
            else:
                db[user_id] = subscription
                db[user_id]['created_at'] = datetime.now().isoformat()
                db[user_id]['photos_used_this_year'] = 0
                db[user_id]['storage_used_gb'] = 0
            self._save_local_db(db)
        else:
            self.db.collection(self.collection).document(user_id).set(
                subscription, merge=True
            )
        
        print(f"✅ Updated subscription for {user_id}: {plan}")
        return subscription
    
    def check_can_upload(self, user_id: str, photo_count: int, size_bytes: int) -> Dict:
        """
        Check if user can upload photos based on their plan limits
        Returns: {
            'allowed': bool,
            'reason': str,
            'current_usage': dict,
            'limits': dict
        }
        """
        subscription = self.get_user_subscription(user_id)
        plan_details = subscription['plan_details']
        
        # Get current usage
        photos_used = subscription.get('photos_used_this_year', 0)
        storage_used_gb = subscription.get('storage_used_gb', 0)
        size_gb = size_bytes / (1024 * 1024 * 1024)
        
        # Check limits
        max_photos = plan_details['max_photos']
        max_storage_gb = plan_details['storage_gb']
        
        # Unlimited plan (-1)
        if max_photos == -1 and max_storage_gb == -1:
            return {
                'allowed': True,
                'reason': 'Unlimited plan',
                'current_usage': {
                    'photos': photos_used,
                    'storage_gb': storage_used_gb
                },
                'limits': {
                    'photos': 'unlimited',
                    'storage_gb': 'unlimited'
                }
            }
        
        # Check photo limit
        if max_photos != -1 and (photos_used + photo_count) > max_photos:
            return {
                'allowed': False,
                'reason': f'Photo limit exceeded. Your plan allows {max_photos:,} photos/year. You have {photos_used:,} photos. Upgrade to upload more.',
                'current_usage': {
                    'photos': photos_used,
                    'storage_gb': storage_used_gb
                },
                'limits': {
                    'photos': max_photos,
                    'storage_gb': max_storage_gb
                }
            }
        
        # Check storage limit
        if max_storage_gb != -1 and (storage_used_gb + size_gb) > max_storage_gb:
            return {
                'allowed': False,
                'reason': f'Storage limit exceeded. Your plan allows {max_storage_gb} GB. You have used {storage_used_gb:.2f} GB. Upgrade for more storage.',
                'current_usage': {
                    'photos': photos_used,
                    'storage_gb': storage_used_gb
                },
                'limits': {
                    'photos': max_photos,
                    'storage_gb': max_storage_gb
                }
            }
        
        # All checks passed
        return {
            'allowed': True,
            'reason': 'Within limits',
            'current_usage': {
                'photos': photos_used,
                'storage_gb': storage_used_gb
            },
            'limits': {
                'photos': max_photos,
                'storage_gb': max_storage_gb
            }
        }
    
    def increment_usage(self, user_id: str, photo_count: int, size_bytes: int):
        """
        Increment user's photo and storage usage
        """
        size_gb = size_bytes / (1024 * 1024 * 1024)
        
        if TESTING_MODE:
            db = self._load_local_db()
            if user_id not in db:
                db[user_id] = {
                    'user_id': user_id,
                    'plan': 'free',
                    'status': 'active',
                    'created_at': datetime.now().isoformat(),
                    'photos_used_this_year': 0,
                    'storage_used_gb': 0
                }
            
            db[user_id]['photos_used_this_year'] = db[user_id].get('photos_used_this_year', 0) + photo_count
            db[user_id]['storage_used_gb'] = db[user_id].get('storage_used_gb', 0) + size_gb
            self._save_local_db(db)
        else:
            # Firebase increment
            from google.cloud.firestore import Increment
            self.db.collection(self.collection).document(user_id).set({
                'photos_used_this_year': Increment(photo_count),
                'storage_used_gb': Increment(size_gb)
            }, merge=True)
        
        print(f"📊 Updated usage for {user_id}: +{photo_count} photos, +{size_gb:.2f} GB")
    
    def get_plan_details(self, plan_name: str) -> Dict:
        """Get details for a specific plan"""
        return PLANS.get(plan_name, PLANS['free'])
    
    def get_all_plans(self) -> Dict:
        """Get all available plans"""
        return PLANS


# Global instance
pricing_manager = PricingManager()


if __name__ == "__main__":
    print("🧪 Testing Pricing Manager...")
    
    # Test get subscription
    test_user = "test@example.com"
    subscription = pricing_manager.get_user_subscription(test_user)
    print(f"Subscription: {subscription}")
    
    # Test limits check
    check = pricing_manager.check_can_upload(test_user, 500, 1024 * 1024 * 1024)  # 500 photos, 1GB
    print(f"Can upload: {check}")
    
    print("✅ Pricing Manager test complete!")

