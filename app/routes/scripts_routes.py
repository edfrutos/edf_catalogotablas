#!/usr/bin/env python3
# app/routes/scripts_routes.py

import os
import glob
import subprocess
import json
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, jsonify, request, abort, session, redirect, url_for, flash

# Definir el decorador admin_required localmente para evitar dependencias
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session or session.get("role") != "admin":
            flash("No tiene permisos para acceder a esta página", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

# Definir el directorio raíz
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Definir el directorio de herramientas donde se encuentran las copias de los scripts
TOOLS_DIR = os.path.join(ROOT_DIR, 'tools')

# Crear el blueprint
scripts_bp = Blueprint('scripts', __name__, url_prefix='/tools')

@scripts_bp.route('/content/<path:script_path>')
@admin_required
def view_script_content(script_path):
    """Muestra el contenido de un script"""
    # Obtener la ruta absoluta del script
    abs_script_path = os.path.abspath(script_path)
    
    print(f"Intentando acceder al script: {abs_script_path}")
    
    # Verificar que el script existe
    if not os.path.exists(abs_script_path):
        flash('Script no encontrado: ' + abs_script_path, 'error')
        return redirect(url_for('scripts.tools_dashboard'))
    
    # Verificar que el script está dentro del directorio del proyecto
    if not abs_script_path.startswith(ROOT_DIR):
        flash('Script fuera del directorio del proyecto: ' + abs_script_path, 'error')
        return redirect(url_for('scripts.tools_dashboard'))
    
    try:
        # Leer el contenido del script
        with open(abs_script_path, 'r') as f:
            script_content = f.read()
        
        return render_template('script_content.html', 
                              script_name=os.path.basename(abs_script_path),
                              script_path=abs_script_path,
                              script_content=script_content)
    except Exception as e:
        flash(f'Error al leer el contenido del script: {str(e)}', 'error')
        return redirect(url_for('scripts.tools_dashboard'))

@scripts_bp.route('/')
@admin_required
def tools_dashboard():
    """Ruta para acceder al gestor de scripts del sistema"""
    # Definir el directorio de scripts principal (ahora usando el directorio de herramientas)
    tools_dir = TOOLS_DIR
    
    # Definir las categorías de scripts y sus subdirectorios
    script_categories = {
        'maintenance': {
            'name': 'Mantenimiento',
            'description': 'Scripts para iniciar, supervisar y mantener la aplicación',
            'path': os.path.join(tools_dir, 'maintenance'),
            'color': 'primary'
        },
        'admin_utils': {
            'name': 'Utilidades de Admin',
            'description': 'Scripts para administración del sistema',
            'path': os.path.join(tools_dir, 'admin_utils'),
            'color': 'danger'
        },
        'app_runners': {
            'name': 'Ejecutores de App',
            'description': 'Scripts para ejecutar diferentes versiones de la aplicación',
            'path': os.path.join(tools_dir, 'app_runners'),
            'color': 'success'
        },
        'aws_utils': {
            'name': 'Utilidades AWS',
            'description': 'Scripts para interactuar con servicios de AWS',
            'path': os.path.join(tools_dir, 'aws_utils'),
            'color': 'warning'
        },
        'catalog_utils': {
            'name': 'Utilidades de Catálogo',
            'description': 'Scripts para gestionar catálogos',
            'path': os.path.join(tools_dir, 'catalog_utils'),
            'color': 'info'
        },
        'db_utils': {
            'name': 'Utilidades de BD',
            'description': 'Scripts para gestionar la base de datos',
            'path': os.path.join(tools_dir, 'db_utils'),
            'color': 'secondary'
        },
        'image_utils': {
            'name': 'Utilidades de Imágenes',
            'description': 'Scripts para procesar imágenes',
            'path': os.path.join(tools_dir, 'image_utils'),
            'color': 'dark'
        },
        'monitoring': {
            'name': 'Monitoreo',
            'description': 'Scripts para monitorear el sistema',
            'path': os.path.join(tools_dir, 'monitoring'),
            'color': 'light'
        },
        'password_utils': {
            'name': 'Utilidades de Contraseñas',
            'description': 'Scripts para gestionar contraseñas',
            'path': os.path.join(tools_dir, 'password_utils'),
            'color': 'danger'
        },
        'session_utils': {
            'name': 'Utilidades de Sesión',
            'description': 'Scripts para gestionar sesiones',
            'path': os.path.join(tools_dir, 'session_utils'),
            'color': 'warning'
        },
        'root': {
            'name': 'Scripts Raíz',
            'description': 'Scripts en el directorio raíz',
            'path': os.path.join(tools_dir, 'root'),
            'color': 'secondary'
        }
    }
    
    # Recopilar todos los scripts
    scripts = []
    
    # Procesar cada categoría
    for category_id, category_info in script_categories.items():
        path = category_info['path']
        print(f"Buscando scripts en: {path}")
        
        if os.path.exists(path):
            # Buscar scripts .sh y .py
            scripts_sh = glob.glob(os.path.join(path, '*.sh'))
            scripts_py = glob.glob(os.path.join(path, '*.py'))
            category_scripts = scripts_sh + scripts_py
            
            # Si es la categoría 'root', excluir scripts que están en subdirectorios
            if category_id == 'root':
                category_scripts = [s for s in category_scripts if os.path.dirname(s) == path]
            
            print(f"Scripts encontrados en {category_id}: {len(category_scripts)}")
            
            for script_path in category_scripts:
                # Obtener una descripción personalizada basada en el nombre del script
                script_name = os.path.basename(script_path)
                script_ext = os.path.splitext(script_name)[1]
                
                # Determinar el tipo de script y su descripción
                if script_ext == '.sh':
                    description = f"Script de shell para {category_info['name']}"
                else:  # .py
                    description = f"Script de Python para {category_info['name']}"
                
                # Añadir el script a la lista
                print(f"Añadiendo script: {script_path}")
                scripts.append({
                    'name': script_name,
                    'path': script_path,
                    'category': category_id,
                    'description': description
                })
        else:
            print(f"Directorio no encontrado: {path}")
    
    print(f"Total de scripts encontrados: {len(scripts)}")
    if len(scripts) == 0:
        print("ADVERTENCIA: No se encontraron scripts para mostrar")
    
    return render_template('tools_dashboard.html', scripts=scripts, categories=script_categories)

@scripts_bp.route('/run/<path:script_path>', methods=['POST'])
@admin_required
def run_script(script_path):
    """Ejecuta un script y devuelve su salida"""
    # Obtener la ruta absoluta del script
    abs_script_path = os.path.abspath(script_path)
    
    print(f"Intentando ejecutar el script: {abs_script_path}")
    
    # Verificar que el script existe
    if not os.path.exists(abs_script_path):
        return jsonify({
            'error': 'Script no encontrado: ' + abs_script_path,
            'script': os.path.basename(script_path)
        }), 404
    
    # Verificar que el script está dentro del directorio del proyecto
    if not abs_script_path.startswith(ROOT_DIR):
        return jsonify({
            'error': 'Script fuera del directorio del proyecto: ' + abs_script_path,
            'script': os.path.basename(script_path)
        }), 404
    
    # Verificar que el script tiene permisos de ejecución
    if not os.access(abs_script_path, os.X_OK):
        try:
            # Intentar dar permisos de ejecución con sudo
            sudo_cmd = ['sudo', 'chmod', '+x', abs_script_path]
            subprocess.run(sudo_cmd, check=True)
        except Exception as e:
            return jsonify({
                'error': f'No se pudieron establecer permisos de ejecución: {str(e)}',
                'script': os.path.basename(script_path)
            }), 403
    
    try:
        # Ejecutar el script con sudo para evitar problemas de permisos
        process = subprocess.Popen(
            ['sudo', abs_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(abs_script_path),
            text=True
        )
        stdout, stderr = process.communicate(timeout=30)  # Timeout de 30 segundos
        
        result = {
            'script': os.path.basename(script_path),
            'exit_code': process.returncode,
            'output': stdout,
            'error': stderr,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(result)
    except subprocess.TimeoutExpired:
        return jsonify({
            'script': os.path.basename(script_path),
            'error': 'El script tardó demasiado tiempo en ejecutarse (más de 30 segundos)',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 408
    except Exception as e:
        return jsonify({
            'script': os.path.basename(script_path),
            'error': f'Error al ejecutar el script: {str(e)}',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500
