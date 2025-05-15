# app/error_handlers.py
from flask import Blueprint, render_template

errors_bp = Blueprint('errors', __name__)

# -------------------------------------------
# Manejadores de errores personalizados
# -------------------------------------------

@errors_bp.app_errorhandler(404)
def not_found_error(error):
    """Error 404: Página no encontrada"""
    return render_template("not_found.html"), 404

@errors_bp.app_errorhandler(500)
def internal_error(error):
    """Error 500: Error interno del servidor"""
    return render_template("error.html", error=str(error)), 500

@errors_bp.app_errorhandler(503)
def service_unavailable_error(error):
    """Error 503: Servicio no disponible"""
    return render_template("errors/503.html"), 503
