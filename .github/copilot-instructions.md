# EDF Catálogo de Tablas - AI Coding Agent Guide

## Big Picture Architecture

This is a **Flask-based catalog management system** with dual interfaces:
- **Web application** (primary interface) 
- **PyWebView desktop app** for macOS (wraps the web app)

**Key Components:**
- **Backend:** Flask + MongoDB Atlas + AWS S3 for file storage
- **Frontend:** Bootstrap 5 + custom JavaScript modal system
- **Authentication:** Session-based with role management (admin/user)
- **File handling:** Hybrid local/S3 storage with proxy endpoints

## Critical Development Workflows

### Running the Application
```bash
# Development server (port 5001)
python run_server.py

# Alternative multi-instance server
python run_server_multi.py

# Desktop app (macOS)
python launcher_native_websockets.py
```

### Database & Configuration
- **MongoDB:** Uses `app/models/database.py` for connection management
- **Config:** Environment variables loaded via `load_env.py` and `config.py`
- **S3 Config:** Credentials in environment, proxy at `/admin/s3/` endpoint

### Testing & Quality
```bash
# Run tests
python -m pytest tests/

# Format code
black app/ --line-length 88

# Lint code  
flake8 app/ --config .flake8
```

## Project-Specific Patterns

### Modal System Architecture
The project uses a **unified modal system** (`app/static/js/modal-functions-UNIFIED.js`) that handles:
- **Images:** ID `imagenModalVerTabla` with image element `imagenModalVerTablaSrc`
- **Documents:** ID `documentModal` for PDFs, markdown, text files
- **Multimedia:** ID `multimediaModal` for video/audio files

**Critical Detail:** Template uses Spanish IDs (`imagenModalVerTabla`) but older JS code expected English IDs (`imageModal`). Always verify DOM element IDs match function calls.

### File Storage Patterns
```python
# S3 files: Proxied through /admin/s3/ endpoint
s3_url = "/admin/s3/filename.jpg"

# Local files: Direct static serving
local_url = "/static/uploads/filename.jpg" 

# Detection pattern in JS:
is_s3 = url.includes('/admin/s3/') || url.includes('s3.amazonaws.com')
```

### Template Structure
- **Base:** `app/templates/base.html` (common layout)
- **Table view:** `app/templates/ver_tabla.html` (main catalog interface)
- **Admin:** `app/templates/admin/` (management interface)
- **Authentication:** `app/templates/auth/` (login/register)

### Route Organization
```python
# Main routes: app/routes/main_routes.py
# Admin routes: app/routes/admin_routes.py  
# Auth routes: app/routes/auth_routes.py
# API endpoints: app/routes/api_routes.py
```

## Integration Points

### MongoDB Queries
```python
# Standard pattern in models/database.py
from app.models.database import db, users_collection, catalogs_collection

# Always use try/except for DB operations
try:
    result = users_collection.find_one({"_id": ObjectId(user_id)})
except Exception as e:
    logger.error(f"Database error: {e}")
```

### S3 File Operations
```python
# Proxy endpoint in main routes handles S3 downloads
@main_bp.route('/admin/s3/<path:filename>')
def s3_proxy(filename):
    # Downloads from S3 and returns to client
```

### PyWebView Compatibility
- **JavaScript compatibility layer:** `app/static/js/pywebview_compatibility.js`
- **Detection:** `window.isPyWebView` global variable
- **Fallbacks:** Always provide browser-based alternatives for modal operations

## Common Gotchas

### Modal Element IDs
❌ **Don't assume:** English modal IDs like `imageModal`  
✅ **Always check:** Use Spanish IDs like `imagenModalVerTabla`

### File URL Construction
❌ **Avoid hardcoded URLs:** Don't assume `/static/uploads/`  
✅ **Use detection logic:** Check for S3 indicators and proxy accordingly

### Database ObjectId Handling
```python
# Convert strings to ObjectId for MongoDB queries
from bson import ObjectId
user_id = ObjectId(user_id_string)
```

### Authentication Decorators
```python
# Use existing decorators, don't recreate auth logic
from app.decorators import login_required, admin_required

@admin_required
def admin_only_view():
    pass
```

## Essential Files to Understand

- **`app/static/js/modal-functions-UNIFIED.js`** - Modal system implementation
- **`app/templates/ver_tabla.html`** - Main table view with modal triggers  
- **`app/models/database.py`** - MongoDB connection and query patterns
- **`app/routes/main_routes.py`** - Core application routes including S3 proxy
- **`run_server.py`** - Application entry point and configuration
- **`app/static/js/pywebview_compatibility.js`** - Desktop app compatibility

## Current Known Issues
- Modal functions were targeting incorrect HTML element IDs (recently fixed)
- PyWebView modal compatibility may need fallback handling
- S3 proxy caching could be optimized for large files

Focus on understanding the **modal system**, **file storage patterns**, and **MongoDB integration** as these are the most complex architectural decisions in this codebase.