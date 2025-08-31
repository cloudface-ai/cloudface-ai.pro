# main_app.py - Google OAuth Authentication + Supabase Database
import flet as ft
from supabase import create_client, Client
from flow_controller import process_drive_folder_and_store
from search_handler import search_for_person
from auth_handler import get_google_login_url, exchange_code_for_tokens, get_user_info, create_test_user
from local_cache import list_cached_images
import os
import time
from dotenv import load_dotenv

# Load Supabase credentials from example.env (for database operations only)
load_dotenv('example.env')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

# Supabase client initialization

# Initialize Supabase client (optional for now)
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized successfully")
    except Exception as e:
        print(f"⚠️  Failed to initialize Supabase client: {e}")
        supabase = None
else:
    print("⚠️  Supabase credentials not found - running in local mode")
    print("   Database operations will be simulated locally")

# Check if required tables exist
def check_database_setup():
    """Check if required database tables exist and create them if needed."""
    try:
        print("🔍 Checking database setup...")
        
        # Check if Supabase is available
        if not supabase:
            print("⚠️  Supabase not available - running in local mode")
            print("   Database operations will be simulated locally")
            return True  # Allow app to run in local mode
        
        # Try to access the faces table
        result = supabase.table('faces').select('count', count='exact').limit(1).execute()
        print("✅ faces table exists and is accessible")
        return True
    except Exception as e:
        print(f"❌ faces table issue: {e}")
        print("📋 You need to create the faces table in Supabase!")
        print("Run this SQL in your Supabase SQL Editor:")
        print("""
        -- Create faces table
        CREATE TABLE IF NOT EXISTS faces (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id TEXT NOT NULL,
            photo_reference TEXT NOT NULL,
            face_embedding JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create index for faster user_id lookups
        CREATE INDEX IF NOT EXISTS idx_faces_user_id ON faces(user_id);
        
        -- Create index for face embedding similarity searches
        CREATE INDEX IF NOT EXISTS idx_faces_embedding ON faces USING GIN (face_embedding);
        
        -- Enable RLS
        ALTER TABLE faces ENABLE ROW LEVEL SECURITY;
        
        -- Create RLS policy for users to access their own data
        CREATE POLICY "Users can access their own faces" ON faces
            FOR ALL USING (auth.jwt() ->> 'email' = user_id);
        """)
        return False

def main(page: ft.Page):
    page.title = "Facetak - AI Photo Finder"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # Check database setup first
    if not check_database_setup():
        print("⚠️  Database setup incomplete - authentication may not work properly")

    # --- Google OAuth Authentication Functions ---
    # (Google OAuth flow for secure authentication)
    
    def save_session_to_storage(page, user_info):
        """Save user session to localStorage for persistence."""
        try:
            import json
            session_data = {
                'user_info': user_info,
                'timestamp': time.time()
            }
            page.client_storage.set("facetak_session", json.dumps(session_data))
            print("💾 Session saved to localStorage")
        except Exception as e:
            print(f"⚠️ Could not save session to storage: {e}")
    
    def load_session_from_storage(page):
        """Load user session from localStorage if available."""
        try:
            import json
            session_data = page.client_storage.get("facetak_session")
            if session_data:
                data = json.loads(session_data)
                # Check if session is not too old (24 hours)
                if time.time() - data.get('timestamp', 0) < 86400:
                    print("🔄 Session restored from localStorage")
                    return data.get('user_info')
                else:
                    print("⏰ Session expired, clearing localStorage")
                    page.client_storage.remove("facetak_session")
            return None
        except Exception as e:
            print(f"⚠️ Could not load session from storage: {e}")
            return None
    
    def clear_session_storage(page):
        """Clear user session from localStorage."""
        try:
            page.client_storage.remove("facetak_session")
            print("🗑️ Session cleared from localStorage")
        except Exception as e:
            print(f"⚠️ Could not clear session storage: {e}")

    def create_login_view():
        """Builds and returns the login screen UI."""
        def handle_google_login(e):
            """Handle Google OAuth authentication."""
            try:
                print("🚀 Starting Google OAuth authentication flow...")
                
                # Test Google OAuth setup first
                from auth_handler import test_google_setup
                if not test_google_setup():
                    print("❌ Google OAuth setup failed")
                    page.add(ft.Text("❌ Google OAuth setup failed - check your API keys in example.env", color="red"))
                    page.update()
                    return
                
                # Get Google OAuth login URL
                login_url = get_google_login_url()
                if not login_url:
                    print("❌ Failed to generate Google OAuth login URL")
                    page.add(ft.Text("❌ Failed to generate Google OAuth login URL", color="red"))
                    page.update()
                    return
                
                print(f"✅ Google OAuth login URL generated successfully")
                print(f"🔗 Login URL: {login_url}")
                
                # Launch the Google OAuth sign-in page
                page.launch_url(login_url, web_window_name="_self")
                
            except Exception as e:
                print(f"❌ Google OAuth authentication error: {e}")
                page.add(ft.Text(f"Google OAuth Authentication Error: {e}", color="red"))
                page.update()
        
        return ft.Column([
            ft.Text("Welcome to Facetak", size=40, weight=ft.FontWeight.BOLD),
            ft.Text("AI-Powered Photo Finder", size=20, color="grey600"),
            ft.Divider(),
            ft.Text("Sign in with Google (Secure OAuth Authentication)", size=16, color="grey600"),
            ft.ElevatedButton("Sign in with Google", on_click=handle_google_login, style=ft.ButtonStyle(
                color="white",
                bgcolor="red600",
                padding=20
            )),
            ft.Text("Google OAuth provides secure authentication and Drive access", size=12, color="grey500"),
            ft.Divider(),
            ft.Text("🔧 For testing: Check console for authentication flow details", size=10, color="grey500")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)

    def debug_session():
        """Debug session storage issues."""
        print("🔍 Debugging session storage...")
        
        try:
            # Test 1: Basic session access
            print("Test 1: Basic session access")
            user_info = page.session.get("user_info")
            print(f"  user_info: {user_info}")
            
            # Test 2: Safe email access
            print("Test 2: Safe email access")
            if user_info:
                email = user_info.get("email", "No email")
                print(f"  email: {email}")
            else:
                print("  user_info is None")
            
            # Test 3: Session keys
            print("Test 3: Session keys")
            print(f"  All session keys: {list(page.session.keys()) if hasattr(page.session, 'keys') else 'No keys method'}")
            
        except Exception as e:
            print(f"❌ Session debug error: {e}")
            import traceback
            traceback.print_exc()

    def handle_signout(e):
        """Handle proper signout process."""
        print("🚪 User requested signout")
        
        # Show loading message
        page.clean()
        page.add(ft.Column([
            ft.Text("Signing out...", size=24, weight=ft.FontWeight.BOLD),
            ft.ProgressRing(),
            ft.Text("Please wait while we sign you out from all services.", size=16, color="grey600")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True))
        page.update()
        
        # Small delay to show the message, then redirect to logout route
        import threading
        import time
        
        def delayed_logout():
            time.sleep(1.5)  # Show message for 1.5 seconds
            page.go("/logout")
        
        threading.Thread(target=delayed_logout, daemon=True).start()

    def show_login_again():
        """Show the login view again after signout."""
        print("🔄 User wants to sign in again")
        page.clean()
        page.add(create_login_view())
        page.update()

    def create_main_app_view():
        """Builds and returns your complete Facetak application UI."""
        
        # --- UI Components ---
        drive_url_field = ft.TextField(
            label="Google Drive Folder URL",
            hint_text="Paste your Google Drive folder URL here",
            value="",
            expand=True,
            helper_text="Example: https://drive.google.com/drive/folders/1ABC123..."
        )
        
        process_ring = ft.ProgressRing(visible=False)
        process_status = ft.Text("Ready to process Google Drive photos")
        
        # Add force reprocess checkbox
        force_reprocess_checkbox = ft.Checkbox(
            label="Force reprocess (ignore cache)",
            value=False
        )
        
        # Add cache statistics display
        cache_stats_text = ft.Text("Cache statistics will appear here", size=12, color="grey600")
        
        selfie_path = ft.Text("")
        search_ring = ft.ProgressRing(visible=False)
        search_status = ft.Text("Upload a selfie to search")
        
        threshold_slider = ft.Slider(
            min=0.1,
            max=1.0,
            divisions=18,
            value=0.65,
            label="{value}",
            expand=True
        )
        
        results_grid = ft.GridView(
            expand=1,
            runs_count=5,
            max_extent=150,
            child_aspect_ratio=1.0,
            spacing=10,
            run_spacing=10,
        )

        # --- Event Handlers ---
        def update_cache_stats():
            """Update cache statistics display."""
            try:
                user_info = page.session.get("user_info")
                if user_info:
                    user_id = user_info.get("email", "unknown_user")
                    from local_cache import get_cache_stats
                    stats = get_cache_stats(user_id)
                    
                    cache_stats_text.value = (
                        f"📊 Cache Stats: {stats['photos_count']} photos, "
                        f"{stats['embeddings_count']} embeddings, "
                        f"{stats['total_photo_size'] / (1024*1024):.1f}MB photos, "
                        f"{stats['total_embedding_size'] / 1024:.1f}KB embeddings"
                    )
                    page.update()
            except Exception as e:
                cache_stats_text.value = f"⚠️ Could not load cache stats: {e}"
                page.update()
        
        def process_drive_folder_click(e):
            # Use session for user ID and access token
            try:
                user_info = page.session.get("user_info")
                if not user_info:
                    process_status.value = "Error: User not logged in."
                    page.update()
                    return
                user_id = user_info.get("email", "unknown_user")
                access_token = user_info.get("access_token")
                if not access_token:
                    process_status.value = "Error: No access token available. Please sign in again."
                    page.update()
                    return
            except Exception as e:
                process_status.value = f"Error getting user session: {e}"
                page.update()
                return

            drive_url = drive_url_field.value
            if not drive_url:
                process_status.value = "Error: Please enter a Google Drive URL."
                page.update()
                return
            
            process_ring.visible = True
            force_reprocess = force_reprocess_checkbox.value
            if force_reprocess:
                process_status.value = "🔄 Force reprocessing Google Drive folder... this may take a while."
            else:
                process_status.value = "Processing Google Drive folder... checking cache first."
            page.update()

            try:
                # Use the flow controller to process the Google Drive folder
                result = process_drive_folder_and_store(user_id, drive_url, access_token, force_reprocess)
                
                process_ring.visible = False
                process_status.value = (
                    f"✅ Processing complete! "
                    f"Total: {result['total_count']} files, "
                    f"New embeddings: {result['embedded_count']}, "
                    f"Skipped (cached): {result['skipped_count']}"
                )
                
                # Update cache statistics after processing
                update_cache_stats()
                page.update()
                
            except Exception as e:
                process_ring.visible = False
                process_status.value = f"❌ Error processing Google Drive folder: {str(e)}"
                page.update()

        def search_click(e):
            # Use session for user ID
            try:
                user_info = page.session.get("user_info")
                if not user_info:
                    search_status.value = "Error: User not logged in."
                    page.update()
                    return
                user_id = user_info.get("email", "unknown_user")
            except Exception as e:
                search_status.value = f"Error getting user session: {e}"
                page.update()
                return

            if not selfie_path.value:
                search_status.value = "Error: Please upload a selfie first."
                page.update()
                return

            search_ring.visible = True
            results_grid.controls.clear()
            search_status.value = f"Searching with threshold: {threshold_slider.value:.2f}..."
            page.update()

            matched_files = search_for_person(
                selfie_path.value, 
                user_id, 
                threshold_slider.value
            )

            if matched_files:
                search_status.value = f"✅ Found {len(matched_files)} matches!"
                
                for match in matched_files:
                    photo_name = match.get("photo_name", "")
                    similarity_percent = match.get("similarity_percent", "0%")
                    
                    # Try to find the photo in the cached storage
                    cached_photos = []
                
                    # Look in all cached folders for this user
                    base_cache_dir = os.path.join("storage", "data", user_id.replace("/", "_"))
                    if os.path.exists(base_cache_dir):
                        for folder_name in os.listdir(base_cache_dir):
                            folder_path = os.path.join(base_cache_dir, folder_name)
                            if os.path.isdir(folder_path):
                                cached_photos.extend(list_cached_images(user_id, folder_name))
                    
                    # Find the matching photo
                    found_photo = None
                    for photo_path in cached_photos:
                        if os.path.basename(photo_path) == photo_name:
                            found_photo = photo_path
                            break
                    
                    if found_photo and os.path.exists(found_photo):
                        # Create a clickable photo card with download functionality and similarity score
                        photo_card = ft.Container(
                            content=ft.Column([
                                ft.Image(
                                    src=found_photo, 
                                    fit=ft.ImageFit.COVER, 
                                    border_radius=ft.border_radius.all(10),
                                    width=200,
                                    height=150
                                ),
                                ft.Text(f"📷 {os.path.basename(found_photo)}", size=12, text_align=ft.TextAlign.CENTER),
                                ft.Text(f"🎯 Match: {similarity_percent}", size=14, weight=ft.FontWeight.BOLD, color="green"),
                                ft.ElevatedButton(
                                    "Download",
                                    on_click=lambda e, path=found_photo: download_photo(path),
                                    style=ft.ButtonStyle(
                                        color="white",
                                        bgcolor="green600",
                                        padding=5
                                    )
                                )
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=10,
                            border=ft.border.all(1, "gray"),
                            border_radius=10,
                            margin=5
                        )
                        results_grid.controls.append(photo_card)
                    else:
                        # Fallback: show photo name if file not found
                        results_grid.controls.append(ft.Text(f"📷 {photo_name} (file not found) - {similarity_percent} match", size=12, color="red"))
            else:
                search_status.value = "❌ No matches found for this selfie."
            
            search_ring.visible = False
            page.update()
        
        def download_photo(photo_path):
            """Download a photo to the user's downloads folder"""
            try:
                import shutil
                from pathlib import Path
                
                # Get user's downloads folder
                downloads_path = str(Path.home() / "Downloads")
                filename = os.path.basename(photo_path)
                destination = os.path.join(downloads_path, filename)
                
                # Copy the file
                shutil.copy2(photo_path, destination)
                
                # Show success message
                search_status.value = f"✅ Downloaded: {filename}"
                page.update()
                
            except Exception as e:
                search_status.value = f"❌ Download failed: {str(e)}"
                page.update()

        def on_selfie_file_selected(e):
            """Handle file selection from HTML file input"""
            try:
                # Get the selected file from the HTML input
                file_input = e.control
                if hasattr(file_input, 'files') and file_input.files:
                    file = file_input.files[0]
                    
                    # Read the file data
                    file_data = file.read()
                    filename = file.name
                    
                    print(f"DEBUG: File selected: {filename}")
                    print(f"DEBUG: File size: {len(file_data)} bytes")
                    
                    # Create unique filename for our storage
                    import uuid
                    unique_filename = f"selfie_{uuid.uuid4().hex}{os.path.splitext(filename)[1]}"
                    
                    # Save to our storage
                    selfie_storage_dir = os.path.join("storage", "temp", "selfies")
                    os.makedirs(selfie_storage_dir, exist_ok=True)
                    
                    selfie_file_path = os.path.join(selfie_storage_dir, unique_filename)
                    with open(selfie_file_path, 'wb') as f:
                        f.write(file_data)
                    
                    # Store the actual file path
                    selfie_path.value = selfie_file_path
                    search_status.value = f"✅ Selfie loaded: {filename} (saved to storage)"
                    
                    print(f"DEBUG: Selfie saved to: {selfie_file_path}")
                    print(f"DEBUG: File data size: {len(file_data)} bytes")
                    
                else:
                    search_status.value = "No file selected"
                    
            except Exception as ex:
                print(f"Error handling file: {ex}")
                search_status.value = f"Error: Could not load file - {str(ex)}"
            
            page.update()

        # Create a simple file input using HTML
        selfie_file_input = ft.HtmlElement(
            tag="input",
            attributes={
                "type": "file",
                "accept": "image/*",
                "style": "width: 300px; padding: 10px; border: 2px dashed #ccc; border-radius: 5px;"
            },
            on_change=on_selfie_file_selected
        )

        # --- Return the full layout ---
        return ft.Column([
            ft.Row([
                ft.Text("Facetak Engine", size=40, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Sign Out", on_click=lambda e: handle_signout(e), style=ft.ButtonStyle(
                    color="white",
                    bgcolor="red600",
                    padding=10
                ))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("✅ Authentication Successful!", size=16, color="green"),
            ft.Divider(),
            
            # Cache statistics section
            ft.Text("📊 Cache Information", size=18, weight=ft.FontWeight.W_600),
            cache_stats_text,
            ft.ElevatedButton("Refresh Cache Stats", on_click=lambda e: update_cache_stats(), style=ft.ButtonStyle(
                color="white",
                bgcolor="blue600",
                padding=5
            )),
            ft.Divider(),
            
            ft.Row([
                ft.Column([
                    ft.Text("Step 1: Process Google Drive Photos", size=20, weight=ft.FontWeight.W_600),
                    drive_url_field,
                    force_reprocess_checkbox,
                    ft.ElevatedButton("Process Google Drive Photos", on_click=process_drive_folder_click, style=ft.ButtonStyle(
                        color="white",
                        bgcolor="blue600",
                        padding=10
                    )),
                    ft.Row([process_ring, process_status])
                ], alignment=ft.MainAxisAlignment.START, expand=True),
                ft.Column([
                    ft.Text("Step 2: Find a Person", size=20, weight=ft.FontWeight.W_600),
                    ft.Text("Select a selfie photo:"),
                    selfie_file_input,
                    ft.Text("Adjust Match Sensitivity:"),
                    threshold_slider,
                    ft.ElevatedButton("Find My Photos", on_click=search_click),
                    ft.Row([search_ring, search_status]),
                ], alignment=ft.MainAxisAlignment.START, expand=True),
            ]),
            ft.Divider(),
            ft.Text("Results", size=20),
            results_grid
        ])

    # --- Google OAuth Authentication Route Change Logic ---
    def route_change(route):
        print(f"🔄 Route change detected: {page.route}")
        page.clean()
        
        # Try to restore session from localStorage first
        restored_user_info = load_session_from_storage(page)
        if restored_user_info:
            page.session.set("user_info", restored_user_info)
            print(f"🔄 Session restored from localStorage: {restored_user_info.get('email')}")
        
        try:
            # Check if this is a Google OAuth callback (URL contains authorization code)
            if "code=" in page.route:
                try:
                    print(f"🔐 Google OAuth callback detected: {page.route}")
                    print(f"🔍 Full route: {page.route}")
                    
                    # Extract the authorization code from the URL
                    code_start = page.route.find("code=") + 5
                    code_end = page.route.find("&", code_start)
                    if code_end == -1:
                        code_end = len(page.route)
                    auth_code = page.route[code_start:code_end]
                    print(f"🔑 Extracted authorization code: {auth_code[:20]}...")

                    # Exchange authorization code for tokens
                    print("🔄 Exchanging authorization code for tokens...")
                    tokens = exchange_code_for_tokens(auth_code)
                    
                    if tokens and 'access_token' in tokens:
                        print(f"✅ Tokens received successfully")
                        
                        # Get user info from Google using access token
                        user_info = get_user_info(tokens['access_token'])
                        
                        if user_info:
                            print(f"✅ User authenticated: {user_info}")
                            
                            # Store tokens and user info in session
                            user_info['access_token'] = tokens['access_token']
                            if 'refresh_token' in tokens:
                                user_info['refresh_token'] = tokens['refresh_token']
                            
                            page.session.set("user_info", user_info)
                            print(f"💾 Session stored: {page.session.get('user_info')}")
                            
                            # Save to localStorage for persistence
                            save_session_to_storage(page, user_info)
                            
                            # Show main app
                            print("🎉 Google OAuth authentication successful! Showing main app...")
                            
                            # Debug session before showing main app
                            print("🔍 Debugging session before showing main app...")
                            debug_session()
                            
                            page.add(create_main_app_view())
                            page.update()
                            
                            # Initialize cache statistics
                            try:
                                from local_cache import get_cache_stats
                                stats = get_cache_stats(user_info.get('email', 'unknown_user'))
                                print(f"📊 Initial cache stats: {stats['photos_count']} photos, {stats['embeddings_count']} embeddings")
                            except Exception as e:
                                print(f"⚠️ Could not load initial cache stats: {e}")
                            
                            return
                        else:
                            print("❌ Failed to get user info from Google")
                    else:
                        print("❌ Failed to exchange authorization code for tokens")

                    # If we get here, authentication failed
                    print("❌ Google OAuth authentication failed")
                    page.add(create_login_view())

                except Exception as e:
                    print(f"❌ Google OAuth callback error: {e}")
                    page.add(create_login_view())
                    
            elif page.route == "/auth/callback":
                # Handle Google OAuth callback (alternative route)
                try:
                    print(f"🔐 Google OAuth callback route: {page.route}")
                    
                    # Extract authorization code from URL parameters
                    if "code=" in page.route:
                        code_start = page.route.find("code=") + 5
                        code_end = page.route.find("&", code_start)
                        if code_end == -1:
                            code_end = len(page.route)
                        auth_code = page.route[code_start:code_end]
                        
                        print(f"🔑 Extracted authorization code: {auth_code[:20]}...")
                        
                        # Exchange authorization code for tokens
                        tokens = exchange_code_for_tokens(auth_code)
                        
                        if tokens and 'access_token' in tokens:
                            # Get user info from Google
                            user_info = get_user_info(tokens['access_token'])
                            
                            if user_info:
                                print(f"✅ User authenticated: {user_info}")
                                
                                # Store tokens and user info in session
                                user_info['access_token'] = tokens['access_token']
                                if 'refresh_token' in tokens:
                                    user_info['refresh_token'] = tokens['refresh_token']
                                
                                page.session.set("user_info", user_info)
                                print(f"💾 Session stored: {page.session.get('user_info')}")
                                
                                # Save to localStorage for persistence
                                main_instance = page.views[0].content if page.views else None
                                if hasattr(main_instance, 'save_session_to_storage'):
                                    main_instance.save_session_to_storage(user_info)
                                
                                # Show main app
                                print("🎉 Google OAuth authentication successful! Showing main app...")
                                page.add(create_main_app_view())
                                page.update()
                                
                                # Initialize cache statistics
                                try:
                                    from local_cache import get_cache_stats
                                    stats = get_cache_stats(user_info.get('email', 'unknown_user'))
                                    print(f"📊 Initial cache stats: {stats['photos_count']} photos, {stats['embeddings_count']} embeddings")
                                except Exception as e:
                                    print(f"⚠️ Could not load initial cache stats: {e}")
                                
                                return
                            else:
                                print("❌ Failed to get user info from Google")
                                page.add(create_login_view())
                                return
                        else:
                            print("❌ Failed to exchange authorization code for tokens")
                            page.add(create_login_view())
                            return
                    else:
                        print("❌ No authorization code found in callback URL")
                        page.add(create_login_view())
                        return
                        
                except Exception as e:
                    print(f"❌ Google OAuth callback error: {e}")
                    page.add(create_login_view())
                    return
                    
            elif "callback" in page.route or "dashboard" in page.route:
                # Handle any callback/dashboard routes that might be old Clerk redirects
                print(f"🔄 Detected potential old redirect: {page.route}")
                print("🔄 Redirecting to login view...")
                page.add(create_login_view())
                
            elif "google" in page.route.lower() or "oauth" in page.route.lower():
                # Handle any Google/OAuth related routes
                print(f"🔍 Google/OAuth route detected: {page.route}")
                if "code=" in page.route:
                    print(f"🔑 Authorization code found in route: {page.route}")
                    # Try to extract and process the code
                    try:
                        code_start = page.route.find("code=") + 5
                        code_end = page.route.find("&", code_start)
                        if code_end == -1:
                            code_end = len(page.route)
                        auth_code = page.route[code_start:code_end]
                        print(f"🔑 Processing authorization code: {auth_code[:20]}...")
                        
                        # Process the authorization code
                        tokens = exchange_code_for_tokens(auth_code)
                        if tokens and 'access_token' in tokens:
                            user_info = get_user_info(tokens['access_token'])
                            if user_info:
                                user_info['access_token'] = tokens['access_token']
                                if 'refresh_token' in tokens:
                                    user_info['refresh_token'] = tokens['refresh_token']
                                
                                page.session.set("user_info", user_info)
                                print(f"🎉 Authentication successful via Google route!")
                                
                                # Save to localStorage for persistence
                                save_session_to_storage(page, user_info)
                                page.add(create_main_app_view())
                                page.update()
                                return
                    except Exception as e:
                        print(f"❌ Error processing Google route: {e}")
                
                # If we get here, show login
                page.add(create_login_view())
                    
            elif page.route == "/logout":
                print("🚪 Logout requested - clearing session")
                # Clear local session first
                page.session.clear()
                
                # Clear localStorage session
                clear_session_storage(page)
                
                # For Google OAuth, we just need to clear local session
                # Google will handle the OAuth state on their side
                print("🔄 Clearing Google OAuth session...")
                
                # Show logout success message
                page.clean()
                page.add(ft.Column([
                    ft.Text("✅ Successfully Signed Out", size=24, weight=ft.FontWeight.BOLD, color="green"),
                    ft.Icon(ft.icons.CHECK_CIRCLE, size=48, color="green"),
                    ft.Text("Your session has been cleared.", size=16, color="grey600"),
                    ft.Text("Google OAuth session cleared.", size=14, color="blue"),
                    ft.ElevatedButton("Sign In Again", on_click=lambda e: show_login_again(), style=ft.ButtonStyle(
                        color="white",
                        bgcolor="red600",
                        padding=15
                    ))
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True))
                page.update()
                
                return
            else:
                print(f"🔍 Checking user session for route: {page.route}")
                # Check if user is already logged in
                print(f"🔍 Session check - Current session: {page.session.get('user_info')}")
                user_info = page.session.get("user_info") or {}
                if page.session.get("user_info"):
                    print(f"✅ User already logged in: {user_info.get('email', 'Unknown')}")
                    page.add(create_main_app_view())
                    
                    # Initialize cache statistics for existing session
                    try:
                        user_info = page.session.get("user_info")
                        if user_info:
                            from local_cache import get_cache_stats
                            stats = get_cache_stats(user_info.get('email', 'unknown_user'))
                            print(f"📊 Initial cache stats: {stats['photos_count']} photos, {stats['embeddings_count']} embeddings")
                    except Exception as e:
                        print(f"⚠️ Could not load initial cache stats: {e}")
                else:
                    print("❌ No user session found, showing login")
                    page.add(create_login_view())
        except Exception as e:
            print(f"Route change error: {e}")
            page.add(ft.Text(f"An error occurred: {e}"))

        page.update()
    
    page.on_route_change = route_change
    page.go(page.route)

# --- Run the Application ---
if __name__ == "__main__":
    ft.app(target=main, port=8550, view=ft.AppView.WEB_BROWSER)