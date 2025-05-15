#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
import requests
from flask import Flask, render_template, session, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import certifi
from pymongo import MongoClient
from bson.objectid import ObjectId

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
    return render_template('acceso_directo_session.html')

@app.route('/login_admin')
def login_admin():
    """Inicia sesión directamente como administrador."""
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        return jsonify({"error": "Error de conexión a MongoDB"})
    
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
        
        # Cerrar conexión
        client.close()
        
        # Verificar acceso a catálogos
        return verificar_acceso_catalogs()
    
    except Exception as e:
        logger.error(f"❌ Error al iniciar sesión como administrador: {str(e)}")
        if client:
            client.close()
        return jsonify({"error": f"Error al iniciar sesión: {str(e)}"})

@app.route('/login_user')
def login_user():
    """Inicia sesión directamente como usuario normal."""
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        return jsonify({"error": "Error de conexión a MongoDB"})
    
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
        
        # Cerrar conexión
        client.close()
        
        # Verificar acceso a catálogos
        return verificar_acceso_catalogs()
    
    except Exception as e:
        logger.error(f"❌ Error al iniciar sesión como usuario: {str(e)}")
        if client:
            client.close()
        return jsonify({"error": f"Error al iniciar sesión: {str(e)}"})

@app.route('/verificar_acceso')
def verificar_acceso_catalogs():
    """Verifica el acceso a los catálogos y muestra información detallada."""
    # Verificar si hay sesión activa
    if not session.get('logged_in'):
        return jsonify({"error": "No hay sesión activa"})
    
    # Mostrar información de la sesión
    info_sesion = {
        "email": session.get('email'),
        "username": session.get('username'),
        "role": session.get('role'),
        "user_id": session.get('user_id'),
        "name": session.get('name')
    }
    
    # Conectar a MongoDB para verificar catálogos
    client, db = conectar_mongodb()
    if client is None:
        return jsonify({"error": "Error de conexión a MongoDB", "session": info_sesion})
    
    try:
        # Obtener catálogos según el rol
        if session.get('role') == 'admin':
            catalogs_cursor = db.catalogs.find()
        else:
            catalogs_cursor = db.catalogs.find({"created_by": session.get('email')})
        
        # Convertir cursor a lista
        catalogs = []
        for c in catalogs_cursor:
            if c.get("_id"):
                c["_id"] = str(c["_id"])
                catalogs.append(c)
        
        # Cerrar conexión
        client.close()
        
        # Devolver información
        return jsonify({
            "success": True,
            "session": info_sesion,
            "catalogs_count": len(catalogs),
            "catalogs": [{"id": c["_id"], "name": c.get("name"), "rows": len(c.get("rows", []))} for c in catalogs]
        })
    
    except Exception as e:
        logger.error(f"❌ Error al verificar acceso a catálogos: {str(e)}")
        if client:
            client.close()
        return jsonify({"error": f"Error al verificar acceso: {str(e)}", "session": info_sesion})

@app.route('/crear_catalogo')
def crear_catalogo():
    """Crea un catálogo de prueba para el usuario actual."""
    # Verificar si hay sesión activa
    if not session.get('logged_in'):
        return jsonify({"error": "No hay sesión activa"})
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        return jsonify({"error": "Error de conexión a MongoDB"})
    
    try:
        # Crear catálogo de prueba
        catalogo = {
            "name": f"Catálogo de {session.get('name')}",
            "description": "Catálogo creado para pruebas de acceso",
            "headers": ["Número", "Descripción", "Valor"],
            "rows": [
                {"Número": "1", "Descripción": "Item de prueba 1", "Valor": "100"},
                {"Número": "2", "Descripción": "Item de prueba 2", "Valor": "200"}
            ],
            "created_by": session.get('email'),
            "created_at": datetime.datetime.now()
        }
        
        result = db.catalogs.insert_one(catalogo)
        
        # Cerrar conexión
        client.close()
        
        # Devolver información
        return jsonify({
            "success": True,
            "message": "Catálogo creado correctamente",
            "catalog_id": str(result.inserted_id)
        })
    
    except Exception as e:
        logger.error(f"❌ Error al crear catálogo: {str(e)}")
        if client:
            client.close()
        return jsonify({"error": f"Error al crear catálogo: {str(e)}"})

@app.route('/verificar_blueprint')
def verificar_blueprint():
    """Verifica si el blueprint de catálogos está registrado correctamente."""
    # Hacer una solicitud a la aplicación principal
    try:
        response = requests.get('http://127.0.0.1:8002/catalogs/')
        
        return jsonify({
            "status_code": response.status_code,
            "url": response.url,
            "content": response.text[:500] + "..." if len(response.text) > 500 else response.text
        })
    
    except Exception as e:
        logger.error(f"❌ Error al verificar blueprint: {str(e)}")
        return jsonify({"error": f"Error al verificar blueprint: {str(e)}"})

@app.route('/verificar_permisos')
def verificar_permisos():
    """Verifica y corrige los permisos de los catálogos."""
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        return jsonify({"error": "Error de conexión a MongoDB"})
    
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
            
            # Cerrar conexión
            client.close()
            
            return jsonify({
                "success": True,
                "message": f"Se corrigieron {len(docs_sin_created_by)} catálogos sin permisos"
            })
        else:
            # Cerrar conexión
            client.close()
            
            return jsonify({
                "success": True,
                "message": "Todos los catálogos tienen permisos correctos"
            })
    
    except Exception as e:
        logger.error(f"❌ Error al verificar permisos: {str(e)}")
        if client:
            client.close()
        return jsonify({"error": f"Error al verificar permisos: {str(e)}"})

if __name__ == '__main__':
    # Crear plantilla de acceso directo si no existe
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "templates")
    template_path = os.path.join(templates_dir, "acceso_directo_session.html")
    
    if not os.path.exists(template_path):
        with open(template_path, 'w') as f:
            f.write("""
{% extends "base.html" %}
{% block title %}Acceso Directo a Sesión{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h2 class="mb-0">Acceso Directo a Sesión</h2>
                </div>
                <div class="card-body">
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-header bg-success text-white">
                                    <h4 class="mb-0">Iniciar Sesión</h4>
                                </div>
                                <div class="card-body d-flex flex-column">
                                    <p>Selecciona un tipo de usuario para iniciar sesión:</p>
                                    <div class="mt-auto">
                                        <button onclick="loginAdmin()" class="btn btn-primary btn-block mb-2">
                                            <i class="fas fa-user-shield"></i> Acceder como Administrador
                                        </button>
                                        <button onclick="loginUser()" class="btn btn-secondary btn-block">
                                            <i class="fas fa-user"></i> Acceder como Usuario Normal
                                        </button>
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
                                    <p>Utilidades para gestionar la sesión y catálogos:</p>
                                    <div class="mt-auto">
                                        <button onclick="verificarAcceso()" class="btn btn-info btn-block mb-2">
                                            <i class="fas fa-search"></i> Verificar Acceso a Catálogos
                                        </button>
                                        <button onclick="crearCatalogo()" class="btn btn-success btn-block mb-2">
                                            <i class="fas fa-plus-circle"></i> Crear Catálogo de Prueba
                                        </button>
                                        <button onclick="verificarBlueprint()" class="btn btn-warning btn-block mb-2">
                                            <i class="fas fa-code"></i> Verificar Blueprint
                                        </button>
                                        <button onclick="verificarPermisos()" class="btn btn-danger btn-block">
                                            <i class="fas fa-shield-alt"></i> Verificar/Corregir Permisos
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div id="resultContainer" class="mt-4" style="display: none;">
                        <div class="card">
                            <div class="card-header bg-secondary text-white">
                                <h4 class="mb-0">Resultado</h4>
                            </div>
                            <div class="card-body">
                                <pre id="resultContent" class="bg-light p-3 rounded" style="max-height: 400px; overflow-y: auto;"></pre>
                            </div>
                        </div>
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

{% block scripts %}
<script>
function showResult(data) {
    document.getElementById('resultContent').textContent = JSON.stringify(data, null, 2);
    document.getElementById('resultContainer').style.display = 'block';
    window.scrollTo(0, document.body.scrollHeight);
}

function loginAdmin() {
    fetch('/login_admin')
        .then(response => response.json())
        .then(data => {
            showResult(data);
        })
        .catch(error => {
            showResult({error: error.toString()});
        });
}

function loginUser() {
    fetch('/login_user')
        .then(response => response.json())
        .then(data => {
            showResult(data);
        })
        .catch(error => {
            showResult({error: error.toString()});
        });
}

function verificarAcceso() {
    fetch('/verificar_acceso')
        .then(response => response.json())
        .then(data => {
            showResult(data);
        })
        .catch(error => {
            showResult({error: error.toString()});
        });
}

function crearCatalogo() {
    fetch('/crear_catalogo')
        .then(response => response.json())
        .then(data => {
            showResult(data);
        })
        .catch(error => {
            showResult({error: error.toString()});
        });
}

function verificarBlueprint() {
    fetch('/verificar_blueprint')
        .then(response => response.json())
        .then(data => {
            showResult(data);
        })
        .catch(error => {
            showResult({error: error.toString()});
        });
}

function verificarPermisos() {
    fetch('/verificar_permisos')
        .then(response => response.json())
        .then(data => {
            showResult(data);
        })
        .catch(error => {
            showResult({error: error.toString()});
        });
}
</script>
{% endblock %}
""")
        logger.info("✅ Plantilla de acceso directo creada")
    
    # Iniciar servidor
    logger.info("Iniciando servidor de acceso directo en http://127.0.0.1:5005...")
    app.run(host='127.0.0.1', port=5005, debug=True)
