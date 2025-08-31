# 🏗️ Architecture Overview

This document provides a comprehensive overview of **CloudFace AI**'s system architecture, components, and data flow.

## 🎯 System Overview

CloudFace AI is built as a **full-stack web application** with a **modular architecture** that separates concerns and enables scalability. The system combines custom AI face recognition with modern web technologies.

## 🏛️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  Web Interface (HTML/CSS/JS)  │  Desktop App (Flet)           │
│  - Landing Page               │  - Native UI Components      │
│  - Main App                   │  - Local Processing           │
│  - Admin Panel                │  - Offline Capabilities       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Web Server (Flask)           │  Authentication Handler        │
│  - REST API Endpoints         │  - Google OAuth 2.0            │
│  - Template Rendering         │  - Session Management          │
│  - Static File Serving        │  - Token Validation            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Business Logic Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  Flow Controller              │  Search Engine                 │
│  - Process Orchestration      │  - Similarity Algorithms       │
│  - Workflow Management        │  - Threshold Management        │
│  - Error Handling             │  - Result Ranking              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AI/ML Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  CloudFace AI Engine          │  Embedding Engine              │
│  - Face Detection             │  - Vector Operations           │
│  - Feature Extraction         │  - Similarity Calculations     │
│  - Embedding Generation       │  - Distance Metrics            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  Database Handler             │  Local Cache                   │
│  - Supabase Integration       │  - File-based Storage          │
│  - CRUD Operations            │  - Performance Optimization    │
│  - Data Validation            │  - Offline Access              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                            │
├─────────────────────────────────────────────────────────────────┤
│  Supabase (PostgreSQL)        │  Google OAuth                  │
│  - User Management            │  - Authentication              │
│  - Face Embeddings            │  - Authorization               │
│  - Real-time Updates          │  - Profile Information         │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### **1. Web Interface (`templates/`)**
- **Landing Page** (`landing.html`): Marketing and introduction
- **Main App** (`index.html`): Core application interface
- **About Page** (`about.html`): Project information
- **Contact Page** (`contact.html`): Support and feedback
- **Blog Page** (`blog.html`): Updates and articles

**Technologies**: HTML5, CSS3, JavaScript, Responsive Design

### **2. Web Server (`web_server.py`)**
- **Flask Application**: Main web server
- **Route Management**: URL routing and handling
- **Template Engine**: Jinja2 template rendering
- **Static Files**: CSS, JS, and image serving
- **Session Management**: User session handling

**Technologies**: Flask, Jinja2, Werkzeug

### **3. Desktop Application (`main_app.py`)**
- **Flet Framework**: Cross-platform desktop UI
- **Native Components**: Platform-specific UI elements
- **Local Processing**: Offline photo processing
- **System Integration**: File system access

**Technologies**: Flet, Python, Native UI

### **4. CloudFace AI Engine (`facetak_engine.py`)**
- **Face Detection**: Locate faces in images
- **Feature Extraction**: Generate face embeddings
- **Image Processing**: OpenCV integration
- **Error Handling**: Robust error management

**Technologies**: face_recognition, OpenCV, NumPy

### **5. Search Engine (`search_engine.py`)**
- **Similarity Search**: Find similar faces
- **Threshold Management**: Configurable matching
- **Result Ranking**: Sort by similarity score
- **Cache Optimization**: Local performance boost

**Technologies**: NumPy, Custom Algorithms

### **6. Flow Controller (`flow_controller.py`)**
- **Process Orchestration**: Coordinate workflows
- **Error Handling**: Graceful failure management
- **Progress Tracking**: Real-time status updates
- **Resource Management**: Memory and CPU optimization

**Technologies**: Python, Async Processing

### **7. Authentication Handler (`auth_handler.py`)**
- **Google OAuth 2.0**: Secure authentication
- **Token Management**: Access and refresh tokens
- **User Validation**: Identity verification
- **Session Security**: Secure session handling

**Technologies**: Google OAuth, JWT, Sessions

### **8. Database Handler (`database_handler.py`)**
- **Supabase Integration**: Database operations
- **CRUD Operations**: Create, Read, Update, Delete
- **Data Validation**: Input sanitization
- **Connection Management**: Pool management

**Technologies**: Supabase, PostgreSQL, Python

### **9. Local Cache (`local_cache.py`)**
- **File-based Storage**: Local data persistence
- **Performance Optimization**: Fast data access
- **Storage Management**: Disk space optimization
- **Offline Access**: No internet required

**Technologies**: File System, JSON, Pickle

## 🔄 Data Flow

### **Photo Processing Flow**
```
1. User Upload → 2. File Validation → 3. Face Detection → 4. Embedding Generation → 5. Database Storage → 6. Cache Update
```

### **Face Search Flow**
```
1. Selfie Upload → 2. Face Detection → 3. Embedding Generation → 4. Similarity Search → 5. Result Ranking → 6. Display Results
```

### **Authentication Flow**
```
1. Login Request → 2. Google OAuth → 3. Token Exchange → 4. User Validation → 5. Session Creation → 6. Access Granted
```

## 🗄️ Database Schema

### **Faces Table**
```sql
CREATE TABLE faces (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    photo_reference TEXT NOT NULL,
    face_embedding JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Indexes**
- **User Lookup**: `idx_faces_user_id` on `user_id`
- **Similarity Search**: `idx_faces_embedding` on `face_embedding` (GIN)

### **Row Level Security**
- Users can only access their own face data
- JWT-based authentication
- Email-based user identification

## 🔒 Security Architecture

### **Authentication**
- **Google OAuth 2.0**: Industry-standard authentication
- **JWT Tokens**: Secure session management
- **HTTPS Only**: Encrypted data transmission

### **Data Protection**
- **Local Processing**: Photos processed locally
- **Encrypted Storage**: Database encryption
- **Access Control**: Row-level security
- **Input Validation**: SQL injection prevention

### **Privacy Features**
- **User Isolation**: Data separation by user
- **No Cloud Uploads**: Photos stay local
- **Anonymous Embeddings**: Face data anonymized
- **Configurable Retention**: User-controlled data lifecycle

## 📊 Performance Architecture

### **Caching Strategy**
- **Multi-level Caching**: Local + database
- **Smart Invalidation**: Cache coherence
- **Memory Optimization**: Efficient data structures
- **Background Updates**: Non-blocking operations

### **Scalability Features**
- **Horizontal Scaling**: Multiple server instances
- **Load Balancing**: Request distribution
- **Database Optimization**: Indexed queries
- **Async Processing**: Non-blocking operations

## 🔌 API Architecture

### **REST Endpoints**
- **Authentication**: `/auth/login`, `/auth/callback`
- **Photos**: `/photos/upload`, `/photos/process`
- **Search**: `/search/faces`, `/search/similar`
- **User**: `/user/profile`, `/user/settings`

### **Response Format**
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed",
  "timestamp": "2025-01-20T10:30:00Z"
}
```

## 🚀 Deployment Architecture

### **Development Environment**
- **Local Flask Server**: Port 8550
- **Local Database**: Supabase development project
- **Hot Reloading**: Code changes auto-refresh

### **Production Environment**
- **Web Server**: Gunicorn + Flask
- **Reverse Proxy**: Nginx
- **Database**: Supabase production project
- **SSL/TLS**: HTTPS encryption
- **Monitoring**: Health checks and logging

## 🔄 Integration Points

### **External Services**
- **Google OAuth**: User authentication
- **Supabase**: Database and real-time features
- **OpenCV**: Image processing
- **face_recognition**: AI face detection

### **Internal Dependencies**
- **Flask**: Web framework
- **Flet**: Desktop UI framework
- **NumPy**: Mathematical operations
- **Python-dotenv**: Environment management

## 📈 Scalability Considerations

### **Horizontal Scaling**
- **Multiple Web Servers**: Load balancer distribution
- **Database Sharding**: User-based partitioning
- **CDN Integration**: Static asset distribution
- **Microservices**: Component separation

### **Vertical Scaling**
- **Resource Optimization**: Memory and CPU usage
- **Database Tuning**: Query optimization
- **Caching Layers**: Multi-level performance boost
- **Async Processing**: Non-blocking operations

---

**Next Steps**: Explore the [API Reference](API-Reference.md) for detailed endpoint documentation, or check the [Development Setup](Development-Setup.md) for building and extending the system.
