#!/usr/bin/env python3
"""
Ruta unificada para ejecución de scripts
"""

import os
import subprocess
import json
from flask import Blueprint, jsonify, request, current_app
from app.decorators import admin_required

# Crear blueprint unificado
unified_scripts_bp = Blueprint("unified_scripts", __name__, url_prefix="/admin/tools")

@unified_scripts_bp.route("/execute", methods=["POST"])
@admin_required
def execute_script():
    """Ejecuta un script usando script_runner.py"""
    try:
        # Obtener datos del request
        if request.is_json:
            data = request.get_json()
            script_path = data.get("script") or data.get("script_path") or ""
        else:
            script_path = request.form.get("script") or request.form.get("script_path") or ""
        
        if not script_path:
            return jsonify({
                "error": "Ruta del script no proporcionada",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }), 400
        
        # Validar ruta
        if ".." in script_path or script_path.startswith("/"):
            return jsonify({
                "error": "Ruta no permitida",
                "script": script_path,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }), 400
        
        # Construir ruta absoluta
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_abs_path = os.path.join(project_root, script_path)
        
        if not os.path.exists(script_abs_path):
            return jsonify({
                "error": f"Script no encontrado: {script_path}",
                "script": script_path,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }), 404
        
        # Ejecutar usando script_runner
        script_runner_path = os.path.join(project_root, "tools", "script_runner.py")
        
        if not os.path.exists(script_runner_path):
            return jsonify({
                "error": "script_runner.py no encontrado",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }), 500
        
        # Ejecutar el script
        result = subprocess.run([
            sys.executable,
            script_runner_path,
            script_path
        ], capture_output=True, text=True, timeout=60, cwd=project_root)
        
        # Parsear la salida JSON del script_runner
        try:
            json_output = json.loads(result.stdout)
            return jsonify(json_output)
        except json.JSONDecodeError:
            # Si no es JSON válido, devolver error
            return jsonify({
                "error": "Error en la ejecución del script",
                "script": script_path,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            "error": "Timeout en la ejecución del script",
            "script": script_path,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 408
    except Exception as e:
        return jsonify({
            "error": f"Error interno: {str(e)}",
            "script": script_path,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 500

@unified_scripts_bp.route("/", methods=["GET"])
@admin_required
def tools_dashboard():
    """Página principal de herramientas"""
    return current_app.send_static_file("admin/tools_dashboard.html")
