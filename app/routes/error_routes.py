# app/routes/error_routes.py

from flask import Blueprint, render_template, current_app
import logging

logger = logging.getLogger(__name__)
errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def page_not_found(e):
    logger.warning(f"Error 404: Página no encontrada - {e}")
    return render_template('error/404.html'), 404

@errors_bp.app_errorhandler(500)
def server_error(e):
    logger.error(f"Error 500: Error interno del servidor - {e}")
    return render_template('error/500.html'), 500

@errors_bp.app_errorhandler(403)
def forbidden(e):
    logger.warning(f"Error 403: Acceso prohibido - {e}")
    return render_template('error/403.html'), 403

@errors_bp.app_errorhandler(401)
def unauthorized(e):
    logger.warning(f"Error 401: No autorizado - {e}")
    return render_template('error/401.html'), 401