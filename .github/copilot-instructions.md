# EDF Catálogo de Tablas - AI Coding Agent Instructions

This is a hybrid Flask web application + macOS native app for managing table catalogs with multimedia support, user authentication, and administrative tools.

## Architecture Overview

### Core Application Structure
- **Flask App**: Main web application in `app/` with factory pattern (`app/factory.py`)
- **MongoDB**: Primary database using PyMongo with collections for users, catalogs, audit logs
- **Blueprint-based Routes**: Modular routing in `app/routes/` - main routes handle table operations, catalog routes handle CRUD operations
- **Template-based Frontend**: Jinja2 templates in `app/templates/` with Bootstrap styling
- **S3 Integration**: AWS S3 for file storage with local fallback in `app/static/uploads/`

### Key Components
- **Catalogs System**: Core functionality for managing tabular data with headers and rows
- **Multimedia Handling**: Support for images, videos, audio, documents with URL/file upload dual approach
- **User Management**: Authentication with Flask-Login, role-based access control
- **Admin Interface**: Comprehensive admin tools in `app/routes/admin/`

## Essential Development Patterns

### Catalog Data Structure
```python
# Catalogs stored in MongoDB with this schema:
{
    "_id": ObjectId,
    "name": "Catalog Name",
    "headers": ["Column1", "Column2", "Multimedia"],
    "data": [  # Actual rows data
        {"Column1": "value", "Multimedia": "url_or_filename"},
    ],
    "rows": [],  # Legacy field, use 'data' instead
    "owner_email": "user@example.com"
}
```

### Multimedia Field Handling
- **URLs**: External links stored directly as strings
- **Files**: Uploaded files stored as filenames, served via `/static/uploads/`
- **S3 Files**: Full S3 URLs or proxied via `/admin/s3/` routes
- **Template Logic**: Check `multimedia_data.startswith('http')` to distinguish URLs from files

### Route Organization
- **Main Routes** (`app/routes/main_routes.py`): Legacy table operations, editing rows
- **Catalog Routes** (`app/routes/catalogs_routes.py`): Modern CRUD operations for catalogs
- **Admin Routes** (`app/routes/admin/`): Administrative functions, user management
- **API Routes** (`app/routes/api_routes.py`): RESTful endpoints for frontend interactions

## Critical Developer Workflows

### Running the Application
```bash
# Web development server
python run_server.py

# Production WSGI
gunicorn --bind 0.0.0.0:5001 wsgi:app

# Native app launcher
python launcher_native_websockets.py
```

### Database Connection Pattern
```python
# Always use Flask's g object for database access
from flask import g

# Collections are initialized in factory.py before_request
users_collection = g.users_collection
spreadsheets_collection = g.spreadsheets_collection
```

### File Upload Handling
- **Security**: Always use `secure_filename()` from Werkzeug
- **Storage**: Files saved to `app/static/uploads/` or S3 based on configuration
- **Validation**: Check file extensions and size limits (300MB max)
- **URL Generation**: Use `url_for('static', filename='uploads/' + filename)` for local files

### Template Rendering Best Practices
- **Multimedia Display**: Use the pattern in `app/templates/catalogos/view.html` for consistent multimedia rendering
- **Form Handling**: Dual input pattern for URL/file uploads in edit forms
- **Error Handling**: Always include flash message display in templates

## Integration Points

### MongoDB Collections
- `users_unified`: User authentication and profiles
- `spreadsheets`: Catalog data (legacy naming, actually contains catalogs)
- `audit_logs`: Activity tracking
- `password_resets`: Password reset tokens

### External Services
- **AWS S3**: File storage with bucket `edf-catalogo-tablas`
- **Email**: SMTP integration for notifications and password resets
- **Google Drive**: Legacy integration for some data sources

### JavaScript Components
- **Modal System**: Unified modal functions in `app/static/js/modal-functions-UNIFIED.js`
- **Image Handling**: Advanced image viewing and download capabilities
- **Table Operations**: Interactive table editing and real-time updates

## Project-Specific Conventions

### Error Handling
```python
# Always log errors and provide user-friendly messages
current_app.logger.error(f"Error description: {error}")
flash("User-friendly error message", "error")
```

### Authentication Decorators
- Use `@login_required` for protected routes
- Use `@check_catalog_permission` for catalog-specific access control
- Session management with Flask-Login and custom User model

### Logging Pattern
- Structured logging with context: `[COMPONENT] Description`
- Debug logging for development: `[DEBUG_COMPONENT] Details`
- Error categorization: Database, File, Auth, etc.

### Form Processing
- Always validate and sanitize inputs
- Handle both form data and file uploads in single endpoints
- Use consistent field naming: `{header}_url` for URLs, `{header}_file` for uploads

### Template Inheritance
- Base templates: `base.html`, `admin/base.html`
- Consistent block structure: `title`, `content`, `scripts`
- Bootstrap 5 integration throughout

## Testing and Build

### Test Structure
- Unit tests in `tests/` directory
- Use pytest for test execution
- Mock MongoDB connections for unit tests
- Integration tests for critical user flows

### Build Process
- PyInstaller for native macOS app: `EDF_CatalogoDeTablas_Native_WebSockets.spec`
- Docker support with Dockerfile
- GitHub Actions for automated builds and deployment

This codebase prioritizes maintainability through modular design, comprehensive error handling, and consistent patterns for database operations, file handling, and user interface interactions.