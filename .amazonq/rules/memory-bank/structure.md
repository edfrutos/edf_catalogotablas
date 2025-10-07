# EDF Catálogo de Tablas - Project Structure

## Directory Organization

### Core Application (`/app/`)
- **`routes/`**: Flask route handlers organized by functionality (auth, catalogs, admin, API)
- **`templates/`**: Jinja2 HTML templates with modular component structure
- **`static/`**: Frontend assets (CSS, JavaScript, images) with organized subdirectories
- **`models/`**: Database models and data structures
- **`utils/`**: Utility functions for common operations (file handling, image processing, database operations)

### Configuration & Setup
- **`config/`**: Application configuration files and environment-specific settings
- **`app_data/`**: Runtime data files including fallback configurations and metrics
- **Root config files**: `config.py`, `.env`, `requirements.txt` for application setup

### Development & Tools (`/tools/`)
- **`Scripts Principales/`**: Core maintenance and setup scripts
- **`maintenance/`**: System maintenance and cleanup utilities
- **`diagnostico/`**: Diagnostic and troubleshooting tools
- **`utils/`**: Development utilities and helper scripts
- **`macOS/`**: Platform-specific tools for macOS application building

### Testing & Quality (`/tests/`)
- **Unit tests**: Individual component testing
- **Integration tests**: Full workflow testing
- **Static files**: Test resources and mock data

### Documentation (`/docs/`)
- **`development/`**: Technical documentation and script catalogs
- **`deployment/`**: Deployment guides and CI/CD configuration
- **`security/`**: Security documentation and certificates
- **`user-guide/`**: End-user documentation

### Data & Storage
- **`backups/`**: Automated backup files with compression
- **`flask_session/`**: Session storage for web application
- **`logs/`**: Application and system logs with rotation
- **`exportados/`**: User-generated export files

### Build & Deployment
- **`app/build_constructores/`**: Application builders for different platforms
- **`app/launcher/`**: Application launchers for various deployment modes
- **`.github/workflows/`**: CI/CD pipeline configuration

## Core Components

### Application Factory Pattern
- **`app/factory.py`**: Flask application factory with extension initialization
- **`app/extensions.py`**: Centralized extension management
- **`app/__init__.py`**: Package initialization and configuration

### Database Layer
- **`app/database.py`**: MongoDB connection and database utilities
- **`app/models/`**: Data models with validation and serialization
- **Collection structure**: Users, catalogs, audit logs, reset tokens

### Authentication System
- **`app/routes/auth_routes.py`**: Authentication endpoints
- **`app/auth_utils.py`**: Authentication utilities and decorators
- **`app/routes/auth2fa_routes.py`**: Two-factor authentication implementation

### API Architecture
- **`app/routes/api_routes.py`**: RESTful API endpoints
- **`app/routes/catalogs_routes.py`**: Catalog management API
- **JSON response standardization**: Consistent API response format

## Architectural Patterns

### MVC Architecture
- **Models**: Database models in `/app/models/`
- **Views**: Jinja2 templates in `/app/templates/`
- **Controllers**: Flask routes in `/app/routes/`

### Modular Design
- **Route Blueprints**: Organized by functionality (admin, auth, catalogs, API)
- **Utility Modules**: Reusable components in `/app/utils/`
- **Configuration Management**: Environment-based configuration classes

### Security Architecture
- **Middleware**: Security middleware for request validation
- **Decorators**: Authentication and authorization decorators
- **Audit System**: Comprehensive logging and monitoring

### Storage Architecture
- **Local Storage**: File system for development and fallback
- **Cloud Storage**: AWS S3 integration for production media storage
- **Database**: MongoDB with optimized connection pooling

## Integration Points

### External Services
- **AWS S3**: Media storage and CDN
- **MongoDB Atlas**: Primary database service
- **Email Services**: SMTP integration for notifications
- **Google Drive API**: Backup and synchronization services

### Platform Integration
- **Web Interface**: Standard Flask web application
- **Desktop Application**: PyWebView wrapper for native experience
- **API Access**: RESTful endpoints for external integrations