#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para acceder directamente al panel de administración sin pasar por el login normal.
Este script crea una sesión de administrador y proporciona acceso directo al panel.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from flask import Flask, session, redirect, url_for, request, render_template, flash
from flask_session import Session

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

# Inicializar la extensión de sesión
Session(app)

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
    """Página principal que muestra información sobre el script"""
    return render_template('acceso_directo.html', 
                          title="Acceso Directo al Panel de Administración",
                          message="Esta herramienta permite acceder directamente al panel de administración.")

@app.route('/login_admin/<username>')
def login_admin(username):
    """Crea una sesión de administrador para el usuario especificado"""
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
        return redirect('/admin/')
        
    except Exception as e:
        logger.error(f"Error al crear sesión: {str(e)}")
        flash(f"Error al crear sesión: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/check_session')
def check_session():
    """Verifica el estado de la sesión actual"""
    session_data = {key: session.get(key) for key in session}
    return render_template('session_info.html', 
                          title="Información de Sesión",
                          session_data=session_data)

@app.route('/logout')
def logout():
    """Cierra la sesión actual"""
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for('index'))

# Crear plantillas necesarias
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'), exist_ok=True)

# Crear plantilla acceso_directo.html
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'acceso_directo.html'), 'w') as f:
    f.write("""
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
            <a href="{{ url_for('check_session') }}" class="btn btn-info">Verificar sesión actual</a>
            <a href="{{ url_for('logout') }}" class="btn btn-danger">Cerrar sesión</a>
        </div>
    </div>
</body>
</html>
    """)

# Crear plantilla session_info.html
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'session_info.html'), 'w') as f:
    f.write("""
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
    """)

if __name__ == '__main__':
    port = 5004
    logger.info(f"Iniciando aplicación de acceso directo al panel de administración en el puerto {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
