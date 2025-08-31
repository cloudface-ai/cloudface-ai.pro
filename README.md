# 🔍 CloudFace AI - AI-Powered Photo Search Web Application

A sophisticated web application featuring custom-built AI face recognition technology for intelligent photo organization and search. CloudFace AI processes local photo libraries to extract face embeddings and enables lightning-fast similarity searches across thousands of photos.

## ✨ Features

- **🤖 Custom AI Face Recognition Engine** - Built from scratch using advanced machine learning
- **🌐 Modern Web Interface** - Responsive HTML/CSS/JavaScript frontend
- **🔐 Google OAuth Authentication** - Secure user authentication and session management
- **📸 Intelligent Photo Processing** - Automatic face detection and embedding generation
- **🔍 Advanced Search Algorithms** - Configurable similarity thresholds for precise matching
- **💾 Supabase Backend** - Scalable database storage with real-time capabilities
- **⚡ Local Caching System** - Optimized performance with intelligent data caching
- **📱 Multi-Platform Support** - Works on desktop and mobile devices

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │───▶│  Custom AI       │───▶│  Face Detection │
│   (HTML/CSS/JS) │    │  Engine          │    │   & Embedding   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Google OAuth   │    │  Photo Processing│    │  Supabase DB    │
│  Authentication │    │  & Local Cache   │    │  Storage        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account and credentials
- Google OAuth API credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nerdykeeda/cloudface-ai.com.git
   cd cloudface-ai.com
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp example.env .env
   # Edit .env with your Supabase and Google OAuth credentials
   ```

4. **Set up Supabase database**
   ```sql
   -- Create faces table
   CREATE TABLE IF NOT EXISTS faces (
       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
       user_id TEXT NOT NULL,
       photo_reference TEXT NOT NULL,
       face_embedding JSONB NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   
   -- Create indexes for performance
   CREATE INDEX IF NOT EXISTS idx_faces_user_id ON faces(user_id);
   CREATE INDEX IF NOT EXISTS idx_faces_embedding ON faces USING GIN (face_embedding);
   ```

5. **Run the application**
   ```bash
   # Start the web server
   python web_server.py
   
   # Or run the desktop app
   python main_app.py
   ```

## 🔧 Core Components

### **CloudFace AI Engine** (`facetak_engine.py`)
- Custom face detection and embedding generation
- Built with `face_recognition` library and OpenCV
- Generates unique face fingerprints for similarity matching

### **Search Engine** (`search_engine.py`)
- Intelligent similarity search algorithms
- Configurable threshold-based matching
- Local cache optimization for performance

### **Web Server** (`web_server.py`)
- Flask-based web application
- RESTful API endpoints
- Template rendering and static file serving

### **Authentication Handler** (`auth_handler.py`)
- Google OAuth 2.0 integration
- Secure token management
- User session handling

### **Database Handler** (`database_handler.py`)
- Supabase integration
- Face embedding storage and retrieval
- User data management

## 📁 Project Structure

```
CloudFace AI/
├── web_server.py              # Main web application server
├── main_app.py                # Desktop application (Flet)
├── facetak_engine.py          # Custom AI face recognition engine
├── search_engine.py           # Similarity search algorithms
├── auth_handler.py            # Google OAuth authentication
├── database_handler.py        # Supabase database operations
├── flow_controller.py         # Application flow management
├── local_cache.py             # Local caching system
├── templates/                 # HTML templates
│   ├── index.html            # Main application interface
│   ├── landing.html          # Landing page
│   ├── about.html            # About page
│   ├── contact.html          # Contact page
│   └── blog.html             # Blog page
├── public/                    # Static assets
│   ├── assets/               # CSS, JS, images
│   └── favicon.ico           # Site icon
├── storage/                   # Local storage and cache
└── example.env                # Environment configuration template
```

## 🎯 Use Cases

- **Photographers** - Organize client photos by faces
- **Researchers** - Analyze image datasets for facial patterns
- **Families** - Sort through years of family memories
- **Law Enforcement** - Identify individuals across photo collections
- **Businesses** - Customer recognition and photo management

## 🔒 Privacy & Security

- **Local Processing** - Photos processed locally, not uploaded to cloud
- **Secure Authentication** - Google OAuth 2.0 with proper token handling
- **Data Isolation** - User data separated with Row Level Security
- **Encrypted Storage** - Face embeddings stored securely in Supabase

## 🚀 Performance Features

- **Local Caching** - Intelligent caching system for instant results
- **Background Processing** - Non-blocking photo processing
- **Optimized Algorithms** - Efficient similarity search algorithms
- **Database Indexing** - Fast query performance with proper indexing

## 🛠️ Technology Stack

- **Backend**: Python, Flask, Supabase
- **Frontend**: HTML5, CSS3, JavaScript
- **AI/ML**: face_recognition, OpenCV, NumPy
- **Authentication**: Google OAuth 2.0
- **Database**: Supabase (PostgreSQL)
- **Caching**: Local file-based caching system

## 📱 Running the Application

### Web Application
```bash
python web_server.py
# Access at http://localhost:8550
```

### Desktop Application
```bash
python main_app.py
# Native desktop interface
```

### Development Mode
```bash
# Enable debug mode
export FLASK_ENV=development
python web_server.py
```

## 🧪 Testing

```bash
# Run face recognition tests
python test_caching.py

# Test photo processing
python process_photos.py

# Test search functionality
python search_engine.py
```

## 📊 Configuration

### Environment Variables
```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### Search Thresholds
- **Strict Matching**: 0.4 (very similar faces)
- **Standard Matching**: 0.6 (similar faces)
- **Loose Matching**: 0.8 (somewhat similar faces)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **face_recognition** library for face detection capabilities
- **OpenCV** for image processing
- **Supabase** for backend infrastructure
- **Google OAuth** for secure authentication

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/nerdykeeda/cloudface-ai.com/issues)
- **Documentation**: [Wiki](https://github.com/nerdykeeda/cloudface-ai.com/wiki)
- **Email**: nerdykeeda@gmail.com

---

**CloudFace AI** - Where AI meets photo organization. Find faces, discover memories, and organize your photo collection with the power of custom machine learning.
