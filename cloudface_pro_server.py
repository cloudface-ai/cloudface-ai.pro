"""
CloudFace Pro - Main Web Server
Production-ready server with real data only
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, Response
from werkzeug.utils import secure_filename
import json
import cloudface_pro_config as config
from cloudface_pro_storage import storage
from cloudface_pro_events import event_manager
from cloudface_pro_processor import processor
from cloudface_pro_auth import auth
from cloudface_pro_guest_auth import guest_auth
from cloudface_pro_pricing import pricing_manager, PLANS
from cloudface_pro_email import email_service
from datetime import datetime
from io import BytesIO
import os
TESTING_MODE = os.environ.get('TESTING_MODE', 'true').lower() == 'true'
from functools import wraps

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Session configuration for production (behind Cloudflare/Nginx)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True only if using HTTPS directly
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Make config available to templates
@app.context_processor
def inject_config():
    return {
        'config': config,
        'current_year': datetime.now().year,
        'user_logged_in': session.get('user_id') is not None,
        'user_email': session.get('user_email'),
        'guest_logged_in': session.get('guest_id') is not None,
        'guest_name': session.get('guest_name'),
        'guest_email': session.get('guest_email')
    }

# ===========================
# AUTHENTICATION DECORATORS
# ===========================

def admin_required(f):
    """Decorator to require admin login (for event hosts)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            # Admin not logged in
            return redirect('/login')
        
        # Check if guest is trying to access admin route
        if session.get('guest_id'):
            return "Access Denied: Guests cannot access admin pages", 403
        
        return f(*args, **kwargs)
    return decorated_function

def guest_required(f):
    """Decorator to require guest login (for event attendees)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('guest_id'):
            # Extract event_id from kwargs or args
            event_id = kwargs.get('event_id') or (args[0] if args else None)
            if event_id:
                return redirect(f'/guest/login/{event_id}')
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def owns_event_required(f):
    """Decorator to ensure user owns the event they're accessing"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check admin login
        user_id = session.get('user_id')
        if not user_id:
            print(f"⚠️ owns_event_required: No user_id in session, redirecting to login")
            return redirect('/admin/login')
        
        # Get event_id from kwargs or args
        event_id = kwargs.get('event_id') or (args[0] if args else None)
        
        if event_id:
            event = event_manager.get_event(event_id)
            if not event:
                print(f"⚠️ owns_event_required: Event {event_id} not found")
                return "Event not found", 404
            
            # Check if user owns this event
            event_user_id = event.get('user_id')
            print(f"🔍 owns_event_required: Checking access for event {event_id}")
            print(f"🔍 Event user_id: {event_user_id}")
            print(f"🔍 Session user_id: {user_id}")
            
            if event_user_id != user_id:
                print(f"⚠️ Access denied: Event owner {event_user_id} != logged in user {user_id}")
                return "Access Denied: You don't have permission to access this event", 403
        
        return f(*args, **kwargs)
    return decorated_function

# Keep backward compatibility
login_required = admin_required

# ===========================
# ADMIN AUTHENTICATION ROUTES
# ===========================

@app.route('/admin/login', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])  # Backward compatibility
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Try to sign in
        result = auth.sign_in(email, password)
        
        if result:
            # Store in session
            session.permanent = True  # Make session last 24 hours
            session['user_id'] = result['user_id']
            session['user_email'] = result['email']
            session['token'] = result['token']
            
            return jsonify({
                'success': True,
                'redirect': '/admin/dashboard'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
    
    return render_template('cloudface_pro/login.html')

@app.route('/admin/signup', methods=['GET', 'POST'])
@app.route('/signup', methods=['GET', 'POST'])  # Backward compatibility
def admin_signup():
    """Admin signup with email verification"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Create account (but mark as unverified)
        result = auth.sign_up(email, password)
        
        if result:
            # Store email and password in session temporarily
            session['pending_verification_email'] = email
            session['pending_verification_password'] = password
            
            # Generate and send verification code
            code = email_service.generate_verification_code(email)
            email_service.send_verification_email(email, code)
            
            return jsonify({
                'success': True,
                'redirect': '/admin/verify-email'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Email already exists or invalid'
            }), 400
    
    return render_template('cloudface_pro/signup.html')

@app.route('/admin/verify-email', methods=['GET', 'POST'])
def admin_verify_email():
    """Verify email with code"""
    if 'pending_verification_email' not in session:
        return redirect('/admin/signup')
    
    email = session.get('pending_verification_email')
    
    if request.method == 'POST':
        data = request.get_json()
        code = data.get('code')
        
        # Verify the code
        if email_service.verify_code(email, code):
            # Code is valid - complete signup
            password = session.get('pending_verification_password')
            result = auth.sign_in(email, password)
            
            if result:
                # Clear pending data
                session.pop('pending_verification_email', None)
                session.pop('pending_verification_password', None)
                
                # Log in user
                session.permanent = True  # Make session last 24 hours
                session['user_id'] = result['user_id']
                session['user_email'] = result['email']
                session['token'] = result['token']
                
                # Send welcome email
                email_service.send_welcome_email(email)
                
                return jsonify({
                    'success': True,
                    'redirect': '/admin/dashboard'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Account verification failed'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired code. Please try again.'
            }), 400
    
    return render_template('cloudface_pro/verify_email.html', email=email)

@app.route('/admin/resend-verification', methods=['POST'])
def admin_resend_verification():
    """Resend verification code"""
    if 'pending_verification_email' not in session:
        return jsonify({'success': False, 'error': 'No pending verification'}), 400
    
    email = session.get('pending_verification_email')
    
    # Generate new code
    code = email_service.generate_verification_code(email)
    email_service.send_verification_email(email, code)
    
    return jsonify({'success': True})

@app.route('/admin/logout')
@app.route('/logout')  # Backward compatibility
def admin_logout():
    """Admin logout"""
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('token', None)
    return redirect('/')

# ===========================
# GUEST AUTHENTICATION
# ===========================

@app.route('/guest/login', methods=['GET', 'POST'])
def guest_login():
    """Guest login (no event needed)"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Sign in
        result = guest_auth.sign_in(email, password)
        
        if result:
            # Store in session
            session.permanent = True  # Make session last 24 hours
            session['guest_id'] = result['guest_id']
            session['guest_email'] = result['email']
            session['guest_name'] = result['name']
            
            # Check if they came from an event page
            last_event_id = session.get('last_event_id')
            if last_event_id:
                # Redirect back to the event they came from
                return jsonify({
                    'success': True,
                    'redirect': f'/e/{last_event_id}'
                })
            else:
                # No event context, go to dashboard
                return jsonify({
                    'success': True,
                    'redirect': '/guest/dashboard'
                })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
    
    return render_template('cloudface_pro/guest_login.html', event=None)

@app.route('/guest/signup', methods=['GET', 'POST'])
def guest_signup():
    """Guest signup (no event needed)"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone', '')
        
        # Create guest account
        result = guest_auth.create_guest(email, password, name, phone)
        
        if result:
            # Store in session
            session.permanent = True  # Make session last 24 hours
            session['guest_id'] = result['guest_id']
            session['guest_email'] = result['email']
            session['guest_name'] = result['name']
            
            # Check if they came from an event page
            last_event_id = session.get('last_event_id')
            if last_event_id:
                # Redirect back to the event they came from
                return jsonify({
                    'success': True,
                    'redirect': f'/e/{last_event_id}'
                })
            else:
                # No event context, go to selfie capture
                return jsonify({
                    'success': True,
                    'redirect': '/guest/capture-selfie'
                })
        else:
            return jsonify({
                'success': False,
                'error': 'Email already exists'
            }), 400
    
    return render_template('cloudface_pro/guest_signup.html', event=None)

@app.route('/guest/capture-selfie', methods=['GET', 'POST'])
def guest_capture_selfie():
    """Capture and store guest selfie during signup"""
    if 'guest_id' not in session:
        return redirect('/guest/signup')
    
    if request.method == 'POST':
        if 'selfie' not in request.files:
            return jsonify({'error': 'No selfie uploaded'}), 400
        
        selfie = request.files['selfie']
        selfie_bytes = selfie.read()
        
        # Validate selfie is not empty
        if not selfie_bytes or len(selfie_bytes) == 0:
            return jsonify({
                'success': False,
                'error': 'Selfie file is empty. Please try again.'
            }), 400
        
        print(f"📸 Received selfie: {len(selfie_bytes)} bytes")
        
        # Save selfie
        guest_id = session.get('guest_id')
        filename = guest_auth.save_guest_selfie(guest_id, selfie_bytes)
        
        if filename:
            return jsonify({
                'success': True,
                'redirect': '/guest/dashboard'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save selfie'
            }), 500
    
    return render_template('cloudface_pro/capture_selfie.html', event=None)

@app.route('/guest/logout')
def guest_logout():
    """Guest logout"""
    session.pop('guest_id', None)
    session.pop('guest_email', None)
    session.pop('guest_name', None)
    session.pop('last_event_id', None)
    return redirect('/')

@app.route('/guest/<guest_id>/selfie')
def get_guest_selfie(guest_id):
    """Serve guest's stored selfie"""
    selfie_bytes = guest_auth.get_guest_selfie(guest_id)
    if not selfie_bytes:
        return "Selfie not found", 404
    
    return send_file(BytesIO(selfie_bytes), mimetype='image/jpeg')

@app.route('/guest/dashboard')
@app.route('/guest/my-events')  # Backward compatibility
def guest_dashboard():
    """Guest dashboard - shows all events they've accessed"""
    if 'guest_id' not in session:
        return redirect('/guest/login')
    
    guest_id = session.get('guest_id')
    guest = guest_auth.get_guest(guest_id)
    
    if not guest:
        return redirect('/guest/login')
    
    # Get event IDs this guest has accessed
    event_ids = guest.get('events_accessed', [])
    
    # Fetch full event details for each
    events = []
    for event_id in event_ids:
        event = event_manager.get_event(event_id)
        if event:
            # Add cover image (first photo as thumbnail)
            photos = storage.list_event_photos(event_id)
            if photos:
                event['cover_image'] = photos[0]
            else:
                event['cover_image'] = None
            
            events.append(event)
    
    # Sort by date (newest first)
    events.sort(key=lambda x: x.get('event_date', ''), reverse=True)
    
    return render_template('cloudface_pro/guest_dashboard.html', events=events)

# ===========================
# PRICING & SUBSCRIPTIONS
# ===========================

@app.route('/admin/pricing')
@app.route('/pricing')  # Public access
def view_pricing():
    """View pricing plans"""
    current_plan = None
    usage = None
    limits = None
    
    if session.get('user_id'):
        # Admin is logged in - show current plan and usage
        subscription = pricing_manager.get_user_subscription(session['user_id'])
        current_plan = subscription['plan_details']
        usage = {
            'photos': subscription.get('photos_used_this_year', 0),
            'storage_gb': subscription.get('storage_used_gb', 0)
        }
        limits = {
            'photos': current_plan['max_photos'],
            'storage_gb': current_plan['storage_gb']
        }
    
    return render_template('cloudface_pro/pricing.html',
                          current_plan=current_plan,
                          usage=usage,
                          limits=limits)

@app.route('/admin/subscribe/<plan>', methods=['GET', 'POST'])
@admin_required
def subscribe_to_plan(plan):
    """Subscribe to a plan (payment integration)"""
    if plan not in PLANS:
        return "Invalid plan", 400
    
    # For now, just update the plan (payment integration comes later)
    if request.method == 'POST' or TESTING_MODE:
        user_id = session.get('user_id')
        pricing_manager.update_subscription(user_id, plan)
        return redirect('/admin/dashboard')
    
    # Show payment page (TODO: Integrate Razorpay/Stripe)
    plan_details = PLANS[plan]
    return render_template('cloudface_pro/subscribe.html', plan=plan, plan_details=plan_details)

# ===========================
# MAIN PAGES
# ===========================

@app.route('/')
def index():
    """Home page - Landing page"""
    return render_template('cloudface_pro/landing.html')

@app.route('/admin/dashboard')
@app.route('/dashboard')  # Backward compatibility
@login_required
def admin_dashboard():
    """Admin dashboard - shows user's events"""
    user_id = session.get('user_id')
    user_email = session.get('user_email')  # Get email for subscription lookup
    
    try:
        # Get user events
        events = event_manager.list_user_events(user_id)
        
        # Add cover image to each event (first photo)
        for event in events:
            photos = storage.list_event_photos(event['event_id'])
            print(f"📸 Event {event['event_id']} ({event.get('event_name', 'Unnamed')}) has {len(photos)} photos")
            if photos:
                # Use the first photo as cover image (thumbnail route will handle the conversion)
                event['cover_image'] = photos[0]
                print(f"📸 Set cover image: {photos[0]}")
            else:
                event['cover_image'] = None
                print(f"📸 No cover image (no photos)")
                
    except Exception as e:
        print(f"⚠️  Error loading events: {e}")
        events = []
    
    # Calculate user stats from events - count actual photos, not just stats
    total_events = len(events)
    total_photos = 0
    total_searches = sum(event.get('stats', {}).get('total_searches', 0) for event in events)
    total_storage_bytes = 0
    
    # Count actual photos from storage for accurate count
    for event in events:
        try:
            photos = storage.list_event_photos(event['event_id'])
            actual_photo_count = len(photos)
            total_photos += actual_photo_count
            
            # Update event stats if they're wrong
            stored_photo_count = event.get('stats', {}).get('total_photos', 0)
            if actual_photo_count != stored_photo_count:
                print(f"🔄 Updating event {event['event_id']} stats: {stored_photo_count} -> {actual_photo_count} photos")
                event_manager.update_event(event['event_id'], {
                    'stats.total_photos': actual_photo_count
                })
                
        except Exception as e:
            print(f"⚠️ Error counting photos for event {event['event_id']}: {e}")
            # Fall back to stored stats
            total_photos += event.get('stats', {}).get('total_photos', 0)
    
    # Calculate storage size
    total_storage_bytes = sum(event.get('stats', {}).get('storage_bytes', 0) for event in events)
    total_storage_gb = total_storage_bytes / (1024 * 1024 * 1024)  # Convert to GB
    
    user_stats = {
        'total_events': total_events,
        'total_photos': total_photos,
        'total_searches': total_searches,
        'total_storage_gb': total_storage_gb
    }
    
    # Get subscription info (use email, not user_id)
    subscription = pricing_manager.get_user_subscription(user_email)
    
    # Debug: Print subscription details
    print(f"🔍 DEBUG Dashboard for user: {user_email}")
    print(f"🔍 Subscription plan: {subscription.get('plan')}")
    print(f"🔍 Plan name: {subscription.get('plan_details', {}).get('name')}")
    
    return render_template('cloudface_pro/dashboard.html',
                          events=events,
                          user_stats=user_stats,
                          subscription=subscription)

@app.route('/admin/events')
@app.route('/events')  # Backward compatibility
@login_required
def admin_events():
    """Admin events page - grid view of all events"""
    user_id = session.get('user_id')
    
    try:
        events = event_manager.list_user_events(user_id)
    except Exception as e:
        print(f"⚠️  Error loading events: {e}")
        events = []
    
    return render_template('cloudface_pro/my_events.html', events=events)

# ===========================
# EVENT MANAGEMENT
# ===========================

@app.route('/admin/events/create', methods=['GET', 'POST'])
@app.route('/events/create', methods=['GET', 'POST'])  # Backward compatibility
@login_required
def admin_create_event():
    """Create new event"""
    if request.method == 'POST':
        user_id = session.get('user_id')
        
        event_data = {
            'event_name': request.form.get('event_name'),
            'event_date': request.form.get('event_date'),
            'event_type': request.form.get('event_type', 'other'),
            'event_details': request.form.get('event_details', ''),
            'company_name': request.form.get('company_name', ''),
            'enable_selling': request.form.get('enable_selling') == 'on',
            'is_public': request.form.get('is_public') == 'on',
            'enable_pin': request.form.get('enable_pin') == 'on',
            'guest_pin': request.form.get('guest_pin', ''),
            'full_access_pin': request.form.get('full_access_pin', ''),
            'enable_watermark': request.form.get('enable_watermark') == 'on',
            'watermark_type': request.form.get('watermark_type', 'text'),
            'watermark_text': request.form.get('watermark_text', ''),
            'watermark_position': request.form.get('watermark_position', 'bottom_left'),
            'watermark_opacity': int(request.form.get('watermark_opacity', 70))
        }
        
        # Handle logo upload
        logo_filename = None
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file.filename:
                logo_filename = secure_filename(logo_file.filename)
                event_data['logo_filename'] = logo_filename
        
        # Handle watermark logo upload
        watermark_logo_filename = None
        if 'watermark_logo' in request.files:
            watermark_logo_file = request.files['watermark_logo']
            if watermark_logo_file.filename:
                watermark_logo_filename = secure_filename(watermark_logo_file.filename)
                event_data['watermark_logo_filename'] = watermark_logo_filename
        
        # Create event
        event_id = event_manager.create_event(user_id, event_data)
        
        # Save logo if provided
        if logo_filename and 'logo' in request.files:
            request.files['logo'].seek(0)  # Reset file pointer
            storage.save_event_logo(event_id, logo_filename, request.files['logo'])
        
        # Save watermark logo if provided
        if watermark_logo_filename and 'watermark_logo' in request.files:
            request.files['watermark_logo'].seek(0)  # Reset file pointer
            storage.save_event_watermark_logo(event_id, watermark_logo_filename, request.files['watermark_logo'])
        
        return jsonify({
            'success': True,
            'event_id': event_id,
            'redirect': f'/events/{event_id}/upload'
        })
    
    return render_template('cloudface_pro/create_event.html')

@app.route('/events/<event_id>/upload', methods=['GET', 'POST'])
@owns_event_required
def upload_photos(event_id):
    """Upload photos to event"""
    if request.method == 'POST':
        try:
            user_id = session.get('user_id')
            user_email = session.get('user_email')  # Get email for subscription lookup
            
            # Handle photo uploads
            files = request.files.getlist('photos')
            
            if not files:
                return jsonify({'error': 'No files uploaded'}), 400
            
            # Prepare files for processing
            photo_files = []
            total_size = 0
            
            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    file.seek(0, 2)  # Seek to end
                    file_size = file.tell()
                    file.seek(0)  # Reset
                    total_size += file_size
                    photo_files.append((filename, file))
            
            if not photo_files:
                return jsonify({'error': 'No valid files found'}), 400
            
            # Check plan limits (use email, not user_id)
            limit_check = pricing_manager.check_can_upload(user_email, len(photo_files), total_size)
            
            if not limit_check['allowed']:
                return jsonify({
                    'error': limit_check['reason'],
                    'upgrade_url': '/admin/pricing'
                }), 403
            
            # Save photos immediately with better memory management
            saved_count = 0
            saved_files = []
            
            for filename, file_obj in photo_files:
                try:
                    file_obj.seek(0)
                    
                    # Check file size to prevent memory issues
                    file_size = len(file_obj.read())
                    file_obj.seek(0)
                    
                    if file_size > 50 * 1024 * 1024:  # 50MB limit per file
                        print(f"⚠️ Skipping large file {filename} ({file_size/1024/1024:.1f}MB)")
                        continue
                    
                    if file_size == 0:
                        print(f"⚠️ Skipping empty file {filename}")
                        continue
                    
                    # Read the file content to memory
                    file_content = file_obj.read()
                    
                    # Save to storage
                    storage.save_event_photo(event_id, filename, BytesIO(file_content))
                    saved_count += 1
                    
                    # Store for background processing (create new BytesIO to avoid memory issues)
                    saved_files.append((filename, BytesIO(file_content)))
                    
                except Exception as e:
                    print(f"⚠️ Error saving {filename}: {e}")
                    continue
            
            if saved_count == 0:
                return jsonify({
                    'error': 'No valid photos could be saved'
                }), 400
            
            # Generate thumbnails immediately (fast operation)
            try:
                thumbnail_count = processor.generate_thumbnails_only(event_id, saved_files)
                print(f"✅ Generated {thumbnail_count} thumbnails immediately")
            except Exception as e:
                print(f"⚠️ Thumbnail generation failed: {e}")
                # Continue anyway - thumbnails are not critical
            
            # Start background processing for face detection only
            try:
                import threading
                processing_thread = threading.Thread(
                    target=processor.process_event_photos_background,
                    args=(event_id, saved_files),
                    daemon=True
                )
                processing_thread.start()
                print(f"🔄 Started background processing for {saved_count} photos")
            except Exception as e:
                print(f"⚠️ Failed to start background processing: {e}")
                # Continue anyway - photos are saved
            
            # Update usage stats (use email, not user_id)
            pricing_manager.increment_usage(user_email, saved_count, total_size)
            
            return jsonify({
                'success': True,
                'message': f'{saved_count} photos uploaded successfully',
                'processing': True,
                'redirect': f'/events/{event_id}'
            })
            
        except Exception as e:
            print(f"❌ Error in upload_photos: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': f'Upload failed: {str(e)}'
            }), 500
    
    # GET: Show upload page
    event = event_manager.get_event(event_id)
    if not event:
        return "Event not found", 404
    
    return render_template('cloudface_pro/upload_photos.html', event=event)

@app.route('/api/events/<event_id>/processing-status')
@owns_event_required
def check_processing_status(event_id):
    """Check if photo processing is complete (Admin only - must own event)"""
    try:
        event = event_manager.get_event(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        status = event.get('status', 'unknown')
        
        # Check for completion file in testing mode
        completion_data = None
        testing_mode = os.environ.get('TESTING_MODE', 'true').lower() == 'true'
        if testing_mode:
            completion_file = f'storage/cloudface_pro/events/{event_id}/processing_complete.json'
            if os.path.exists(completion_file):
                try:
                    with open(completion_file, 'r') as f:
                        completion_data = json.load(f)
                except Exception as e:
                    print(f"⚠️ Error reading completion file: {e}")
                    pass
        
        return jsonify({
            'status': status,
            'completed': status == 'ready',
            'completion_data': completion_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<event_id>/upload-progress')
@owns_event_required
def upload_progress(event_id):
    """Get upload progress for large batches"""
    try:
        # Count photos in storage
        event_path = f'storage/cloudface_pro/events/{event_id}/photos'
        if os.path.exists(event_path):
            photo_count = len([f for f in os.listdir(event_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))])
            
            return jsonify({
                'success': True,
                'photos_uploaded': photo_count,
                'status': 'uploading' if photo_count > 0 else 'pending'
            })
        else:
            return jsonify({
                'success': True,
                'photos_uploaded': 0,
                'status': 'pending'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/events/<event_id>')
@app.route('/events/<event_id>')  # Backward compatibility
@owns_event_required
def admin_view_event(event_id):
    """View event details (Admin only - must own event)"""
    event = event_manager.get_event(event_id)
    if not event:
        return "Event not found", 404
    
    # Get photo list
    photos = storage.list_event_photos(event_id)
    
    return render_template('cloudface_pro/view_event.html',
                          event=event,
                          photos=photos)

@app.route('/admin/events/<event_id>/delete', methods=['POST'])
@app.route('/events/<event_id>/delete', methods=['POST'])  # Backward compatibility
@owns_event_required
def admin_delete_event(event_id):
    """Delete event (Admin only - must own event)"""
    event_manager.delete_event(event_id)
    return redirect('/admin/dashboard')

# ===========================
# PUBLIC EVENT ACCESS
# ===========================

@app.route('/e/<event_id>')
def public_event(event_id):
    """Public event landing page - requires guest login"""
    event = event_manager.get_event(event_id)
    if not event:
        return "Event not found", 404
    
    # Store last accessed event
    session['last_event_id'] = event_id
    
    # Check if guest is logged in
    guest_id = session.get('guest_id')
    guest_selfie_url = None
    
    if guest_id:
        # Guest is logged in - track this event access
        guest_auth.track_event_access(guest_id, event_id)
        
        # Get their stored selfie
        guest = guest_auth.get_guest(guest_id)
        if guest and guest.get('selfie_filename'):
            guest_selfie_url = f"/guest/{guest_id}/selfie"
    
    return render_template('cloudface_pro/public_event.html', 
                          event=event,
                          guest_logged_in=guest_id is not None,
                          guest_name=session.get('guest_name'),
                          guest_selfie_url=guest_selfie_url)

@app.route('/e/<event_id>/search', methods=['POST'])
def search_event(event_id):
    """Search for face in event"""
    if 'selfie' not in request.files:
        return jsonify({'error': 'No selfie uploaded'}), 400
    
    selfie = request.files['selfie']
    selfie_bytes = selfie.read()
    
    # Search for matches
    matches = processor.search_face_in_event(event_id, selfie_bytes)
    
    return jsonify({
        'success': True,
        'matches': matches,
        'total': len(matches)
    })

# ============================================================
# 🚨 CRITICAL: REAL-TIME STREAMING SEARCH - DO NOT REMOVE! 🚨
# This endpoint streams results one-by-one as photos are found
# Makes the UI responsive and exciting for guests
# ============================================================
@app.route('/e/<event_id>/search-stream', methods=['POST'])
def search_event_stream(event_id):
    """Search for face in event with real-time streaming"""
    if 'selfie' not in request.files:
        return jsonify({'error': 'No selfie uploaded'}), 400
    
    selfie = request.files['selfie']
    selfie_bytes = selfie.read()
    
    def generate():
        try:
            # Get all photos in event
            photos = storage.list_event_photos(event_id)
            total_photos = len(photos)
            processed = 0
            
            yield f"data: {json.dumps({'type': 'start', 'total_photos': total_photos})}\n\n"
            
            matches = []
            
            # Process photos one by one and stream results
            for photo_filename in photos:
                try:
                    # Get photo bytes
                    photo_bytes = storage.get_event_photo(event_id, photo_filename)
                    if not photo_bytes:
                        continue
                    
                    # Search in this specific photo
                    photo_matches = processor.search_face_in_single_photo(photo_bytes, selfie_bytes, photo_filename)
                    
                    if photo_matches:
                        matches.extend(photo_matches)
                        # Stream each match immediately
                        for match in photo_matches:
                            yield f"data: {json.dumps({'type': 'match', 'match': match})}\n\n"
                    
                    processed += 1
                    
                    # Send progress update every 10 photos
                    if processed % 10 == 0:
                        yield f"data: {json.dumps({'type': 'progress', 'processed': processed, 'total': total_photos, 'matches': len(matches)})}\n\n"
                
                except Exception as e:
                    print(f"⚠️ Error processing {photo_filename}: {e}")
                    processed += 1
                    continue
            
            # Send final completion
            yield f"data: {json.dumps({'type': 'complete', 'matches': matches, 'total': len(matches)})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

# ===========================
# PHOTO SERVING
# ===========================

@app.route('/events/<event_id>/photo/<filename>')
def serve_photo(event_id, filename):
    """Serve event photo"""
    photo_bytes = storage.get_event_photo(event_id, filename)
    if not photo_bytes:
        return "Photo not found", 404
    
    return send_file(BytesIO(photo_bytes), mimetype='image/jpeg')

@app.route('/events/<event_id>/thumbnail/<filename>')
def serve_thumbnail(event_id, filename):
    """Serve event thumbnail"""
    thumb_bytes = storage.get_event_thumbnail(event_id, filename)
    if not thumb_bytes:
        return "Thumbnail not found", 404
    
    return send_file(BytesIO(thumb_bytes), mimetype='image/jpeg')

@app.route('/events/<event_id>/logo/<filename>')
def serve_logo(event_id, filename):
    """Serve event logo"""
    logo_path = f"events/{event_id}/logo/{filename}"
    logo_bytes = storage.get_file(logo_path)
    if not logo_bytes:
        return "Logo not found", 404
    
    return send_file(BytesIO(logo_bytes), mimetype='image/png')

@app.route('/events/<event_id>/download/<filename>')
def download_photo(event_id, filename):
    """Download photo with watermark if enabled"""
    from cloudface_pro_watermark import watermark_processor
    
    # Get original photo
    photo_bytes = storage.get_event_photo(event_id, filename)
    if not photo_bytes:
        return "Photo not found", 404
    
    # Get event data for watermark settings
    event = event_manager.get_event(event_id)
    if not event:
        return "Event not found", 404
    
    # Add watermark if enabled
    if event.get('enable_watermark', False):
        # Add event_id to event data for watermark processor
        event['event_id'] = event_id
        photo_bytes = watermark_processor.add_watermark_to_image(photo_bytes, event)
    
    return send_file(
        BytesIO(photo_bytes), 
        mimetype='image/jpeg',
        as_attachment=True,
        download_name=filename
    )

@app.route('/e/<event_id>/download-zip', methods=['POST'])
def download_photos_zip(event_id):
    """Download multiple photos as ZIP with watermarks"""
    from cloudface_pro_watermark import watermark_processor
    import zipfile
    from io import BytesIO
    
    try:
        data = request.get_json()
        filenames = data.get('filenames', [])
        
        if not filenames:
            return "No photos specified", 400
        
        # Get event data for watermark settings
        event = event_manager.get_event(event_id)
        if not event:
            return "Event not found", 404
        
        # Create ZIP in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename in filenames:
                # Get original photo
                photo_bytes = storage.get_event_photo(event_id, filename)
                if photo_bytes:
                    # Add watermark if enabled
                    if event.get('enable_watermark', False):
                        # Add event_id to event data for watermark processor
                        event['event_id'] = event_id
                        photo_bytes = watermark_processor.add_watermark_to_image(photo_bytes, event)
                    
                    # Add to ZIP
                    zip_file.writestr(filename, photo_bytes)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'{event_id}_photos.zip'
        )
        
    except Exception as e:
        print(f"❌ ZIP creation error: {e}")
        return "Failed to create ZIP", 500

# ===========================
# API ENDPOINTS
# ===========================

@app.route('/api/storage/stats')
def storage_stats():
    """Get storage statistics"""
    stats = storage.get_total_storage_used()
    return jsonify(stats)

@app.route('/api/events/<event_id>/stats')
@owns_event_required
def event_stats(event_id):
    """Get event statistics (Admin only - must own event)"""
    event = event_manager.get_event(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    return jsonify(event.get('stats', {}))

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Receive AI feedback from guests"""
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        rating = data.get('rating')
        total_matches = data.get('total_matches')
        timestamp = data.get('timestamp')
        
        # Store feedback in event analytics
        feedback_data = {
            'rating': rating,
            'total_matches': total_matches,
            'timestamp': timestamp
        }
        
        # Get event and append feedback
        event = event_manager.get_event(event_id)
        if event:
            # Store in analytics
            import os
            TESTING_MODE = os.environ.get('TESTING_MODE', 'true').lower() == 'true'
            
            if TESTING_MODE:
                db = event_manager._load_local_db()
                if event_id in db:
                    if 'analytics' not in db[event_id]:
                        db[event_id]['analytics'] = {}
                    if 'feedback' not in db[event_id]['analytics']:
                        db[event_id]['analytics']['feedback'] = []
                    
                    db[event_id]['analytics']['feedback'].append(feedback_data)
                    event_manager._save_local_db(db)
        
        print(f"📊 Feedback received for {event_id}: {rating}/4 stars ({total_matches} matches)")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ Error saving feedback: {e}")
        return jsonify({'success': False}), 500

# ===========================
# ERROR HANDLERS
# ===========================

@app.errorhandler(404)
def not_found(e):
    return render_template('cloudface_pro/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('cloudface_pro/500.html'), 500

# ===========================
# START SERVER
# ===========================

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 CloudFace Pro - Production Server")
    print("=" * 70)
    print(f"📦 Storage: {config.STORAGE_TYPE}")
    print(f"📧 Contact: {config.CONTACT_EMAIL}")
    print(f"📱 Phone: {config.CONTACT_PHONE_DISPLAY}")
    print(f"🎨 Theme: Google Blue + Firebase Orange")
    print(f"🔧 Mode: Production (Real Data Only)")
    print("=" * 70)
    print("\n🌐 Server starting on: http://localhost:5002")
    print("   • Home: http://localhost:5002/")
    print("   • Dashboard: http://localhost:5002/dashboard")
    print("   • Create Event: http://localhost:5002/events/create")
    print("\n")
    
    app.run(debug=True, port=5002, host='0.0.0.0')

