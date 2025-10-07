# EDF Catálogo de Tablas - Development Guidelines

## Code Quality Standards

### File Headers and Documentation
- **Standard Header Pattern**: All Python files include a standardized header with script description, usage, requirements, environment variables, and author attribution
- **Docstring Format**: Functions use comprehensive docstrings with Args, Returns, and description sections
- **Inline Documentation**: Complex logic sections include detailed comments explaining business logic and technical decisions

### Naming Conventions
- **Variables**: Snake_case for variables and functions (`catalog_id`, `user_data`, `get_mongo_db`)
- **Constants**: UPPER_CASE for configuration constants (`COLLECTION_USERS`, `MONGO_CONFIG`, `ALLOWED_IMAGE_EXTENSIONS`)
- **Classes**: PascalCase for class names (`BaseConfig`, `DevelopmentConfig`, `AppFunctionalityChecker`)
- **Files**: Snake_case for module files (`catalogs_routes.py`, `database.py`, `functionality_check_web_interface.py`)

### Error Handling Patterns
- **Comprehensive Exception Handling**: Multi-level try-catch blocks with specific exception types
- **Logging Integration**: All errors logged with context using `current_app.logger.error()` and `logging.error()`
- **User-Friendly Messages**: Flash messages for user feedback separate from technical logging
- **Graceful Degradation**: Fallback mechanisms when primary systems fail (database fallback, S3 to local storage)

## Architectural Patterns

### Flask Application Structure
- **Blueprint Organization**: Routes organized by functionality (`catalogs_bp`, `auth_routes`, `admin_routes`)
- **Decorator Pattern**: Extensive use of decorators for authentication (`@check_catalog_permission`), caching (`@cached`), and validation
- **Factory Pattern**: Configuration classes with inheritance (`BaseConfig`, `DevelopmentConfig`, `ProductionConfig`)

### Database Access Patterns
- **Connection Management**: Global connection variables with thread-safe access (`_mongo_client`, `_mongo_db`, `_is_connected`)
- **Resilient Operations**: Database operations wrapped in try-catch with fallback data sources
- **Collection Abstraction**: Helper functions for common collections (`get_users_collection()`, `get_catalogs_collection()`)
- **Caching Strategy**: Multi-level caching with TTL and key prefixes (`@cached(ttl=3600, key_prefix="user")`)

### Security Implementation
- **Permission Validation**: Role-based access control with admin/user distinction
- **Session Management**: Comprehensive session validation and user context checking
- **Input Sanitization**: File upload validation, secure filename generation, and extension checking
- **CSRF Protection**: Configurable CSRF protection with selective application

## Frontend Integration Patterns

### JavaScript Organization
- **Namespace Pattern**: Functions organized under global window object for template access
- **Error Handling**: Comprehensive console logging with prefixed messages for debugging
- **Modal Management**: Centralized modal functions with type detection and fallback handling
- **File Type Detection**: Automatic file type detection with appropriate handler selection

### Template Integration
- **Dynamic Content**: Server-side data processing for client-side consumption
- **Image Processing**: Automatic image URL conversion and proxy handling for S3 integration
- **Form Handling**: Multi-field form processing with file upload and URL input support

## Performance Optimization Patterns

### Resource Management
- **Connection Pooling**: Optimized MongoDB connection settings with reduced pool sizes
- **Caching Strategy**: Multi-level caching (memory, database, fallback) with appropriate TTL values
- **Compression**: Response compression with configurable levels and size thresholds
- **Session Optimization**: Filesystem-based sessions with reduced lifetime for resource efficiency

### Database Optimization
- **Projection Usage**: Specific field selection to reduce data transfer (`projection = {"password": 1, "email": 1}`)
- **Query Limits**: Automatic limits on large result sets to prevent memory issues
- **Index-Friendly Queries**: Query patterns optimized for MongoDB indexing
- **Batch Operations**: Bulk updates and inserts where applicable

## Configuration Management

### Environment-Based Configuration
- **Class Hierarchy**: Base configuration with environment-specific overrides
- **Environment Variables**: Extensive use of `os.getenv()` with sensible defaults
- **Feature Flags**: Boolean configuration for optional features (`USE_S3`, `DEBUG`, `TESTING`)
- **Resource Limits**: Configurable limits for uploads, timeouts, and connection pools

### Deployment Considerations
- **Production Hardening**: Security settings automatically adjusted for production environment
- **Resource Constraints**: Optimized settings for memory and CPU usage in production
- **Logging Configuration**: Environment-appropriate logging levels and handlers

## Testing and Quality Assurance

### Mock Handling
- **Test Compatibility**: Code designed to work with both real objects and MagicMock instances
- **Type Checking**: Runtime type validation to handle test vs. production differences
- **Fallback Values**: Default values for test scenarios when mocks don't provide expected data

### Validation Patterns
- **Input Validation**: Multi-step validation for user inputs, file uploads, and database operations
- **Data Integrity**: Consistency checks between different data representations (`rows` vs `data`)
- **Error Recovery**: Automatic correction of data inconsistencies where possible

## File and Media Handling

### Upload Processing
- **Dual Storage**: S3 primary with local fallback for file uploads
- **Security Validation**: File type checking, size limits, and secure filename generation
- **URL Management**: Automatic conversion between S3 URLs and proxy URLs for CORS handling
- **Cleanup Operations**: Proper cleanup of temporary files and failed uploads

### Image Processing
- **Multi-Source Support**: External URLs, S3 storage, and local files
- **Automatic Detection**: Smart detection of image sources in data structures
- **Proxy Integration**: Seamless S3 to proxy URL conversion for frontend consumption

## API Design Patterns

### Response Standardization
- **Consistent Structure**: Standardized JSON responses with status, data, and error fields
- **Error Handling**: Uniform error response format across all endpoints
- **Status Codes**: Appropriate HTTP status codes for different scenarios

### Route Organization
- **RESTful Design**: Resource-based URL structure with appropriate HTTP methods
- **Parameter Validation**: Comprehensive validation of route parameters and query strings
- **Permission Integration**: Consistent permission checking across all protected routes

## Logging and Monitoring

### Structured Logging
- **Contextual Information**: Logs include user context, operation details, and system state
- **Debug Levels**: Appropriate log levels for different types of information
- **Performance Tracking**: Timing information for critical operations
- **Error Correlation**: Consistent error tracking with correlation IDs where applicable

### Monitoring Integration
- **Health Checks**: Built-in health check endpoints for system monitoring
- **Metrics Collection**: Performance metrics collection for optimization
- **Audit Trails**: Comprehensive audit logging for security and compliance