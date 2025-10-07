# EDF Catálogo de Tablas - Technology Stack

## Programming Languages
- **Python 3.10**: Primary backend language with modern syntax features
- **JavaScript**: Frontend interactivity and AJAX operations
- **HTML5/CSS3**: Modern web standards with responsive design
- **Shell Script**: Automation and deployment scripts

## Core Framework & Libraries

### Backend Framework
- **Flask 3.0.2**: Lightweight web framework with modular architecture
- **Werkzeug 3.0.1**: WSGI utilities and development server
- **Jinja2 3.1.6**: Template engine for dynamic HTML generation
- **Gunicorn 23.0.0**: Production WSGI server for deployment

### Database & Storage
- **PyMongo 4.10.1**: MongoDB driver with connection pooling
- **MongoDB Atlas**: Cloud database service for production
- **Boto3 1.34.34**: AWS SDK for S3 integration
- **Pandas 2.0.3**: Data manipulation and Excel integration

### Authentication & Security
- **Flask-Login**: Session management and user authentication
- **Python-dotenv 1.0.1**: Environment variable management
- **Werkzeug Security**: Password hashing and security utilities
- **Custom 2FA**: Two-factor authentication implementation

### Development & Testing
- **Pytest 8.3.5**: Testing framework with fixtures and plugins
- **Black 24.8.0**: Code formatting and style enforcement
- **Pydantic 2.11.7**: Data validation and serialization
- **MyPy**: Static type checking (configured)

## Frontend Technologies

### UI Framework
- **Bootstrap 5**: Responsive CSS framework
- **jQuery**: DOM manipulation and AJAX requests
- **Custom CSS**: Application-specific styling and themes

### JavaScript Libraries
- **Modal Management**: Custom modal system for user interactions
- **File Upload**: Drag-and-drop file handling
- **Form Validation**: Client-side validation with server sync

## Cloud Services & Infrastructure

### AWS Services
- **S3**: Object storage for images and media files
- **CloudFront**: CDN for global content delivery (configured)
- **IAM**: Access management and security policies

### Database Services
- **MongoDB Atlas**: Primary database with replica sets
- **Connection Pooling**: Optimized connection management
- **Backup Services**: Automated backup with compression

## Development Tools & Configuration

### Build System
- **PyInstaller**: Native application packaging for macOS
- **PyWebView**: Desktop application wrapper
- **Shell Scripts**: Automated build and deployment processes

### Code Quality
- **Linting**: Flake8, Pylint configuration
- **Formatting**: Black, Prettier for consistent code style
- **Type Checking**: MyPy configuration for static analysis
- **Spell Checking**: CSpell integration for documentation

### Development Environment
- **Virtual Environment**: Python venv for dependency isolation
- **Environment Variables**: .env file configuration
- **Hot Reload**: Development server with auto-restart

## Deployment & Operations

### Production Deployment
- **Gunicorn**: WSGI server with worker processes
- **Nginx**: Reverse proxy and static file serving (configured)
- **SSL/TLS**: HTTPS encryption with Let's Encrypt

### Monitoring & Logging
- **Custom Logging**: Structured logging with rotation
- **Performance Monitoring**: Built-in metrics collection
- **Error Tracking**: Comprehensive error logging and reporting

### Backup & Recovery
- **Automated Backups**: Scheduled database and file backups
- **Compression**: Gzip compression for backup efficiency
- **Restore Scripts**: Automated recovery procedures

## Development Commands

### Setup & Installation
```bash
# Environment setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Edit .env with your configuration
```

### Development Server
```bash
# Web development
python run_server.py

# Native app development
python app/launcher/launcher_native.py

# Multi-process server
python run_server_multi.py
```

### Testing & Quality
```bash
# Run tests
pytest tests/

# Code formatting
black .

# Type checking
mypy app/

# Spell checking
cspell "**/*.py" "**/*.md"
```

### Build & Deployment
```bash
# macOS app build
./app/build_constructores/build_macos_app.sh

# Production deployment
gunicorn --config gunicorn.conf.py wsgi:app

# Backup operations
python tools/maintenance/09_backup_restore_total.py
```

## Version Requirements
- **Python**: 3.10+
- **Node.js**: 16+ (for development tools)
- **MongoDB**: 4.4+
- **macOS**: 10.15+ (for native app)

## Performance Optimizations
- **Connection Pooling**: MongoDB connection optimization
- **Caching**: Static file caching and session optimization
- **Compression**: Response compression for bandwidth efficiency
- **Resource Limits**: Memory and upload size limitations