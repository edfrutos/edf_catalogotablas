#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
from flask import Flask, session, redirect, url_for
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
    """Crea una aplicación Flask para acceso directo."""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    @app.route('/')
    def acceso_directo():
        # Establecer datos de sesión para el usuario normal
        session['logged_in'] = True
        session['email'] = 'usuario@example.com'
        session['username'] = 'usuario'
        session['role'] = 'user'
        session['name'] = 'Usuario Normal'
        
        logger.info("Sesión establecida para usuario normal")
        logger.info(f"Datos de sesión: {dict(session)}")
        
        # Redirigir al dashboard de usuario
        return redirect('/dashboard_user')
    
    return app

if __name__ == '__main__':
    app = crear_app_acceso_directo()
    logger.info("Iniciando servidor de acceso directo para usuario normal...")
    logger.info("Accede a http://127.0.0.1:5000/ para iniciar sesión automáticamente como usuario normal")
    app.run(host='127.0.0.1', port=5000, debug=True)
