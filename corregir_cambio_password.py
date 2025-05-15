#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
from werkzeug.security import generate_password_hash

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

def desactivar_cambio_password_forzado(db):
    """Desactiva el cambio de contraseña forzado para todos los usuarios."""
    try:
        # Actualizar todos los usuarios para desactivar el cambio de contraseña forzado
        result = db.users.update_many(
            {},
            {"$set": {"force_password_change": False}}
        )
        
        logger.info(f"✅ Cambio de contraseña forzado desactivado para {result.modified_count} usuarios")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al desactivar cambio de contraseña forzado: {str(e)}")
        return False

def actualizar_usuario_normal(db):
    """Actualiza el usuario normal con una contraseña válida y sin cambio forzado."""
    try:
        # Datos del usuario
        email = "usuario@example.com"
        password = "admin123"
        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        # Actualizar el usuario
        result = db.users.update_one(
            {"email": email},
            {"$set": {
                "password": password_hash,
                "force_password_change": False,
                "password_changed_at": datetime.datetime.now(),
                "active": True,
                "login_attempts": 0,
                "locked": False
            }}
        )
        
        if result.matched_count > 0:
            logger.info(f"✅ Usuario {email} actualizado correctamente")
            return True
        else:
            logger.warning(f"⚠️ No se encontró el usuario {email}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error al actualizar usuario normal: {str(e)}")
        return False

def crear_acceso_directo_catalogs():
    """Crea un script de acceso directo a los catálogos."""
    ruta_archivo = "acceso_directo_catalogs_sin_password.py"
    
    try:
        contenido = """#!/usr/bin/env python3
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
    \"\"\"Crea una aplicación Flask para acceso directo a los catálogos.\"\"\"
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
        f.write(\"\"\"<!DOCTYPE html>
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
</html>\"\"\")
    
    app = crear_app_acceso_directo()
    logger.info("Iniciando servidor de acceso directo a catálogos...")
    logger.info("Accede a http://127.0.0.1:5000/ para seleccionar el tipo de acceso")
    app.run(host='127.0.0.1', port=5000, debug=True)
"""
        
        with open(ruta_archivo, 'w') as f:
            f.write(contenido)
        
        logger.info(f"✅ Script de acceso directo a catálogos creado: {ruta_archivo}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear script de acceso directo a catálogos: {str(e)}")
        return False

def main():
    """Función principal que ejecuta la corrección del cambio de contraseña forzado."""
    logger.info("Iniciando corrección del cambio de contraseña forzado...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # 1. Desactivar cambio de contraseña forzado para todos los usuarios
        cambio_password_ok = desactivar_cambio_password_forzado(db)
        
        # 2. Actualizar usuario normal
        usuario_ok = actualizar_usuario_normal(db)
        
        # 3. Crear script de acceso directo a catálogos
        acceso_directo_ok = crear_acceso_directo_catalogs()
        
        # Resumen
        logger.info("\n=== RESUMEN DE CORRECCIÓN ===")
        logger.info(f"1. Desactivar cambio de contraseña forzado: {'✅ Completado' if cambio_password_ok else '❌ No completado'}")
        logger.info(f"2. Actualizar usuario normal: {'✅ Completado' if usuario_ok else '❌ No completado'}")
        logger.info(f"3. Script de acceso directo: {'✅ Creado' if acceso_directo_ok else '❌ No creado'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Utiliza el script de acceso directo para acceder a los catálogos:")
        logger.info("   $ python3 acceso_directo_catalogs_sin_password.py")
        logger.info("3. Accede a http://127.0.0.1:5000/ y selecciona el tipo de acceso")
        logger.info("4. Serás redirigido automáticamente a los catálogos")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante la corrección: {str(e)}")
        return False
    
    finally:
        if client:
            client.close()
            logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
