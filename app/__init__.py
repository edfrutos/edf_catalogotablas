# app/__init__.py
"""
Módulo de inicialización de la aplicación Flask para edf_catalogotablas.
Configura blueprints, variables de entorno, S3, MongoDB y otros componentes.
"""
import importlib.util
import logging
import os
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask, g, jsonify, render_template, request, session  # noqa: F401
from flask_login import LoginManager

# Importar filtros personalizados
from app.filters import init_app as init_filters

# Importar blueprints
from .error_handlers import errors_bp
from .routes.admin_routes import admin_bp, admin_logs_bp
from .routes.auth_routes import auth_bp
from .routes.catalog_images_routes import image_bp
from .routes.catalogs_routes import catalogs_bp  # maintenance_bp se registra a través de register_maintenance_routes
from .routes.dev_template import bp_dev_template
from .routes.emergency_access import emergency_bp
from .routes.images_routes import images_bp  # Blueprint para /imagenes_subidas/<filename>
from .routes.main_routes import main_bp
from .routes.scripts_routes import scripts_bp
from .routes.scripts_tools_routes import scripts_tools_bp
from .routes.usuarios_routes import usuarios_bp


# Agregar excepciones personalizadas
class DatabaseConnectionError(Exception):
    """Se lanza cuando hay problemas de conexión con la base de datos MongoDB."""


# Cargar variables de entorno desde .env (sobrescribir existentes)
_ = load_dotenv(override=True)

# Configurar el cliente de S3 si está habilitado
use_s3 = os.environ.get("USE_S3", "false").lower() == "true"
if use_s3:
    try:
        # Importar boto3 y verificar que esté instalado
        import boto3  # type: ignore # noqa: F401  # Usado condicionalmente cuando S3 está habilitado

        logging.info("AWS S3 está habilitado y boto3 está instalado correctamente")
    except ImportError:
        logging.error(
            "AWS S3 está habilitado pero boto3 no está instalado. Instálelo con 'pip install boto3'"
        )
        # No detener la aplicación, simplemente deshabilitar S3
        os.environ["USE_S3"] = "false"

# Definir instancias de MongoDB para uso posterior
client = None
db = None


def _configure_app_basics(import_name, testing=False):
    """
    Configura la aplicación Flask con la configuración básica.
    
    Args:
        import_name: Nombre del módulo de importación para Flask
        testing: Si es True, activa el modo de pruebas
        
    Returns:
        Flask: Instancia de Flask configurada con la configuración básica
    """
    import os
    from flask import Flask
    
    app = Flask(
        import_name,
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
        static_url_path="/static",
    )

    # Configuración del modo de pruebas si es necesario
    if testing:
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False  # Si usas Flask-WTF

    # Configurar clave secreta para sesiones
    app.secret_key = os.getenv("SECRET_KEY", "edf_secret_key_2025")

    # Cargar configuración unificada desde config.py
    app.config.from_object("config.Config")

    # Configuración adicional para archivos grandes
    app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024  # 300MB
    app.config["MAX_CONTENT_PATH"] = None

    # Asegurar que el directorio de sesiones existe
    session_dir = app.config.get("SESSION_FILE_DIR")
    if session_dir:
        os.makedirs(session_dir, exist_ok=True)
        app.logger.info(f"✅ Directorio de sesiones configurado: {session_dir}")
        
    return app


def _initialize_mongodb_connection(app):
    """
    Inicializa la conexión a MongoDB usando el módulo de base de datos.
    
    Args:
        app: Instancia de Flask para configurar
    """
    global client, db
    
    # Importamos el módulo de base de datos que maneja las conexiones de forma resiliente
    app.logger.info("Inicializando conexión a MongoDB usando el módulo database.py...")
    try:
        from app.database import get_mongo_client, get_mongo_db, initialize_db

        _ = initialize_db(app)
        app.logger.info("✅ Conexión global a MongoDB inicializada (initialize_db)")
        client = get_mongo_client()
        db = get_mongo_db()
        # Elimina asignaciones directas a app.mongo_client, app.db, etc.
    except Exception as e:
        app.logger.error(f"❌ Error inicializando la conexión global a MongoDB: {e}")
        db = None


def _setup_flask_login(app):
    """
    Configura Flask-Login y el manejo de usuarios para la autenticación.
    
    Args:
        app: Instancia de Flask para configurar
    """
    from flask import g
    from flask_login import LoginManager
    from app.database import get_mongo_client, get_mongo_db
    from app.exceptions import DatabaseConnectionError
    from app.models.user import User
    
    # Inicializar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Función para asegurar que las colecciones estén disponibles en g
    def ensure_db():
        client = get_mongo_client()
        db = get_mongo_db()
        g.mongo_client = client
        g.db = db
        if db is not None:
            g.users_collection = db["users"]
            g.resets_collection = db["password_resets"]
            g.spreadsheets_collection = db["spreadsheets"]
        else:
            g.users_collection = None
            g.resets_collection = None
            g.spreadsheets_collection = None

    # Registrar la función para que se use
    _ = app.before_request(ensure_db)

    @login_manager.user_loader
    def load_user(user_id: str):  # type: ignore
        if not user_id or user_id == "":
            return None
        # Usar g para la colección de usuarios
        users_collection = getattr(g, "users_collection", None)
        if not users_collection:
            app.logger.error(
                "[CRÍTICO] users_collection no está inicializada. Verifica la conexión a MongoDB antes de autenticar usuarios."
            )
            raise DatabaseConnectionError(
                "users_collection no está inicializada. No se puede autenticar usuarios sin conexión a la base de datos."
            )
        user_data = users_collection.find_one({"email": user_id})
        if not user_data:
            return None
        return User(user_data)


def _setup_common_components(app):
    """
    Inicializa componentes comunes como filtros, extensiones, logging y seguridad.
    
    Args:
        app: Instancia de Flask para configurar
    """
    # Inicializar filtros personalizados
    from app.filters import init_app as init_filters
    init_filters(app)

    # Inicializar extensiones
    from app.extensions import init_extensions
    init_extensions(app)

    # Configurar logging unificado
    from app.logging_unified import setup_unified_logging
    _ = setup_unified_logging(app)
    
    # Inicializar middleware de seguridad
    from app.security_middleware import security_middleware
    security_middleware.init_app(app)


def _register_main_blueprints(app):
    """
    Registra los blueprints principales de la aplicación.
    
    Args:
        app: Instancia de Flask para configurar
    """
    # Importar blueprints necesarios
    from .routes.main_routes import main_bp
    from .routes.auth_routes import auth_bp
    from .routes.catalogs_routes import catalogs_bp
    from .routes.catalog_images_routes import image_bp
    from .routes.usuarios_routes import usuarios_bp
    from .error_handlers import errors_bp
    from .routes.admin_routes import admin_bp, admin_logs_bp
    from .routes.scripts_routes import scripts_bp
    from .routes.scripts_tools_routes import scripts_tools_bp
    from .routes.dev_template import bp_dev_template
    
    # Definir blueprints principales
    blueprints = [
        (main_bp, ""),
        (auth_bp, ""),
        (catalogs_bp, "/catalogs"),
        (image_bp, "/images"),
        (usuarios_bp, "/usuarios"),
        (errors_bp, ""),
    ]

    # Registrar blueprint de API
    try:
        from app.routes.api_routes import api_bp
        app.register_blueprint(api_bp)
        app.logger.info("Blueprint de API registrado correctamente")
    except Exception as e:
        app.logger.error(f"Error registrando blueprint de API: {str(e)}")

    # Registrar blueprints de administración
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(admin_logs_bp, url_prefix="/admin")
    app.register_blueprint(scripts_bp)
    app.register_blueprint(scripts_tools_bp)  # Usa su url_prefix propio

    # Registrar blueprints principales
    for bp, prefix in blueprints:
        try:
            app.register_blueprint(bp, url_prefix=prefix)
        except Exception as e:
            app.logger.error(f"Error registrando blueprint {bp.name}: {str(e)}")
            
    # Registrar blueprint de plantilla de desarrollo SIEMPRE
    app.register_blueprint(bp_dev_template)

    # Registrar blueprint de testing DESPUÉS de bp_dev_template
    try:
        from app.routes.testing_routes import testing_bp
        app.register_blueprint(testing_bp)
        app.logger.info("Blueprint de testing registrado correctamente")
    except Exception as e:
        app.logger.error(f"Error registrando blueprint de testing: {str(e)}")


def _setup_error_handlers(app):
    """
    Configura los manejadores de errores para API y páginas web.
    
    Args:
        app: Instancia de Flask para configurar
    """
    from flask import jsonify, request, render_template
    
    # Error handlers globales para API (devuelven JSON en endpoints tipo /api/ o si se acepta JSON)
    def api_error_handler(error):
        code = getattr(error, "code", 500)
        message = getattr(error, "description", str(error))
        # Si es petición a API o acepta JSON
        if (
            request.path.startswith("/api/")
            or request.is_json
            or "application/json" in request.headers.get("Accept", "")
        ):
            return jsonify({"status": "error", "message": message}), code
        # Si no, deja que el handler por defecto actúe
        return error

    for err_code in [400, 401, 403, 404, 429, 500]:
        app.register_error_handler(err_code, api_error_handler)
    
    # Handler explícito para 404 que muestra plantilla personalizada
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("error/404.html"), 404

    # Registrar el handler para que se use
    app.register_error_handler(404, page_not_found)


def _register_development_testing_blueprints(app):
    """
    Registra blueprints específicos para desarrollo y testing.
    
    Args:
        app: Instancia de Flask para configurar
    """
    import os
    import importlib.util
    
    # Registrar blueprint de test de sesión SOLO en testing o desarrollo
    if (
        app.config.get("TESTING")
        or app.config.get("ENV") == "development"
        or os.environ.get("FLASK_ENV") in ("development", "testing")
    ):
        try:
            # Intentar importar test_session_routes solo si existe
            spec = importlib.util.find_spec("app.routes.test_session_routes")
            if spec is not None:
                # Solo importar si el módulo existe
                try:
                    from app.routes.test_session_routes import test_session_bp
                    app.register_blueprint(test_session_bp)
                    app.logger.info("Blueprint test_session_bp registrado para tests y desarrollo")
                except ImportError:
                    app.logger.info("test_session_routes encontrado pero no se pudo importar - omitiendo registro")
            else:
                app.logger.info("test_session_routes no encontrado - omitiendo registro")

            # Registrar blueprint para test de modales PDF
            try:
                from app.routes.test_pdf_modal_routes import test_pdf_modal_bp
                app.register_blueprint(test_pdf_modal_bp)
                app.logger.info("Blueprint test_pdf_modal_bp registrado para pruebas de modales PDF")
            except Exception as e:
                app.logger.error(f"Error al registrar blueprint de test de modales PDF: {e}")
            
            # Registrar blueprint para test de modales unificados
            try:
                from app.routes.modal_test_routes import modal_test_bp
                app.register_blueprint(modal_test_bp)
                app.logger.info("Blueprint modal_test_bp registrado para pruebas de modales unificados")
            except Exception as e:
                app.logger.error(f"Error al registrar blueprint de test de modales unificados: {e}")
        except Exception as e:
            app.logger.error(f"No se pudo registrar test_session_bp: {e}")


def _register_additional_blueprints(app):
    """
    Registra blueprints adicionales como mantenimiento, emergencia e imágenes.
    
    Args:
        app: Instancia de Flask para configurar
    """
    from .routes.emergency_access import emergency_bp
    from .routes.images_routes import images_bp
    
    # Registrar blueprints de mantenimiento usando la función especializada
    try:
        from app.routes.maintenance_routes import register_maintenance_routes
        register_maintenance_routes(app)
        app.logger.info("Blueprints de mantenimiento y API registrados correctamente")
    except Exception as e:
        app.logger.error(f"Error registrando blueprints de mantenimiento: {str(e)}")

    # Registrar blueprint de emergencia (emergency_bp) sin prefijo
    try:
        app.register_blueprint(emergency_bp)
        app.logger.info("Blueprint de emergencia (emergency_bp) registrado correctamente.")
    except Exception as e:
        app.logger.error(f"Error registrando blueprint de emergencia: {str(e)}")

    # Registrar blueprints adicionales si existen
    try:
        from app.routes.admin_routes import register_admin_blueprints
        register_admin_blueprints(app)
    except Exception as e:
        app.logger.error(f"Error con blueprints adicionales: {str(e)}")

    # Registrar blueprint de imágenes subidas para /imagenes_subidas/<filename>
    try:
        app.register_blueprint(images_bp)
        app.logger.info(
            "uploaded_images_bp registrado en app (ruta /imagenes_subidas/<filename>)"
        )
    except Exception as e:
        app.logger.error(f"ERROR registrando uploaded_images_bp: {e}")


def _setup_monitoring(app):
    """
    Inicializa el sistema de monitoreo de la aplicación.
    
    Args:
        app: Instancia de Flask para configurar
    """
    global client
    
    # Inicializar sistema de monitoreo
    try:
        from app import monitoring
        # Usar configuración de app en lugar de atributos directos
        app.config["MONITORING_THREAD"] = monitoring.init_app(app, client)
        app.config["MONITORING_ENABLED"] = True
        app.logger.info("Sistema de monitoreo inicializado correctamente")
    except Exception as e:
        # Forzar habilitación del monitoreo incluso si hay errores
        app.config["MONITORING_ENABLED"] = True
        app.logger.warning(f"Error al inicializar el sistema de monitoreo: {str(e)}")
        app.logger.info("Monitoreo habilitado manualmente para permitir funcionalidad básica")


def _setup_debug_features_and_logging(app):
    """
    Configura características de depuración y logging adicional.
    
    Args:
        app: Instancia de Flask para configurar
    """
    import os
    import logging
    from logging.handlers import RotatingFileHandler
    from flask import session
    
    # Ruta de test de sesión
    @app.route("/test_session")
    def test_session():  # type: ignore
        session["test"] = "ok"
        return f"Valor de session['test']: {session.get('test')}"

    # Añadir log para depuración de cookies
    @app.before_request
    def log_cookie():  # type: ignore
        # Función de debugging - se ejecuta automáticamente
        pass

    # Log de la cookie enviada en la respuesta
    @app.after_request
    def log_set_cookie(response):  # type: ignore
        app.logger.info(f"[COOKIES] Set-Cookie enviada: {response.headers.get('Set-Cookie')}")
        return response

    # Loggear la URI de MongoDB
    app.logger.info(f"MONGO_URI usado: {app.config.get('MONGO_URI')}")

    # Crear directorio de logs si no existe - usar LOG_DIR si está configurado
    if os.environ.get("LOG_DIR"):
        logs_dir = os.environ["LOG_DIR"]
    else:
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, "flask_debug.log")

    # Añadir handler para logs en archivo rotativo
    file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)


def create_app(testing=False):
    """
    Crea y configura una instancia de la aplicación Flask con todas las extensiones,
    blueprints, middlewares y configuraciones necesarias para el funcionamiento
    de la aplicación de catálogo de tablas.
    
    Esta función inicializa:
    - Configuración base y entorno
    - Conexión a MongoDB
    - Sistema de autenticación (Flask-Login)
    - Filtros personalizados para templates
    - Extensiones de Flask
    - Logging unificado
    - Middleware de seguridad
    - Todos los blueprints de rutas
    - Sistema de monitoreo
    - Manejadores de errores
    
    Args:
        testing (bool): Si es True, activa el modo de pruebas y desactiva CSRF
    
    Returns:
        Flask: Instancia de Flask app completamente configurada
    """
    import os

    app = _configure_app_basics(__name__, testing)

    # Inicializar conexión a MongoDB usando el módulo de base de datos
    _initialize_mongodb_connection(app)

    # Inicializar Flask-Login y configurar user_loader
    _setup_flask_login(app)

    # Inicializar componentes comunes: filtros, extensiones, logging y seguridad
    _setup_common_components(app)

    # Registrar todos los blueprints de la aplicación
    _register_main_blueprints(app)

    # Configurar manejadores de errores para API y páginas web
    _setup_error_handlers(app)

    # Registrar blueprints de testing y desarrollo si es necesario
    _register_development_testing_blueprints(app)

    # Registrar blueprints de mantenimiento, emergencia y adicionales
    _register_additional_blueprints(app)

    # Inicializar sistema de monitoreo
    _setup_monitoring(app)

    # Configurar rutas de test, logging adicional y loggers
    _setup_debug_features_and_logging(app)
    
    return app
