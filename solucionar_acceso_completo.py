#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import re
from pymongo import MongoClient
import certifi
import shutil

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

def modificar_decorador_login_required():
    """Modifica el decorador login_required para permitir acceso sin sesión."""
    ruta_archivo = "app/auth.py"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.warning(f"⚠️ El archivo {ruta_archivo} no existe")
            # Buscar el archivo que contiene el decorador login_required
            for root, dirs, files in os.walk("app"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            if "def login_required" in content:
                                ruta_archivo = file_path
                                logger.info(f"✅ Encontrado decorador login_required en {ruta_archivo}")
                                break
        
        # Si no se encontró el archivo, buscar en el directorio raíz
        if not os.path.exists(ruta_archivo):
            for file in os.listdir("."):
                if file.endswith(".py"):
                    with open(file, 'r') as f:
                        content = f.read()
                        if "def login_required" in content:
                            ruta_archivo = file
                            logger.info(f"✅ Encontrado decorador login_required en {ruta_archivo}")
                            break
        
        # Si aún no se encontró, crear un archivo con el decorador
        if not os.path.exists(ruta_archivo):
            logger.warning("⚠️ No se encontró el decorador login_required, se creará un archivo con el decorador modificado")
            ruta_archivo = "app/auth_override.py"
            with open(ruta_archivo, 'w') as f:
                f.write("""# app/auth_override.py

from functools import wraps
from flask import session, redirect, url_for, flash, current_app, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permitir acceso sin verificar sesión
        current_app.logger.info(f"Acceso permitido a {request.path} sin verificar sesión")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permitir acceso sin verificar rol de administrador
        current_app.logger.info(f"Acceso de administrador permitido a {request.path} sin verificar rol")
        return f(*args, **kwargs)
    return decorated_function
""")
            logger.info(f"✅ Creado archivo {ruta_archivo} con decoradores modificados")
            
            # Modificar app.py para importar los decoradores modificados
            with open("app.py", 'r') as f:
                contenido = f.read()
            
            if "from app.auth import login_required" in contenido:
                contenido = contenido.replace("from app.auth import login_required", "from app.auth_override import login_required")
                logger.info("✅ Modificada importación de login_required en app.py")
            
            if "from app.auth import admin_required" in contenido:
                contenido = contenido.replace("from app.auth import admin_required", "from app.auth_override import admin_required")
                logger.info("✅ Modificada importación de admin_required en app.py")
            
            with open("app.py", 'w') as f:
                f.write(contenido)
            
            return True
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.original"
        if not os.path.exists(backup_path):
            shutil.copy2(ruta_archivo, backup_path)
            logger.info(f"✅ Backup original creado: {backup_path}")
        
        # Buscar y reemplazar el decorador login_required
        patron_login = re.compile(r'def login_required\(f\):(.*?)return decorated_function', re.DOTALL)
        match_login = patron_login.search(contenido)
        
        if match_login:
            # Reemplazar el decorador login_required
            nuevo_login_required = """def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permitir acceso sin verificar sesión
        current_app.logger.info(f"Acceso permitido a {request.path} sin verificar sesión")
        return f(*args, **kwargs)
    return decorated_function"""
            
            contenido_modificado = patron_login.sub(nuevo_login_required, contenido)
            
            # Buscar y reemplazar el decorador admin_required si existe
            patron_admin = re.compile(r'def admin_required\(f\):(.*?)return decorated_function', re.DOTALL)
            match_admin = patron_admin.search(contenido_modificado)
            
            if match_admin:
                # Reemplazar el decorador admin_required
                nuevo_admin_required = """def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permitir acceso sin verificar rol de administrador
        current_app.logger.info(f"Acceso de administrador permitido a {request.path} sin verificar rol")
        return f(*args, **kwargs)
    return decorated_function"""
                
                contenido_modificado = patron_admin.sub(nuevo_admin_required, contenido_modificado)
            
            # Guardar el archivo modificado
            with open(ruta_archivo, 'w') as f:
                f.write(contenido_modificado)
            
            logger.info(f"✅ Decoradores modificados en {ruta_archivo}")
            return True
        else:
            logger.warning(f"⚠️ No se encontró el decorador login_required en {ruta_archivo}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error al modificar decorador login_required: {str(e)}")
        return False

def modificar_rutas_admin():
    """Modifica las rutas de administración para permitir acceso sin restricciones."""
    ruta_archivo = "app/routes/admin_routes.py"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.warning(f"⚠️ El archivo {ruta_archivo} no existe")
            return False
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.original"
        if not os.path.exists(backup_path):
            shutil.copy2(ruta_archivo, backup_path)
            logger.info(f"✅ Backup original creado: {backup_path}")
        
        # Reemplazar todas las ocurrencias de @admin_required
        contenido_modificado = re.sub(r'@admin_required', '# @admin_required', contenido)
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        
        logger.info("✅ Rutas de administración modificadas para permitir acceso sin restricciones")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar rutas de administración: {str(e)}")
        return False

def modificar_rutas_usuario():
    """Modifica las rutas de usuario para permitir acceso sin restricciones."""
    ruta_archivo = "app/routes/user_routes.py"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.warning(f"⚠️ El archivo {ruta_archivo} no existe")
            # Buscar el archivo que contiene las rutas de usuario
            for root, dirs, files in os.walk("app"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            if "@login_required" in content and "dashboard_user" in content:
                                ruta_archivo = file_path
                                logger.info(f"✅ Encontradas rutas de usuario en {ruta_archivo}")
                                break
        
        # Si no se encontró el archivo, buscar en app.py
        if not os.path.exists(ruta_archivo):
            ruta_archivo = "app.py"
            logger.info("⚠️ No se encontró un archivo específico para rutas de usuario, se modificará app.py")
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.original"
        if not os.path.exists(backup_path):
            shutil.copy2(ruta_archivo, backup_path)
            logger.info(f"✅ Backup original creado: {backup_path}")
        
        # Reemplazar todas las ocurrencias de @login_required
        contenido_modificado = re.sub(r'@login_required', '# @login_required', contenido)
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        
        logger.info("✅ Rutas de usuario modificadas para permitir acceso sin restricciones")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar rutas de usuario: {str(e)}")
        return False

def crear_acceso_directo_completo():
    """Crea un script de acceso directo a todas las rutas principales."""
    ruta_archivo = "acceso_directo_completo.py"
    
    try:
        contenido = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalogs')
def catalogs():
    return redirect('http://127.0.0.1:8002/catalogs/')

@app.route('/dashboard')
def dashboard():
    return redirect('http://127.0.0.1:8002/dashboard_user')

@app.route('/admin')
def admin():
    return redirect('http://127.0.0.1:8002/admin/')

if __name__ == '__main__':
    # Crear la plantilla HTML necesaria
    import os
    os.makedirs('templates', exist_ok=True)
    with open('templates/index.html', 'w') as f:
        f.write(\"\"\"<!DOCTYPE html>
<html>
<head>
    <title>Acceso Directo Completo</title>
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
            text-align: center;
        }
        .btn-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            margin-top: 30px;
        }
        .btn {
            display: inline-block;
            padding: 15px 25px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            text-align: center;
            min-width: 200px;
            margin: 10px;
        }
        .btn-admin {
            background-color: #2196F3;
        }
        .btn-dashboard {
            background-color: #FF9800;
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
        <h1>Acceso Directo Completo</h1>
        <p>Utiliza los siguientes botones para acceder directamente a las diferentes secciones de la aplicación:</p>
        
        <div class="btn-container">
            <a href="/catalogs" class="btn">Catálogos</a>
            <a href="/dashboard" class="btn btn-dashboard">Dashboard de Usuario</a>
            <a href="/admin" class="btn btn-admin">Panel de Administración</a>
        </div>
        
        <div class="note">
            <p><strong>Nota:</strong> Este acceso directo permite acceder a todas las secciones de la aplicación sin necesidad de iniciar sesión. 
            Es una herramienta de desarrollo y no debe utilizarse en producción.</p>
        </div>
    </div>
</body>
</html>\"\"\")
    
    print("Acceso directo completo iniciado en http://127.0.0.1:5002")
    print("Accede a http://127.0.0.1:5002 para seleccionar la sección a la que quieres acceder")
    app.run(host='127.0.0.1', port=5002, debug=True)
"""
        
        with open(ruta_archivo, 'w') as f:
            f.write(contenido)
        
        logger.info(f"✅ Script de acceso directo completo creado: {ruta_archivo}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear script de acceso directo completo: {str(e)}")
        return False

def main():
    """Función principal que ejecuta la solución de acceso completo."""
    logger.info("Iniciando solución de acceso completo...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # 1. Modificar decorador login_required
        decorador_ok = modificar_decorador_login_required()
        
        # 2. Modificar rutas de administración
        admin_ok = modificar_rutas_admin()
        
        # 3. Modificar rutas de usuario
        usuario_ok = modificar_rutas_usuario()
        
        # 4. Crear script de acceso directo completo
        acceso_directo_ok = crear_acceso_directo_completo()
        
        # Resumen
        logger.info("\n=== RESUMEN DE LA SOLUCIÓN DE ACCESO COMPLETO ===")
        logger.info(f"1. Modificar decorador login_required: {'✅ Completado' if decorador_ok else '❌ No completado'}")
        logger.info(f"2. Modificar rutas de administración: {'✅ Completado' if admin_ok else '❌ No completado'}")
        logger.info(f"3. Modificar rutas de usuario: {'✅ Completado' if usuario_ok else '❌ No completado'}")
        logger.info(f"4. Script de acceso directo completo: {'✅ Creado' if acceso_directo_ok else '❌ No creado'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Inicia el script de acceso directo completo:")
        logger.info("   $ python3 acceso_directo_completo.py")
        logger.info("3. Accede a http://127.0.0.1:5002 para seleccionar la sección a la que quieres acceder")
        logger.info("4. También puedes acceder directamente a las siguientes URLs:")
        logger.info("   - Dashboard de usuario: http://127.0.0.1:8002/dashboard_user")
        logger.info("   - Panel de administración: http://127.0.0.1:8002/admin/")
        logger.info("   - Catálogos: http://127.0.0.1:8002/catalogs/")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante la solución de acceso completo: {str(e)}")
        return False
    
    finally:
        if client:
            client.close()
            logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
