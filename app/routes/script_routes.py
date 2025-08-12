#!/usr/bin/env python3
"""
Rutas para gestionar scripts usando el detector de entorno
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required
from app.utils.script_manager import (
    script_manager,
    find_script,
    run_script_by_name,
    get_available_scripts,
    run_maintenance_script,
    run_db_script,
    run_utility_script,
    run_admin_script,
    run_password_script,
    run_image_script,
    run_monitoring_script
)
from app.utils.environment_detector import get_environment, is_development, is_production
import logging

logger = logging.getLogger(__name__)

# Crear blueprint para rutas de scripts
script_bp = Blueprint('scripts', __name__, url_prefix='/admin/scripts')

@script_bp.route('/environment', methods=['GET'])
@login_required
def get_environment_info():
    """Obtiene información del entorno actual"""
    try:
        env_info = script_manager.env_detector.get_environment_info()
        return jsonify({
            'success': True,
            'environment': env_info['environment'],
            'hostname': env_info['hostname'],
            'base_path': env_info['base_path'],
            'script_paths': env_info['script_paths']
        })
    except Exception as e:
        logger.error(f"Error obteniendo información del entorno: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/available', methods=['GET'])
@login_required
def list_available_scripts():
    """Lista todos los scripts disponibles"""
    try:
        available_scripts = get_available_scripts()
        return jsonify({
            'success': True,
            'scripts': available_scripts,
            'total_scripts': sum(len(scripts) for scripts in available_scripts.values())
        })
    except Exception as e:
        logger.error(f"Error listando scripts disponibles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/find/<script_name>', methods=['GET'])
@login_required
def find_script_route(script_name):
    """Busca un script específico"""
    try:
        script_info = find_script(script_name)
        if script_info:
            return jsonify({
                'success': True,
                'script': script_info
            })
        else:
            return jsonify({
                'success': False,
                'error': f"Script '{script_name}' no encontrado"
            }), 404
    except Exception as e:
        logger.error(f"Error buscando script '{script_name}': {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/execute', methods=['POST'])
@login_required
def execute_script():
    """Ejecuta un script específico"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        script_name = data.get('script_name')
        script_type = data.get('script_type')  # Opcional
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        if not script_name:
            return jsonify({
                'success': False,
                'error': 'Nombre del script requerido'
            }), 400
        
        # Si se especifica el tipo, usar la función específica
        if script_type:
            script_functions = {
                'maintenance': run_maintenance_script,
                'db_utils': run_db_script,
                'utils': run_utility_script,
                'admin_utils': run_admin_script,
                'password_utils': run_password_script,
                'image_utils': run_image_script,
                'monitoring': run_monitoring_script
            }
            
            if script_type in script_functions:
                result = script_functions[script_type](script_name, *args, **kwargs)
            else:
                return jsonify({
                    'success': False,
                    'error': f"Tipo de script '{script_type}' no válido"
                }), 400
        else:
            # Búsqueda automática
            result = run_script_by_name(script_name, *args, **kwargs)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error ejecutando script: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/maintenance/<script_name>', methods=['POST'])
@login_required
def execute_maintenance_script(script_name):
    """Ejecuta un script de mantenimiento específico"""
    try:
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        result = run_maintenance_script(script_name, *args, **kwargs)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error ejecutando script de mantenimiento '{script_name}': {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/database/<script_name>', methods=['POST'])
@login_required
def execute_database_script(script_name):
    """Ejecuta un script de base de datos específico"""
    try:
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        result = run_db_script(script_name, *args, **kwargs)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error ejecutando script de base de datos '{script_name}': {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/utility/<script_name>', methods=['POST'])
@login_required
def execute_utility_script(script_name):
    """Ejecuta un script de utilidades específico"""
    try:
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        result = run_utility_script(script_name, *args, **kwargs)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error ejecutando script de utilidades '{script_name}': {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/admin/<script_name>', methods=['POST'])
@login_required
def execute_admin_script(script_name):
    """Ejecuta un script de administración específico"""
    try:
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        result = run_admin_script(script_name, *args, **kwargs)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error ejecutando script de administración '{script_name}': {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/password/<script_name>', methods=['POST'])
@login_required
def execute_password_script(script_name):
    """Ejecuta un script de gestión de contraseñas específico"""
    try:
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        result = run_password_script(script_name, *args, **kwargs)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error ejecutando script de contraseñas '{script_name}': {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/image/<script_name>', methods=['POST'])
@login_required
def execute_image_script(script_name):
    """Ejecuta un script de gestión de imágenes específico"""
    try:
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        result = run_image_script(script_name, *args, **kwargs)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error ejecutando script de imágenes '{script_name}': {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/monitoring/<script_name>', methods=['POST'])
@login_required
def execute_monitoring_script(script_name):
    """Ejecuta un script de monitoreo específico"""
    try:
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        result = run_monitoring_script(script_name, *args, **kwargs)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error ejecutando script de monitoreo '{script_name}': {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@script_bp.route('/status', methods=['GET'])
@login_required
def get_script_status():
    """Obtiene el estado general del sistema de scripts"""
    try:
        available_scripts = get_available_scripts()
        total_scripts = sum(len(scripts) for scripts in available_scripts.values())
        
        return jsonify({
            'success': True,
            'environment': get_environment(),
            'is_development': is_development(),
            'is_production': is_production(),
            'total_scripts': total_scripts,
            'script_types': list(available_scripts.keys()),
            'scripts_by_type': {k: len(v) for k, v in available_scripts.items()}
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de scripts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
