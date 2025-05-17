#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import shutil
import requests
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def crear_script_acceso_simple():
    """Crea un script de acceso simple con enlaces directos."""
    ruta_archivo = "acceso_simple.py"
    
    try:
        contenido = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Acceso Directo Simple</title>
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
                flex-direction: column;
                align-items: center;
                margin-top: 30px;
            }
            .btn {
                display: block;
                padding: 15px 25px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                text-align: center;
                width: 80%;
                margin: 10px 0;
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Acceso Directo Simple</h1>
            <p>Haz clic en los enlaces para acceder directamente:</p>
            
            <div class="btn-container">
                <a href="http://127.0.0.1:8002/catalogs/" class="btn" target="_blank">Ver Catálogos</a>
                <a href="http://127.0.0.1:8002/dashboard_user" class="btn btn-dashboard" target="_blank">Dashboard de Usuario</a>
                <a href="http://127.0.0.1:8002/admin/" class="btn btn-admin" target="_blank">Panel de Administración</a>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    print("Acceso simple iniciado en http://127.0.0.1:5003")
    print("Accede a http://127.0.0.1:5003 para ver los enlaces directos")
    app.run(host='127.0.0.1', port=5003, debug=True)
"""
        
        with open(ruta_archivo, 'w') as f:
            f.write(contenido)
        
        logger.info(f"✅ Script de acceso simple creado: {ruta_archivo}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear script de acceso simple: {str(e)}")
        return False

def modificar_plantilla_admin():
    """Modifica la plantilla del panel de administración para corregir los enlaces."""
    ruta_archivo = "app/templates/admin/dashboard.html"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.warning(f"⚠️ El archivo {ruta_archivo} no existe")
            # Buscar la plantilla del panel de administración
            for root, dirs, files in os.walk("app/templates"):
                for file in files:
                    if file.endswith(".html") and ("admin" in file or "dashboard" in file):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            if "admin" in content and ("dashboard" in content or "panel" in content):
                                ruta_archivo = file_path
                                logger.info(f"✅ Encontrada plantilla del panel de administración en {ruta_archivo}")
                                break
        
        # Si no se encontró el archivo, no hacer nada
        if not os.path.exists(ruta_archivo):
            logger.warning("⚠️ No se encontró la plantilla del panel de administración")
            return False
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.original"
        if not os.path.exists(backup_path):
            shutil.copy2(ruta_archivo, backup_path)
            logger.info(f"✅ Backup original creado: {backup_path}")
        
        # Analizar el HTML con BeautifulSoup
        soup = BeautifulSoup(contenido, 'html.parser')
        
        # Corregir todos los enlaces
        for a in soup.find_all('a'):
            if a.get('href') and a.get('href').startswith('/'):
                a['href'] = f"http://127.0.0.1:8002{a['href']}"
                a['target'] = '_blank'
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(str(soup))
        
        logger.info(f"✅ Plantilla del panel de administración modificada: {ruta_archivo}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar plantilla del panel de administración: {str(e)}")
        return False

def modificar_plantilla_dashboard_user():
    """Modifica la plantilla del dashboard de usuario para corregir los enlaces."""
    ruta_archivo = "app/templates/dashboard_user.html"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.warning(f"⚠️ El archivo {ruta_archivo} no existe")
            # Buscar la plantilla del dashboard de usuario
            for root, dirs, files in os.walk("app/templates"):
                for file in files:
                    if file.endswith(".html") and "dashboard" in file and "user" in file:
                        file_path = os.path.join(root, file)
                        ruta_archivo = file_path
                        logger.info(f"✅ Encontrada plantilla del dashboard de usuario en {ruta_archivo}")
                        break
        
        # Si no se encontró el archivo, no hacer nada
        if not os.path.exists(ruta_archivo):
            logger.warning("⚠️ No se encontró la plantilla del dashboard de usuario")
            return False
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.original"
        if not os.path.exists(backup_path):
            shutil.copy2(ruta_archivo, backup_path)
            logger.info(f"✅ Backup original creado: {backup_path}")
        
        # Analizar el HTML con BeautifulSoup
        soup = BeautifulSoup(contenido, 'html.parser')
        
        # Corregir todos los enlaces
        for a in soup.find_all('a'):
            if a.get('href') and a.get('href').startswith('/'):
                a['href'] = f"http://127.0.0.1:8002{a['href']}"
                a['target'] = '_blank'
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(str(soup))
        
        logger.info(f"✅ Plantilla del dashboard de usuario modificada: {ruta_archivo}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar plantilla del dashboard de usuario: {str(e)}")
        return False

def crear_script_bypass_login():
    """Crea un script para acceder directamente sin login."""
    ruta_archivo = "bypass_login.py"
    
    try:
        contenido = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import requests
from flask import Flask, redirect, render_template_string, request, session
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'bypass_login_secret_key'

# URLs de la aplicación principal
BASE_URL = 'http://127.0.0.1:8002'
ADMIN_URL = f'{BASE_URL}/admin/'
USER_URL = f'{BASE_URL}/dashboard_user'
CATALOGS_URL = f'{BASE_URL}/catalogs/'

@app.route('/')
def index():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bypass Login</title>
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
                flex-direction: column;
                align-items: center;
                margin-top: 30px;
            }
            .btn {
                display: block;
                padding: 15px 25px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                text-align: center;
                width: 80%;
                margin: 10px 0;
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
            <h1>Bypass Login</h1>
            <p>Selecciona una opción para acceder directamente:</p>
            
            <div class="btn-container">
                <a href="/bypass/catalogs" class="btn">Ver Catálogos</a>
                <a href="/bypass/dashboard" class="btn btn-dashboard">Dashboard de Usuario</a>
                <a href="/bypass/admin" class="btn btn-admin">Panel de Administración</a>
            </div>
            
            <div class="note">
                <p><strong>Nota:</strong> Este acceso directo permite acceder a todas las secciones de la aplicación sin necesidad de iniciar sesión. 
                Es una herramienta de desarrollo y no debe utilizarse en producción.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/bypass/admin')
def bypass_admin():
    try:
        # Obtener la página de administración
        response = requests.get(ADMIN_URL)
        if response.status_code == 200:
            # Modificar los enlaces para que apunten a la aplicación principal
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a'):
                if a.get('href') and a.get('href').startswith('/'):
                    a['href'] = f"{BASE_URL}{a['href']}"
            
            # Devolver la página modificada
            return str(soup)
        else:
            return f"Error al acceder al panel de administración: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/bypass/dashboard')
def bypass_dashboard():
    try:
        # Obtener la página de dashboard de usuario
        response = requests.get(USER_URL)
        if response.status_code == 200:
            # Modificar los enlaces para que apunten a la aplicación principal
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a'):
                if a.get('href') and a.get('href').startswith('/'):
                    a['href'] = f"{BASE_URL}{a['href']}"
            
            # Devolver la página modificada
            return str(soup)
        else:
            return f"Error al acceder al dashboard de usuario: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/bypass/catalogs')
def bypass_catalogs():
    try:
        # Obtener la página de catálogos
        response = requests.get(CATALOGS_URL)
        if response.status_code == 200:
            # Modificar los enlaces para que apunten a la aplicación principal
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a'):
                if a.get('href') and a.get('href').startswith('/'):
                    a['href'] = f"{BASE_URL}{a['href']}"
            
            # Devolver la página modificada
            return str(soup)
        else:
            return f"Error al acceder a los catálogos: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/bypass/proxy', methods=['GET', 'POST'])
def proxy():
    
    if request.method == 'GET':
        url = request.args.get('url')
        if not url:
            return "Error: URL no especificada"
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a'):
                if a.get('href') and a.get('href').startswith('/'):
                    a['href'] = f"/bypass/proxy?url={BASE_URL}{a['href']}"
            
            return str(soup)
        except Exception as e:
            return f"Error al acceder a {url}: {str(e)}"
    else:
        # Manejar solicitudes POST
        url = request.form.get('url')
        if not url:
            return "Error: URL no especificada"
        
        try:
            response = requests.post(url, data=request.form)
            return response.text
        except Exception as e:
            return f"Error al enviar datos a {url}: {str(e)}"

if __name__ == '__main__':
    print("Bypass Login iniciado en http://127.0.0.1:5004")
    print("Accede a http://127.0.0.1:5004 para seleccionar la sección a la que quieres acceder")
    app.run(host='127.0.0.1', port=5004, debug=True)
"""
        
        with open(ruta_archivo, 'w') as f:
            f.write(contenido)
        
        logger.info(f"✅ Script de bypass login creado: {ruta_archivo}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear script de bypass login: {str(e)}")
        return False

def main():
    """Función principal que ejecuta la corrección de enlaces."""
    logger.info("Iniciando corrección de enlaces...")
    
    try:
        # 1. Crear script de acceso simple
        acceso_simple_ok = crear_script_acceso_simple()
        
        # 2. Modificar plantilla del panel de administración
        admin_ok = modificar_plantilla_admin()
        
        # 3. Modificar plantilla del dashboard de usuario
        dashboard_ok = modificar_plantilla_dashboard_user()
        
        # 4. Crear script de bypass login
        bypass_ok = crear_script_bypass_login()
        
        # Resumen
        logger.info("\n=== RESUMEN DE LA CORRECCIÓN DE ENLACES ===")
        logger.info(f"1. Script de acceso simple: {'✅ Creado' if acceso_simple_ok else '❌ No creado'}")
        logger.info(f"2. Plantilla del panel de administración: {'✅ Modificada' if admin_ok else '❌ No modificada'}")
        logger.info(f"3. Plantilla del dashboard de usuario: {'✅ Modificada' if dashboard_ok else '❌ No modificada'}")
        logger.info(f"4. Script de bypass login: {'✅ Creado' if bypass_ok else '❌ No creado'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Inicia el script de acceso simple:")
        logger.info("   $ python3 acceso_simple.py")
        logger.info("3. O inicia el script de bypass login (más completo):")
        logger.info("   $ python3 bypass_login.py")
        logger.info("4. Accede a http://127.0.0.1:5003 o http://127.0.0.1:5004 para seleccionar la sección a la que quieres acceder")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante la corrección de enlaces: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
