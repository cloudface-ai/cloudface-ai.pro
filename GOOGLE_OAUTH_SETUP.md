# 🔐 Google OAuth Setup Guide for Facetak

## 🎯 Overview
This guide will help you set up Google OAuth 2.0 authentication for your Facetak application. Google OAuth provides secure, reliable authentication with direct integration.

## 📋 Prerequisites
- Google account
- Python 3.7+ with required packages installed
- Facetak project files

## 🚀 Step-by-Step Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `Facetak-AI-Photo-Finder`
4. Click "Create"

### 2. Enable Google+ API
1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google+ API" or "Google Identity"
3. Click on it and click "Enable"

### 3. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. If prompted, configure OAuth consent screen:
   - User Type: External
   - App name: Facetak
   - User support email: Your email
   - Developer contact information: Your email
   - Save and continue through other sections

### 4. Configure OAuth Client
1. Application type: `Web application`
2. Name: `Facetak Web Client`
3. **Authorized redirect URIs:**
   - `http://localhost:8550/auth/callback`
   - `http://localhost:8550/`
4. Click "Create"

### 5. Get Your Credentials
1. Copy the **Client ID** (ends with `.apps.googleusercontent.com`)
2. Copy the **Client Secret**
3. Keep these secure!

### 6. Update Your Environment File
Edit `example.env` and replace the placeholder values:

```env
# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_actual_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8550/auth/callback
```

## 🧪 Testing Your Setup

### Run the Test Suite
```bash
python test_google_oauth.py
```

### Expected Output
```
✅ Environment Variables
✅ Google Packages  
✅ Google OAuth
🎉 All tests passed!
```

## 🚀 Running Your App

### Start the Application
```bash
python main_app.py
```

### Authentication Flow
1. Open http://localhost:8550
2. Click "Sign in with Google"
3. Complete Google OAuth flow
4. You'll be redirected back and logged in!

## 🔧 Troubleshooting

### Common Issues

#### ❌ "GOOGLE_CLIENT_ID not found"
- Check your `example.env` file
- Make sure you replaced the placeholder values
- Verify the file is in the same directory as your Python scripts

#### ❌ "Invalid client ID"
- Verify your Client ID format (should end with `.apps.googleusercontent.com`)
- Check that you copied the entire Client ID
- Ensure you're using the correct project credentials

#### ❌ "Redirect URI mismatch"
- Verify your redirect URI in Google Console matches exactly: `http://localhost:8550/auth/callback`
- Check for typos or extra spaces
- Make sure you're using the correct OAuth client

#### ❌ "OAuth consent screen not configured"
- Complete the OAuth consent screen setup in Google Console
- Add your email as a test user if using External user type

### Debug Mode
Enable detailed logging by checking the console output when running your app. The authentication flow will show detailed steps and any errors.

## 🔒 Security Notes

### Keep Credentials Secure
- Never commit `example.env` to version control
- Use environment variables in production
- Rotate credentials regularly

### OAuth Scopes
The app requests these scopes:
- `userinfo.profile` - Basic profile information
- `userinfo.email` - Email address
- `drive.readonly` - Read-only access to Google Drive (for future features)

## 📚 Additional Resources

### Google OAuth Documentation
- [OAuth 2.0 Overview](https://developers.google.com/identity/protocols/oauth2)
- [OAuth Consent Screen](https://developers.google.com/identity/protocols/oauth2/openid-connect#consent-screen)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)

### Facetak Documentation
- Check the console output for detailed authentication flow
- Use `test_google_oauth.py` to verify your setup
- Review `auth_handler.py` for implementation details

## 🎉 Success!
Once you've completed this setup:
1. ✅ Google OAuth is configured
2. ✅ Authentication flow works
3. ✅ Users can sign in with Google
4. ✅ You can access user profile information
5. ✅ Ready for Google Drive integration

Your Facetak application now has secure, reliable authentication! 🚀
