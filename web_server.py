#!/usr/bin/env python3
"""
Facetak Web Server
Connects HTML frontend to existing Python backend with OAuth integration
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
import os
import tempfile
import uuid
import requests
from werkzeug.utils import secure_filename
from urllib.parse import urlencode, parse_qs, urlparse

# Import your existing modules
from flow_controller import process_drive_folder_and_store
from search_handler import search_for_person
from progress_endpoint import create_progress_endpoint
from local_cache import get_cache_stats

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production

# Add progress tracking endpoints
create_progress_endpoint(app)

# Configuration
UPLOAD_FOLDER = 'storage/temp/selfies'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'heic'}

# Google OAuth Configuration
from dotenv import load_dotenv
load_dotenv('example.env')

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8550/auth/callback')
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/drive.readonly'
]

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_authenticated():
    """Check if user is authenticated and has valid tokens"""
    return 'access_token' in session and 'user_info' in session

def get_google_auth_url():
    """Generate Google OAuth URL"""
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'scope': ' '.join(GOOGLE_SCOPES),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

@app.route('/')
def landing():
    """Show the landing/marketing page"""
    return render_template('landing.html')

@app.route('/app')
def index():
    """Show the main app interface"""
    return render_template('index.html')

@app.route('/contact')
def contact():
    """Show the contact page"""
    return render_template('contact.html')

@app.route('/about')
def about():
    """Show the about page"""
    return render_template('about.html')

@app.route('/blog')
def blog():
    """Show the blog page"""
    return render_template('blog.html')

@app.route('/privacy')
def privacy():
    """Show the privacy policy page"""
    return render_template('privacy.html')

@app.route('/refund')
def refund():
    """Show the refund policy page"""
    return render_template('refund.html')

@app.route('/terms')
def terms():
    """Show the terms and conditions page"""
    return render_template('terms.html')

@app.route('/pricing')
def pricing():
    """Show the pricing page"""
    return render_template('pricing.html')

@app.route('/auth/login')
def google_login():
    """Redirect to Google OAuth"""
    auth_url = get_google_auth_url()
    return redirect(auth_url)

@app.route('/auth/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get authorization code from callback
        code = request.args.get('code')
        if not code:
            return jsonify({'success': False, 'error': 'No authorization code received'})
        
        # Exchange code for tokens
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_REDIRECT_URI
        }
        
        response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        if response.status_code != 200:
            return jsonify({'success': False, 'error': f'Token exchange failed: {response.text}'})
        
        tokens = response.json()
        
        # Get user info
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        user_response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        if user_response.status_code != 200:
            return jsonify({'success': False, 'error': f'Failed to get user info: {user_response.text}'})
        
        user_info = user_response.json()
        
        # Store in session
        session['access_token'] = tokens['access_token']
        session['refresh_token'] = tokens.get('refresh_token')
        session['user_info'] = user_info
        session['user_id'] = user_info['email']
        
        print(f"✅ User authenticated: {user_info['email']}")
        print(f"✅ Access token: {tokens['access_token'][:20]}...")
        
        # Redirect back to main page
        return redirect('/app')
        
    except Exception as e:
        print(f"❌ OAuth callback error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/auth/logout')
def logout():
    """Clear user session"""
    session.clear()
    return redirect('/')

@app.route('/auth/status')
def auth_status():
    """Check authentication status"""
    if is_authenticated():
        return jsonify({
            'authenticated': True,
            'user': session['user_info']
        })
    else:
        return jsonify({
            'authenticated': False,
            'login_url': '/auth/login'
        })

@app.route('/process_drive', methods=['POST'])
def process_drive():
    """Process Google Drive folder - connects to your existing code"""
    try:
        # Check authentication
        if not is_authenticated():
            return jsonify({'success': False, 'error': 'Not authenticated. Please sign in with Google first.'})
        
        data = request.get_json()
        drive_url = data.get('drive_url')
        force_reprocess = data.get('force_reprocess', False)
        
        if not drive_url:
            return jsonify({'success': False, 'error': 'No drive URL provided'})
        
        # Use real access token from session
        user_id = session['user_id']
        access_token = session['access_token']
        
        print(f"🔍 Starting background processing for user: {user_id}")
        print(f"🔑 Using access token: {access_token[:20]}...")
        
        # Start processing in background thread to avoid Railway timeout
        import threading
        from progress_tracker import start_progress, stop_progress, set_status, set_total, increment
        
        def background_process():
            try:
                # Start progress tracking
                start_progress()
                
                result = process_drive_folder_and_store(
                    user_id=user_id,
                    url=drive_url,
                    access_token=access_token,
                    force_reprocess=force_reprocess
                )
                
                # Stop progress tracking
                stop_progress()
                print(f"✅ Background processing completed for user {user_id}")
            except Exception as e:
                stop_progress()
                print(f"❌ Background processing failed for user {user_id}: {e}")
        
        # Start background thread
        thread = threading.Thread(target=background_process, daemon=True)
        thread.start()
        
        # Return immediately to avoid timeout
        return jsonify({
            'success': True,
            'message': 'Processing started in background. Check terminal for progress.',
            'status': 'processing'
        })
        
    except Exception as e:
        print(f"Error starting drive processing: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/search', methods=['POST'])
def search():
    """Search for person using uploaded selfie - connects to your existing code"""
    try:
        # Check if file was uploaded
        if 'selfie' not in request.files:
            return jsonify({'success': False, 'error': 'No selfie file uploaded'})
        
        file = request.files['selfie']
        threshold = float(request.form.get('threshold', 0.8))
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'})
        
        # Save uploaded file to temp storage
        filename = secure_filename(file.filename)
        unique_filename = f"selfie_{uuid.uuid4().hex}{os.path.splitext(filename)[1]}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        file.save(file_path)
        
        # Get user ID from session - must be authenticated
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated. Please sign in first.'})
        
        user_id = session['user_id']
        
        print(f"🔍 Searching for person with selfie: {file_path}")
        print(f"👤 User ID: {user_id}")
        
        # Call your existing search function
        matches = search_for_person(file_path, user_id, threshold)
        
        if not matches:
            return jsonify({
                'success': True,
                'matches': [],
                'message': 'No matches found'
            })
        
        # Format matches for frontend
        formatted_matches = []
        for match in matches:
            if isinstance(match, dict):
                # Extract photo reference and similarity score
                photo_ref = match.get('photo_reference', 'Unknown')
                similarity_score = match.get('similarity_score', 0.0)  # Use the pre-calculated similarity
                
                # Get just the filename from the full path for display
                photo_name = os.path.basename(photo_ref) if photo_ref != 'Unknown' else 'Unknown'
                
                # Debug: Print what we're getting from search
                print(f"🔍 Match data: photo_ref={photo_ref}, similarity={similarity_score}")
                print(f"🔍 Formatted: photo_name={photo_name}, photo_path={photo_ref}")
                
                formatted_matches.append({
                    'photo_name': photo_name,
                    'photo_path': photo_ref,  # Use full path for serving photos
                    'similarity': similarity_score
                })
        
        return jsonify({
            'success': True,
            'matches': formatted_matches,
            'message': f'Found {len(formatted_matches)} matches'
        })
        
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/photo/<path:filename>')
def serve_photo(filename):
    """Serve photos from user's storage folder"""
    try:
        print(f"🔍 Serving photo: {filename}")
        
        # Get user ID from session - must be authenticated
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated. Please sign in first.'}), 401
        
        user_id = session['user_id']
        user_storage_path = os.path.join('storage', 'data', user_id)
        
        print(f"   👤 User ID: {user_id}")
        print(f"   📁 User storage path: {user_storage_path}")
        
        if os.path.exists(user_storage_path):
            print(f"   🔍 Searching in user folder: {user_storage_path}")
            # Search recursively through all subdirectories
            for root, dirs, files in os.walk(user_storage_path):
                print(f"      Checking directory: {root}")
                print(f"      Files in this dir: {files[:5]}...")  # Show first 5 files
                if filename in files:
                    full_path = os.path.join(root, filename)
                    print(f"   ✅ Found at: {full_path}")
                    return send_from_directory(root, filename)
        else:
            print(f"   ❌ User storage path does not exist: {user_storage_path}")
        
        # Fallback: also check temp folder for uploaded selfies
        temp_path = os.path.join('storage', 'temp', 'selfies')
        if os.path.exists(temp_path) and filename in os.listdir(temp_path):
            print(f"   ✅ Found in temp folder: {temp_path}")
            return send_from_directory(temp_path, filename)
        
        print(f"   ❌ Photo not found: {filename}")
        print(f"   📂 Available directories in storage/data:")
        if os.path.exists('storage/data'):
            for user_dir in os.listdir('storage/data'):
                user_path = os.path.join('storage/data', user_dir)
                if os.path.isdir(user_path):
                    print(f"      - {user_dir}/")
                    for subdir in os.listdir(user_path)[:3]:  # Show first 3 subdirs
                        subdir_path = os.path.join(user_path, subdir)
                        if os.path.isdir(subdir_path):
                            print(f"        - {subdir}/")
                            # Check if our filename is in this subdir
                            if os.path.exists(subdir_path):
                                files_in_subdir = os.listdir(subdir_path)
                                if filename in files_in_subdir:
                                    print(f"          ✅ FOUND {filename} in {subdir}/")
                                else:
                                    print(f"          Files in {subdir}/: {files_in_subdir[:5]}...")
        return jsonify({'error': 'Photo not found'}), 404
        
    except Exception as e:
        print(f"Error serving photo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/cache_stats')
def cache_stats():
    """Get cache statistics"""
    try:
        # Get user ID from session - must be authenticated
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated. Please sign in first.'}), 401
        
        user_id = session['user_id']
        stats = get_cache_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug_storage')
def debug_storage():
    """Debug route to see what's in storage"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        user_storage_path = os.path.join('storage', 'data', user_id)
        
        if not os.path.exists(user_storage_path):
            return jsonify({'error': f'User storage path does not exist: {user_storage_path}'})
        
        storage_info = {
            'user_id': user_id,
            'storage_path': user_storage_path,
            'exists': os.path.exists(user_storage_path),
            'directories': [],
            'total_files': 0
        }
        
        for root, dirs, files in os.walk(user_storage_path):
            rel_path = os.path.relpath(root, user_storage_path)
            if rel_path == '.':
                rel_path = 'root'
            
            storage_info['directories'].append({
                'path': rel_path,
                'file_count': len(files),
                'sample_files': files[:5]  # First 5 files
            })
            storage_info['total_files'] += len(files)
        
        return jsonify(storage_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/find_file/<filename>')
def find_file(filename):
    """Find a specific file in storage"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        user_storage_path = os.path.join('storage', 'data', user_id)
        
        if not os.path.exists(user_storage_path):
            return jsonify({'error': f'User storage path does not exist: {user_storage_path}'})
        
        found_locations = []
        
        for root, dirs, files in os.walk(user_storage_path):
            if filename in files:
                rel_path = os.path.relpath(root, user_storage_path)
                if rel_path == '.':
                    rel_path = 'root'
                found_locations.append({
                    'directory': rel_path,
                    'full_path': os.path.join(root, filename)
                })
        
        return jsonify({
            'filename': filename,
            'user_id': user_id,
            'found': len(found_locations) > 0,
            'locations': found_locations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Folder browsing functionality temporarily disabled to fix Google Drive processing

if __name__ == '__main__':
    # Get port from environment variable (for Railway) or use default
    port = int(os.environ.get('PORT', 8550))
    
    print("🚀 Starting Facetak Web Server with OAuth...")
    print(f"🔑 OAuth Client ID: {GOOGLE_CLIENT_ID[:20]}...")
    print(f"🌐 Redirect URI: {GOOGLE_REDIRECT_URI}")
    print(f"📱 Open http://localhost:{port} in your browser")
    print("⚠️  Auto-reload disabled to prevent connection issues during processing")
    app.run(debug=False, host='0.0.0.0', port=port)
