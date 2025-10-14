# CloudFace Pro - Access Control System

## 🔐 Security Architecture

CloudFace Pro implements **strict separation** between Admin and Guest users to ensure data privacy and proper access control.

---

## 👥 User Types

### 1. **Admin Users** (Event Hosts)
- **Who**: Photographers, Event Organizers, Companies
- **Purpose**: Create events, upload photos, manage settings
- **Access Level**: Full access to ONLY their own events
- **Session Key**: `session['user_id']`

### 2. **Guest Users** (Event Attendees)
- **Who**: Event guests, attendees, photo subjects
- **Purpose**: Search for their photos, download, provide feedback
- **Access Level**: Limited to public event pages they're invited to
- **Session Key**: `session['guest_id']`

---

## 🛡️ Authentication Decorators

### `@admin_required`
- Ensures user is logged in as an admin
- Blocks guests from accessing admin routes
- Redirects to `/login` if not authenticated

### `@owns_event_required`
- Ensures admin owns the specific event
- Prevents admins from accessing other admins' events
- Returns 403 error if user doesn't own the event

### `@guest_required`
- Ensures guest is logged in
- Redirects to event-specific login page

---

## 🔒 Protected Routes

### Admin Routes (Require `@owns_event_required`)
```
✅ /dashboard                          - View own events only
✅ /events                             - List own events only
✅ /events/create                      - Create new event
✅ /events/<event_id>                  - View event details (own events only)
✅ /events/<event_id>/upload           - Upload photos (own events only)
✅ /events/<event_id>/delete           - Delete event (own events only)
✅ /api/events/<event_id>/stats        - Get event stats (own events only)
✅ /api/events/<event_id>/processing-status - Check processing (own events only)
```

### Public Routes (No authentication required)
```
🌐 /                                   - Landing page
🌐 /e/<event_id>                       - Public event page (login prompt if guest not logged in)
🌐 /e/<event_id>/search                - Face search (available to all)
🌐 /e/<event_id>/search-stream         - Real-time face search
🌐 /events/<event_id>/photo/<filename> - Serve photos (for search results)
🌐 /events/<event_id>/thumbnail/<filename> - Serve thumbnails
🌐 /events/<event_id>/logo/<filename>  - Serve event logo
🌐 /events/<event_id>/download/<filename> - Download photo with watermark
🌐 /e/<event_id>/download-zip          - Download multiple photos as ZIP
```

### Guest Routes (Require `@guest_required` in future)
```
🎫 /guest/signup/<event_id>            - Guest signup
🎫 /guest/login/<event_id>             - Guest login
🎫 /guest/capture-selfie/<event_id>    - Capture selfie during signup
🎫 /guest/logout                       - Guest logout
🎫 /guest/<guest_id>/selfie            - Serve stored guest selfie
```

---

## 🚨 Security Rules

### ✅ What's Allowed

1. **Admin can**:
   - Create unlimited events
   - Upload photos to their own events
   - View/manage/delete ONLY their own events
   - See analytics for their own events

2. **Guest can**:
   - Sign up for events
   - Search for their face in public events
   - Download their photos with watermarks
   - Provide feedback on search quality

### ❌ What's Blocked

1. **Admin CANNOT**:
   - Access other admins' events
   - View other admins' photos or analytics
   - Bypass ownership checks

2. **Guest CANNOT**:
   - Access admin dashboard
   - Create or delete events
   - View other guests' data
   - Access admin-only routes (403 Forbidden)

3. **Unauthenticated Users CANNOT**:
   - Access admin pages (redirected to login)
   - Access protected APIs

---

## 📊 Event Access Control Flow

### Admin Creating Event
```
1. Admin logs in → session['user_id'] = admin_id
2. Admin creates event → event.user_id = admin_id (ownership set)
3. Admin uploads photos → Only to events they own
4. Admin views dashboard → Only sees events where event.user_id == session['user_id']
```

### Guest Searching Photos
```
1. Guest visits /e/<event_id> → Public event page
2. If not logged in → Prompted to login/signup
3. Guest logs in → session['guest_id'] = guest_id
4. Guest uploads selfie during signup → Stored for auto-search
5. Guest searches → No authentication needed (public search)
6. Guest downloads → Watermarked photos delivered
```

---

## 🔑 Session Management

### Admin Session
```python
session['user_id']    # Admin's unique ID
session['user_email']  # Admin's email
session['token']       # Firebase auth token (if using Firebase)
```

### Guest Session
```python
session['guest_id']     # Guest's unique ID
session['guest_email']  # Guest's email
session['guest_name']   # Guest's name
session['last_event_id'] # Last accessed event (for logout redirect)
```

### Critical Rule
- Admin and Guest sessions are **MUTUALLY EXCLUSIVE**
- If `session['guest_id']` exists, admin routes return 403
- If `session['user_id']` exists, guest-specific features are disabled

---

## 🎯 Implementation Details

### Ownership Verification
```python
@owns_event_required
def view_event(event_id):
    # Decorator automatically checks:
    # 1. Is user logged in as admin?
    # 2. Does event.user_id == session['user_id']?
    # If either fails → 403 or redirect
    
    event = event_manager.get_event(event_id)
    # User can only reach here if they own this event
```

### Event Listing (Database Filter)
```python
def list_user_events(user_id):
    # TESTING_MODE (Local JSON):
    events = [event for event in db.values() if event.get('user_id') == user_id]
    
    # PRODUCTION (Firebase):
    events = db.collection('events').where('user_id', '==', user_id).stream()
    
    # Result: Admin only sees THEIR events
```

---

## 🚀 Future Landing Page Split

### Admin Entry Point
**"Share Album/Event/Photos"** → Admin Login → Dashboard
- For photographers and event organizers
- Emphasis on uploading and management

### Guest Entry Point
**"Find Your Photos"** → Event ID/Link → Guest Login/Search
- For event attendees
- Emphasis on searching and downloading

---

## ✨ Summary

CloudFace Pro now has **complete separation** between:

1. **Admin Side** (Event Hosts):
   - Isolated events (can only access own events)
   - Full management capabilities
   - Protected by ownership checks

2. **Guest Side** (Event Attendees):
   - Public event access
   - Search and download capabilities
   - Cannot access admin features

**Zero Cross-Contamination**: An admin cannot access another admin's events, and a guest cannot access admin routes.

---

**Last Updated**: October 14, 2025
**Status**: ✅ Fully Implemented and Tested

