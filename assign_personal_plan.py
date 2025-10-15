"""
Quick script to assign sp.vinod@jacpl.com to Personal plan
"""

from cloudface_pro_pricing import pricing_manager

# Assign Personal plan to sp.vinod@jacpl.com
user_email = "sp.vinod@jacpl.com"
plan = "personal"

print(f"🔧 Assigning {user_email} to {plan} plan...")

pricing_manager.update_subscription(
    user_id=user_email,
    plan=plan,
    payment_data={
        'method': 'manual_assignment',
        'note': 'Assigned by admin'
    }
)

# Verify
subscription = pricing_manager.get_user_subscription(user_email)
print(f"\n✅ Assignment complete!")
print(f"User: {user_email}")
print(f"Plan: {subscription['plan']}")
print(f"Plan Name: {subscription['plan_details']['name']}")
print(f"Storage: {subscription['plan_details']['storage_gb']} GB")
print(f"Photos: {subscription['plan_details']['max_photos']:,}")
print(f"Upload Batch: {subscription['plan_details']['max_upload_batch']} photos at once")
print(f"Status: {subscription['status']}")

