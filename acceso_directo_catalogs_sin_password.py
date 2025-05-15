#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
from flask import Flask, session, redirect, url_for, render_template
import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Cargar configuración
try:
    from config import Config
    MONGO_URI = Config.MONGO_URI
except ImportError:
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://admin:admin123@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority')

def crear_app_acceso_directo():
    """Crea una aplicación Flask para acceso directo a los catálogos."""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    @app.route('/')
    def index():
        return render_template('acceso_directo.html')
    
    @app.route('/login_admin')
    def login_admin():
        # Establecer datos de sesión para el administrador
        session.clear()
        session['logged_in'] = True
        session['email'] = 'admin@example.com'
        session['username'] = 'admin'
        session['role'] = 'admin'
        session['name'] = 'Administrador'
        
        logger.info("Sesión establecida para administrador")
        logger.info(f"Datos de sesión: {dict(session)}")
        
        # Redirigir a los catálogos
        return redirect('http://127.0.0.1:8002/catalogs/')
    
    @app.route('/login_usuario')
    def login_usuario():
        # Establecer datos de sesión para el usuario normal
        session.clear()
        session['logged_in'] = True
        session['email'] = 'usuario@example.com'
        session['username'] = 'usuario'
        session['role'] = 'user'
        session['name'] = 'Usuario Normal'
        
        logger.info("Sesión establecida para usuario normal")
        logger.info(f"Datos de sesión: {dict(session)}")
        
        # Redirigir a los catálogos
        return redirect('http://127.0.0.1:8002/catalogs/')
    
    return app

if __name__ == '__main__':
    # Crear la plantilla HTML necesaria
    os.makedirs('templates', exist_ok=True)
    with open('templates/acceso_directo.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Acceso Directo a Catálogos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .btn-container {
            display: flex;
            justify-content: space-around;
            margin-top: 30px;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            text-align: center;
            min-width: 200px;
        }
        .btn-admin {
            background-color: #2196F3;
        }
        .btn:hover {
            opacity: 0.9;
        }
        .note {
            margin-top: 30px;
            padding: 10px;
            background-color: #fffde7;
            border-left: 4px solid #ffd600;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Acceso Directo a Catálogos</h1>
        <p>Utiliza los siguientes botones para acceder directamente a los catálogos sin necesidad de iniciar sesión:</p>
        
        <div class="btn-container">
            <a href="/login_admin" class="btn btn-admin">Acceder como Administrador</a>
            <a href="/login_usuario" class="btn">Acceder como Usuario</a>
        </div>
        
        <div class="note">
            <p><strong>Nota:</strong> Este acceso directo establece una sesión válida sin necesidad de introducir credenciales. 
            Es una herramienta de desarrollo y no debe utilizarse en producción.</p>
        </div>
    </div>
</body>
</html>""")
    
    app = crear_app_acceso_directo()
    logger.info("Iniciando servidor de acceso directo a catálogos...")
    logger.info("Accede a http://127.0.0.1:5000/ para seleccionar el tipo de acceso")
    app.run(host='127.0.0.1', port=5000, debug=True)
