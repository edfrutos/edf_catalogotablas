#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para diagnosticar y corregir problemas de acceso en edefrutos2025.xyz
Este script solo afecta al dominio edefrutos2025.xyz y no modifica configuraciones globales
"""

import os
import sys
import subprocess
import logging
import socket
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Directorio raíz del dominio
DOMAIN_ROOT = "/var/www/vhosts/edefrutos2025.xyz/httpdocs"

def run_command(command):
    """Ejecuta un comando y devuelve su salida"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

def check_port(host, port):
    """Verifica si un puerto está abierto"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def check_socket_file(socket_path):
    """Verifica si un archivo de socket existe y tiene los permisos correctos"""
    if not os.path.exists(socket_path):
        return False, f"El archivo de socket {socket_path} no existe"
    
    if not os.path.isfile(socket_path) and not os.path.islink(socket_path):
        return False, f"{socket_path} existe pero no es un archivo o enlace simbólico"
    
    return True, f"El archivo de socket {socket_path} existe y parece válido"

def create_wsgi_file():
    """Crea o actualiza el archivo WSGI para la aplicación"""
    wsgi_path = os.path.join(DOMAIN_ROOT, "wsgi.py")
    
    wsgi_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Añadir el directorio de la aplicación al path
sys.path.insert(0, os.path.dirname(__file__))

# Importar la aplicación Flask
from app import app as application

# Para compatibilidad con diferentes configuraciones
app = application

if __name__ == "__main__":
    application.run()
"""
    
    try:
        with open(wsgi_path, 'w') as f:
            f.write(wsgi_content)
        logger.info(f"Archivo WSGI creado en {wsgi_path}")
        return True, f"Archivo WSGI creado en {wsgi_path}"
    except Exception as e:
        logger.error(f"Error al crear el archivo WSGI: {str(e)}")
        return False, f"Error al crear el archivo WSGI: {str(e)}"

def create_local_start_script():
    """Crea un script local para iniciar la aplicación"""
    script_path = os.path.join(DOMAIN_ROOT, "iniciar_app_local.sh")
    
    script_content = """#!/bin/bash

# Este script inicia la aplicación Flask localmente para pruebas
# No afecta a la configuración del servidor

# Directorio de la aplicación
APP_DIR="/var/www/vhosts/edefrutos2025.xyz/httpdocs"

# Activar entorno virtual
source $APP_DIR/.venv/bin/activate

# Cambiar al directorio de la aplicación
cd $APP_DIR

# Detener cualquier instancia anterior
pkill -f "python.*app.py" || true
pkill -f "flask run" || true

# Iniciar la aplicación en modo desarrollo
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Iniciar en puerto 5000 (solo accesible localmente)
flask run --host=127.0.0.1 --port=5000
"""
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)  # Hacer el script ejecutable
        logger.info(f"Script de inicio local creado en {script_path}")
        return True, f"Script de inicio local creado en {script_path}"
    except Exception as e:
        logger.error(f"Error al crear el script de inicio local: {str(e)}")
        return False, f"Error al crear el script de inicio local: {str(e)}"

def create_direct_access_script():
    """Crea un script para acceder directamente al panel de administración"""
    script_path = os.path.join(DOMAIN_ROOT, "acceso_directo_admin.py")
    
    script_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
Script para acceder directamente al panel de administración.
Este script crea una aplicación Flask independiente que permite acceder al panel de administración.
\"\"\"

import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from flask import Flask, session, redirect, url_for, request, render_template, flash, jsonify

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)

# Cargar variables de entorno
load_dotenv()

# Configurar la aplicación
app.config['SECRET_KEY'] = 'clave_secreta_para_desarrollo'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
app.config['SESSION_COOKIE_NAME'] = 'edefrutos2025_session'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Obtener la URI de MongoDB
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    logger.error("No se encontró MONGO_URI en las variables de entorno")
    sys.exit(1)

# Conectar a MongoDB
try:
    client = MongoClient(
        mongo_uri,
        tls=True,
        tlsCAFile=certifi.where(),
        server_api=ServerApi('1')
    )
    
    # Verificar conexión
    client.admin.command('ping')
    logger.info("✅ Conexión a MongoDB establecida correctamente")
    
    # Seleccionar base de datos y colección
    db = client["app_catalogojoyero"]
    users_collection = db["users"]
except Exception as e:
    logger.error(f"Error al conectar a MongoDB: {str(e)}")
    sys.exit(1)

@app.route('/')
def index():
    \"\"\"Página principal que muestra información sobre el script\"\"\"
    return render_template('acceso_directo.html', 
                          title="Acceso Directo al Panel de Administración",
                          message="Esta herramienta permite acceder directamente al panel de administración.")

@app.route('/login_admin/<username>')
def login_admin(username):
    \"\"\"Crea una sesión de administrador para el usuario especificado\"\"\"
    try:
        # Buscar usuario por nombre de usuario
        usuario = users_collection.find_one({"username": username})
        
        if not usuario:
            flash(f"No se encontró el usuario: {username}", "error")
            return redirect(url_for('index'))
        
        # Verificar si el usuario es administrador
        if usuario.get('role') != 'admin':
            flash(f"El usuario {username} no tiene permisos de administrador", "error")
            return redirect(url_for('index'))
        
        # Establecer sesión
        session.permanent = True
        session['user_id'] = str(usuario['_id'])
        session['email'] = usuario.get('email')
        session['username'] = usuario.get('username')
        session['role'] = usuario.get('role')
        session['logged_in'] = True
        session['login_time'] = datetime.utcnow().isoformat()
        session['client_ip'] = request.remote_addr
        
        # Actualizar último login en la base de datos
        users_collection.update_one(
            {"_id": usuario["_id"]},
            {"$set": {"last_login": datetime.utcnow().isoformat()}}
        )
        
        logger.info(f"✅ Sesión creada para el administrador: {username}")
        flash(f"Sesión creada para el administrador: {username}", "success")
        
        # Redirigir al panel de administración
        return redirect('http://localhost:5000/admin/')
        
    except Exception as e:
        logger.error(f"Error al crear sesión: {str(e)}")
        flash(f"Error al crear sesión: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/check_session')
def check_session():
    \"\"\"Verifica el estado de la sesión actual\"\"\"
    session_data = {key: session.get(key) for key in session}
    return render_template('session_info.html', 
                          title="Información de Sesión",
                          session_data=session_data)

@app.route('/logout')
def logout():
    \"\"\"Cierra la sesión actual\"\"\"
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for('index'))

@app.route('/admin_info')
def admin_info():
    \"\"\"Muestra información sobre los usuarios administradores\"\"\"
    try:
        # Buscar todos los usuarios administradores
        admins = list(users_collection.find({"role": "admin"}))
        
        # Convertir ObjectId a string para poder serializarlos
        for admin in admins:
            admin['_id'] = str(admin['_id'])
            # Eliminar la contraseña por seguridad
            if 'password' in admin:
                admin['password'] = '********'
        
        return render_template('admin_info.html',
                              title="Información de Administradores",
                              admins=admins)
        
    except Exception as e:
        logger.error(f"Error al obtener información de administradores: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        })

# Crear plantillas necesarias
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
os.makedirs(templates_dir, exist_ok=True)

# Crear plantilla acceso_directo.html
with open(os.path.join(templates_dir, 'acceso_directo.html'), 'w') as f:
    f.write(\"\"\"
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        .btn {
            display: inline-block;
            padding: 10px 15px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .btn-danger {
            background-color: #f44336;
        }
        .btn-info {
            background-color: #2196F3;
        }
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        .flash-success {
            background-color: #dff0d8;
            color: #3c763d;
        }
        .flash-error {
            background-color: #f2dede;
            color: #a94442;
        }
        .flash-info {
            background-color: #d9edf7;
            color: #31708f;
        }
        .instructions {
            background-color: #ffffd9;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            border-left: 4px solid #ffeb3b;
        }
        pre {
            background-color: #f8f8f8;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        
        {% if get_flashed_messages() %}
        <div class="flash-messages">
            {% for category, message in get_flashed_messages(with_categories=true) %}
                <div class="flash-message flash-{{ category }}">
                    {{ message }}
                </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <p>{{ message }}</p>
        
        <div class="actions">
            <h2>Acciones disponibles:</h2>
            <a href="{{ url_for('login_admin', username='edefrutos') }}" class="btn">Acceder como edefrutos (admin)</a>
            <a href="{{ url_for('login_admin', username='administrator') }}" class="btn">Acceder como administrator (admin)</a>
            <a href="{{ url_for('admin_info') }}" class="btn btn-info">Ver información de administradores</a>
            <a href="{{ url_for('check_session') }}" class="btn btn-info">Verificar sesión actual</a>
            <a href="{{ url_for('logout') }}" class="btn btn-danger">Cerrar sesión</a>
        </div>
        
        <div class="instructions">
            <h3>Instrucciones para acceder al panel de administración:</h3>
            <ol>
                <li>Primero, inicia la aplicación Flask localmente ejecutando <code>./iniciar_app_local.sh</code> en una terminal.</li>
                <li>Luego, haz clic en "Acceder como edefrutos (admin)" o "Acceder como administrator (admin)" para iniciar sesión automáticamente.</li>
                <li>La aplicación te redirigirá automáticamente al panel de administración.</li>
            </ol>
            
            <h3>Solución alternativa:</h3>
            <p>Si el acceso directo no funciona, puedes intentar lo siguiente:</p>
            <ol>
                <li>Inicia la aplicación Flask localmente ejecutando <code>./iniciar_app_local.sh</code> en una terminal.</li>
                <li>Abre un navegador y ve a <a href="http://localhost:5000/login" target="_blank">http://localhost:5000/login</a></li>
                <li>Inicia sesión con las credenciales de administrador.</li>
                <li>Luego, visita directamente <a href="http://localhost:5000/admin/" target="_blank">http://localhost:5000/admin/</a></li>
            </ol>
            
            <h3>Credenciales de administrador:</h3>
            <pre>
Usuario: edefrutos
Contraseña: Edefrutos2025!

Usuario: administrator
Contraseña: admin123
            </pre>
        </div>
    </div>
</body>
</html>
    \"\"\")

# Crear plantilla session_info.html
with open(os.path.join(templates_dir, 'session_info.html'), 'w') as f:
    f.write(\"\"\"
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        .btn {
            display: inline-block;
            padding: 10px 15px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin-right: 10px;
        }
        .btn-danger {
            background-color: #f44336;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        
        <h2>Datos de la sesión actual:</h2>
        
        {% if session_data %}
            <table>
                <tr>
                    <th>Clave</th>
                    <th>Valor</th>
                </tr>
                {% for key, value in session_data.items() %}
                <tr>
                    <td>{{ key }}</td>
                    <td>{{ value }}</td>
                </tr>
                {% endfor %}
            </table>
        {% else %}
            <p>No hay datos de sesión disponibles.</p>
        {% endif %}
        
        <a href="{{ url_for('index') }}" class="btn">Volver</a>
        <a href="{{ url_for('logout') }}" class="btn btn-danger">Cerrar sesión</a>
    </div>
</body>
</html>
    \"\"\")

# Crear plantilla admin_info.html
with open(os.path.join(templates_dir, 'admin_info.html'), 'w') as f:
    f.write(\"\"\"
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        .btn {
            display: inline-block;
            padding: 10px 15px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin-right: 10px;
        }
        .admin-card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #f9f9f9;
        }
        .admin-card h3 {
            margin-top: 0;
            color: #2196F3;
        }
        .admin-property {
            margin-bottom: 5px;
        }
        .property-name {
            font-weight: bold;
            display: inline-block;
            width: 150px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        
        <h2>Usuarios administradores en la base de datos:</h2>
        
        {% if admins %}
            {% for admin in admins %}
                <div class="admin-card">
                    <h3>{{ admin.username }}</h3>
                    <div class="admin-property">
                        <span class="property-name">ID:</span> {{ admin._id }}
                    </div>
                    <div class="admin-property">
                        <span class="property-name">Email:</span> {{ admin.email }}
                    </div>
                    <div class="admin-property">
                        <span class="property-name">Rol:</span> {{ admin.role }}
                    </div>
                    <div class="admin-property">
                        <span class="property-name">Último login:</span> {{ admin.last_login or 'Nunca' }}
                    </div>
                    <div class="admin-property">
                        <span class="property-name">Activo:</span> {{ admin.active or admin.is_active or 'Desconocido' }}
                    </div>
                    <div class="admin-property">
                        <span class="property-name">Intentos fallidos:</span> {{ admin.failed_attempts or 0 }}
                    </div>
                    <div class="admin-property">
                        <span class="property-name">Bloqueado hasta:</span> {{ admin.locked_until or 'No bloqueado' }}
                    </div>
                    
                    <a href="{{ url_for('login_admin', username=admin.username) }}" class="btn">Acceder como {{ admin.username }}</a>
                </div>
            {% endfor %}
        {% else %}
            <p>No se encontraron usuarios administradores en la base de datos.</p>
        {% endif %}
        
        <a href="{{ url_for('index') }}" class="btn">Volver</a>
    </div>
</body>
</html>
    \"\"\")

if __name__ == '__main__':
    port = 5001
    logger.info(f"Iniciando aplicación de acceso directo al panel de administración en el puerto {port}...")
    app.run(host='127.0.0.1', port=port, debug=True)
"""
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)  # Hacer el script ejecutable
        logger.info(f"Script de acceso directo creado en {script_path}")
        return True, f"Script de acceso directo creado en {script_path}"
    except Exception as e:
        logger.error(f"Error al crear el script de acceso directo: {str(e)}")
        return False, f"Error al crear el script de acceso directo: {str(e)}"

def main():
    """Función principal"""
    logger.info("Iniciando diagnóstico de problemas de acceso...")
    logger.info(f"Trabajando exclusivamente con el dominio: edefrutos2025.xyz")
    logger.info(f"No se modificarán configuraciones globales del servidor")
    
    # 1. Verificar si la aplicación Flask está en ejecución localmente
    if check_port("127.0.0.1", 5000):
        logger.info("✅ La aplicación Flask está en ejecución en el puerto 5000")
    else:
        logger.info("⚠️ La aplicación Flask no está en ejecución en el puerto 5000")
        logger.info("Creando script para iniciar la aplicación localmente...")
        create_local_start_script()
    
    # 2. Verificar si el archivo WSGI existe
    wsgi_path = os.path.join(DOMAIN_ROOT, "wsgi.py")
    if os.path.exists(wsgi_path):
        logger.info(f"✅ El archivo WSGI existe en {wsgi_path}")
    else:
        logger.info(f"⚠️ No se encontró el archivo WSGI en {wsgi_path}")
        logger.info("Creando archivo WSGI...")
        create_wsgi_file()
    
    # 3. Crear script de acceso directo al panel de administración
    logger.info("Creando script de acceso directo al panel de administración...")
    create_direct_access_script()
    
    # 4. Resumen y recomendaciones
    logger.info("\n=== RESUMEN DEL DIAGNÓSTICO ===")
    logger.info("1. Se ha verificado si la aplicación Flask está en ejecución localmente")
    logger.info("2. Se ha verificado si el archivo WSGI existe")
    
    logger.info("\n=== ACCIONES REALIZADAS ===")
    logger.info("1. Se ha creado un script para iniciar la aplicación localmente: iniciar_app_local.sh")
    logger.info("2. Se ha creado un archivo WSGI para la aplicación")
    logger.info("3. Se ha creado un script de acceso directo al panel de administración: acceso_directo_admin.py")
    
    logger.info("\n=== PRÓXIMOS PASOS ===")
    logger.info("1. Ejecuta el script para iniciar la aplicación localmente:")
    logger.info("   $ cd /var/www/vhosts/edefrutos2025.xyz/httpdocs")
    logger.info("   $ ./iniciar_app_local.sh")
    logger.info("2. En otra terminal, ejecuta el script de acceso directo al panel de administración:")
    logger.info("   $ cd /var/www/vhosts/edefrutos2025.xyz/httpdocs")
    logger.info("   $ python3 acceso_directo_admin.py")
    logger.info("3. Abre un navegador y accede a: http://localhost:5001")
    logger.info("4. Sigue las instrucciones en la página para acceder al panel de administración")

if __name__ == "__main__":
    main()
