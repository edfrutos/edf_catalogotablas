#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
from flask import Flask, render_template, session, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
from werkzeug.security import generate_password_hash, check_password_hash

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
    SECRET_KEY = Config.SECRET_KEY
except ImportError:
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://admin:admin123@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_temporal_para_desarrollo')

# Crear aplicación Flask simple para acceso directo
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "templates"))
app.secret_key = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)
app.config['SESSION_USE_SIGNER'] = False
app.config['SESSION_COOKIE_SECURE'] = False  # Para desarrollo local
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Conectar a MongoDB
def conectar_mongodb():
    """Establece conexión con MongoDB y retorna el cliente y la base de datos."""
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client.get_database()
        logger.info("✅ Conexión a MongoDB establecida correctamente")
        return client, db
    except Exception as e:
        logger.error(f"❌ Error al conectar a MongoDB: {str(e)}")
        return None, None

# Rutas para acceso directo
@app.route('/')
def index():
    """Página principal con opciones de acceso directo."""
    return render_template('acceso_directo_catalogs.html')

@app.route('/login_admin')
def login_admin():
    """Inicia sesión directamente como administrador."""
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        flash("Error de conexión a MongoDB", "danger")
        return redirect(url_for('index'))
    
    try:
        # Buscar usuario administrador
        admin_user = db.users.find_one({"email": "admin@example.com"})
        
        if not admin_user:
            # Crear usuario administrador si no existe
            admin_user = {
                "email": "admin@example.com",
                "username": "administrator",
                "password": generate_password_hash("admin123"),
                "role": "admin",
                "name": "Administrador",
                "last_name": "Sistema",
                "created_at": datetime.datetime.now()
            }
            db.users.insert_one(admin_user)
            logger.info("✅ Usuario administrador creado")
        
        # Establecer sesión
        session.clear()
        session['logged_in'] = True
        session['email'] = admin_user.get('email')
        session['username'] = admin_user.get('username')
        session['role'] = 'admin'
        session['user_id'] = str(admin_user.get('_id'))
        session['name'] = admin_user.get('name', 'Administrador')
        
        logger.info(f"✅ Sesión de administrador establecida: {session}")
        flash("Has iniciado sesión como administrador", "success")
        
        # Cerrar conexión
        client.close()
        
        return redirect('/catalogs')
    
    except Exception as e:
        logger.error(f"❌ Error al iniciar sesión como administrador: {str(e)}")
        flash(f"Error al iniciar sesión: {str(e)}", "danger")
        if client:
            client.close()
        return redirect(url_for('index'))

@app.route('/login_user')
def login_user():
    """Inicia sesión directamente como usuario normal."""
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        flash("Error de conexión a MongoDB", "danger")
        return redirect(url_for('index'))
    
    try:
        # Buscar usuario normal
        user = db.users.find_one({"email": "usuario@example.com"})
        
        if not user:
            # Crear usuario normal si no existe
            user = {
                "email": "usuario@example.com",
                "username": "usuario",
                "password": generate_password_hash("usuario123"),
                "role": "user",
                "name": "Usuario",
                "last_name": "Normal",
                "created_at": datetime.datetime.now()
            }
            db.users.insert_one(user)
            logger.info("✅ Usuario normal creado")
        
        # Establecer sesión
        session.clear()
        session['logged_in'] = True
        session['email'] = user.get('email')
        session['username'] = user.get('username')
        session['role'] = 'user'
        session['user_id'] = str(user.get('_id'))
        session['name'] = user.get('name', 'Usuario')
        
        logger.info(f"✅ Sesión de usuario establecida: {session}")
        flash("Has iniciado sesión como usuario normal", "success")
        
        # Cerrar conexión
        client.close()
        
        return redirect('/catalogs')
    
    except Exception as e:
        logger.error(f"❌ Error al iniciar sesión como usuario: {str(e)}")
        flash(f"Error al iniciar sesión: {str(e)}", "danger")
        if client:
            client.close()
        return redirect(url_for('index'))

@app.route('/crear_catalogo_prueba')
def crear_catalogo_prueba():
    """Crea un catálogo de prueba."""
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        flash("Error de conexión a MongoDB", "danger")
        return redirect(url_for('index'))
    
    try:
        # Verificar si ya existe un catálogo de prueba
        catalogo_prueba = db.catalogs.find_one({"name": "Catálogo de Prueba"})
        
        if not catalogo_prueba:
            # Crear catálogo de prueba
            catalogo = {
                "name": "Catálogo de Prueba",
                "description": "Catálogo creado para pruebas de acceso",
                "headers": ["Número", "Descripción", "Valor"],
                "rows": [
                    {"Número": "1", "Descripción": "Item de prueba 1", "Valor": "100"},
                    {"Número": "2", "Descripción": "Item de prueba 2", "Valor": "200"}
                ],
                "created_by": "admin@example.com",
                "created_at": datetime.datetime.now()
            }
            db.catalogs.insert_one(catalogo)
            logger.info("✅ Catálogo de prueba creado")
            flash("Catálogo de prueba creado correctamente", "success")
        else:
            logger.info("ℹ️ El catálogo de prueba ya existe")
            flash("El catálogo de prueba ya existe", "info")
        
        # Cerrar conexión
        client.close()
        
        return redirect(url_for('index'))
    
    except Exception as e:
        logger.error(f"❌ Error al crear catálogo de prueba: {str(e)}")
        flash(f"Error al crear catálogo: {str(e)}", "danger")
        if client:
            client.close()
        return redirect(url_for('index'))

@app.route('/verificar_permisos')
def verificar_permisos():
    """Verifica y corrige los permisos de los catálogos."""
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        flash("Error de conexión a MongoDB", "danger")
        return redirect(url_for('index'))
    
    try:
        # Verificar catálogos sin created_by
        docs_sin_created_by = list(db.catalogs.find({"created_by": {"$exists": False}}))
        
        if docs_sin_created_by:
            logger.info(f"Corrigiendo {len(docs_sin_created_by)} documentos sin created_by...")
            
            for doc in docs_sin_created_by:
                db.catalogs.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"created_by": "admin@example.com"}}
                )
            logger.info("✅ Documentos actualizados con created_by")
            flash(f"Se corrigieron {len(docs_sin_created_by)} catálogos sin permisos", "success")
        else:
            logger.info("✅ Todos los catálogos tienen permisos correctos")
            flash("Todos los catálogos tienen permisos correctos", "success")
        
        # Cerrar conexión
        client.close()
        
        return redirect(url_for('index'))
    
    except Exception as e:
        logger.error(f"❌ Error al verificar permisos: {str(e)}")
        flash(f"Error al verificar permisos: {str(e)}", "danger")
        if client:
            client.close()
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Crear plantilla de acceso directo si no existe
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "templates")
    template_path = os.path.join(templates_dir, "acceso_directo_catalogs.html")
    
    if not os.path.exists(template_path):
        with open(template_path, 'w') as f:
            f.write("""
{% extends "base.html" %}
{% block title %}Acceso Directo a Catálogos{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h2 class="mb-0">Acceso Directo a Catálogos</h2>
                </div>
                <div class="card-body">
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-header bg-success text-white">
                                    <h4 class="mb-0">Iniciar Sesión</h4>
                                </div>
                                <div class="card-body d-flex flex-column">
                                    <p>Selecciona un tipo de usuario para acceder directamente a los catálogos:</p>
                                    <div class="mt-auto">
                                        <a href="{{ url_for('login_admin') }}" class="btn btn-primary btn-block mb-2">
                                            <i class="fas fa-user-shield"></i> Acceder como Administrador
                                        </a>
                                        <a href="{{ url_for('login_user') }}" class="btn btn-secondary btn-block">
                                            <i class="fas fa-user"></i> Acceder como Usuario Normal
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-header bg-info text-white">
                                    <h4 class="mb-0">Herramientas</h4>
                                </div>
                                <div class="card-body d-flex flex-column">
                                    <p>Utilidades para gestionar los catálogos:</p>
                                    <div class="mt-auto">
                                        <a href="{{ url_for('crear_catalogo_prueba') }}" class="btn btn-success btn-block mb-2">
                                            <i class="fas fa-plus-circle"></i> Crear Catálogo de Prueba
                                        </a>
                                        <a href="{{ url_for('verificar_permisos') }}" class="btn btn-warning btn-block">
                                            <i class="fas fa-shield-alt"></i> Verificar/Corregir Permisos
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="alert alert-info">
                        <h5><i class="fas fa-info-circle"></i> Información</h5>
                        <p>Esta herramienta te permite acceder directamente a los catálogos sin pasar por el proceso normal de inicio de sesión.</p>
                        <p><strong>Credenciales de administrador:</strong> admin@example.com / admin123</p>
                        <p><strong>Credenciales de usuario:</strong> usuario@example.com / usuario123</p>
                    </div>
                </div>
                <div class="card-footer text-center">
                    <a href="http://127.0.0.1:8002" class="btn btn-outline-secondary">
                        <i class="fas fa-arrow-left"></i> Volver a la Aplicación Principal
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""")
        logger.info("✅ Plantilla de acceso directo creada")
    
    # Iniciar servidor
    logger.info("Iniciando servidor de acceso directo en http://127.0.0.1:5004...")
    app.run(host='127.0.0.1', port=5004, debug=True)
