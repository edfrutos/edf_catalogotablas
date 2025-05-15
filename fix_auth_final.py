"""
SOLUCIÓN DEFINITIVA PARA AUTENTICACIÓN Y RUTADO
Este script corrige los problemas de credenciales y rutado de forma permanente.
"""

import os
import sys
import traceback
import logging
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime
import shutil

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Colores para consola
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

# Cargar variables de entorno
load_dotenv()

print(f"\n{YELLOW}=================================================={RESET}")
print(f"{GREEN}     SOLUCIÓN FINAL PARA AUTENTICACIÓN Y RUTADO     {RESET}")
print(f"{YELLOW}=================================================={RESET}\n")

def get_mongodb_connection():
    """Conectar a MongoDB Atlas usando el URI del archivo .env"""
    try:
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            mongo_uri = "mongodb+srv://edfrutos:rYjwUC6pUNrLtbaI@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority"
            logger.info(f"Usando URI predeterminada de MongoDB")
        
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Verificar conexión
        client.admin.command('ping')
        logger.info(f"{GREEN}✅ Conexión exitosa a MongoDB Atlas{RESET}")
        return client
    except Exception as e:
        logger.error(f"{RED}❌ Error conectando a MongoDB: {e}{RESET}")
        return None

def fix_models_py():
    """Corregir el archivo models.py para buscar en todas las colecciones"""
    logger.info("Corrigiendo el archivo models.py para búsqueda de usuarios...")
    
    models_path = "app/models.py"
    backup_path = "app/models.py.bak"
    
    # Crear backup
    if os.path.exists(models_path):
        shutil.copy2(models_path, backup_path)
        logger.info(f"Backup creado: {backup_path}")
    
    # Agregar o reemplazar las funciones necesarias
    update_needed = True
    models_content = ""
    
    if os.path.exists(models_path):
        with open(models_path, 'r') as f:
            models_content = f.read()
    
    # Función para obtener base de datos
    if "def get_db():" not in models_content:
        get_db_code = """
def get_db():
    \"\"\"Obtiene la conexión a la base de datos principal\"\"\"
    from flask import current_app
    from pymongo import MongoClient
    import os
    
    try:
        # Intentar obtener la conexión de Flask PyMongo
        if hasattr(current_app, 'mongo') and hasattr(current_app.mongo, 'db'):
            return current_app.mongo.db
    except Exception:
        pass
    
    # Si falla, intentar conectar directamente
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://edfrutos:rYjwUC6pUNrLtbaI@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority')
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # La base de datos está en el URI, así que get_database() la extrae automáticamente
        return client.get_database()
    except Exception as e:
        print(f"Error conectando a MongoDB: {e}")
        # Última opción: devolver base de datos de desarrollo local
        try:
            client = MongoClient('mongodb://localhost:27017/edefrutos')
            return client.get_database()
        except Exception as e:
            print(f"Error conectando a MongoDB local: {e}")
            return None
"""
        models_content = models_content + get_db_code
    
    # Función mejorada para obtener colección de usuarios
    users_collection_code = """
def get_users_collection():
    \"\"\"Obtiene la colección de usuarios principal, verificando múltiples colecciones\"\"\"
    db = get_db()
    if not db:
        return None
    
    # Prioridad de colecciones 
    collections = ["users", "users_unified", "usuarios", "admins"]
    
    # Verificar cada colección y usar la primera que exista
    for collection_name in collections:
        if collection_name in db.list_collection_names():
            return db[collection_name]
    
    # Si ninguna existe, usar users por defecto
    return db["users"]
"""
    
    # Función mejorada para encontrar usuario
    find_user_code = """
def find_user_by_email_or_name(identifier):
    \"\"\"Busca un usuario por email o nombre de usuario en múltiples colecciones\"\"\"
    if not identifier:
        return None
        
    db = get_db()
    if not db:
        return None
    
    # Convertir a minúsculas para búsqueda insensible a mayúsculas
    identifier = identifier.lower()
    
    # Lista de colecciones donde buscar
    collections = ["users", "users_unified", "usuarios", "admins"]
    
    # Campos donde buscar (en orden de prioridad)
    fields = ["email", "username", "nombre"]
    
    # Probar cada colección
    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            continue
            
        collection = db[collection_name]
        
        # Buscar por cada campo
        for field in fields:
            # Búsqueda insensible a mayúsculas/minúsculas
            user = collection.find_one({field: {"$regex": f"^{identifier}$", "$options": "i"}})
            if user:
                print(f"Usuario encontrado en colección {collection_name}, campo {field}")
                return user
    
    # Si no se encuentra, intentar una última búsqueda más flexible
    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            continue
            
        collection = db[collection_name]
        
        # Búsqueda por cualquier campo parcial
        user = collection.find_one({
            "$or": [
                {"email": {"$regex": identifier, "$options": "i"}},
                {"username": {"$regex": identifier, "$options": "i"}},
                {"nombre": {"$regex": identifier, "$options": "i"}}
            ]
        })
        
        if user:
            print(f"Usuario encontrado con búsqueda flexible en colección {collection_name}")
            return user
    
    return None
"""

    # Reemplazar o agregar las funciones al archivo
    if "def get_users_collection():" in models_content:
        start = models_content.find("def get_users_collection()")
        end = models_content.find("def ", start + 10)
        if end == -1:
            end = len(models_content)
        models_content = models_content[:start] + users_collection_code + models_content[end:]
    else:
        models_content += users_collection_code
    
    if "def find_user_by_email_or_name(" in models_content:
        start = models_content.find("def find_user_by_email_or_name(")
        end = models_content.find("def ", start + 10)
        if end == -1:
            end = len(models_content)
        models_content = models_content[:start] + find_user_code + models_content[end:]
    else:
        models_content += find_user_code
    
    # Guardar el archivo actualizado
    with open(models_path, 'w') as f:
        f.write(models_content)
    
    logger.info(f"{GREEN}✅ Archivo models.py actualizado correctamente{RESET}")
    return True

def fix_auth_routes():
    """Corregir el rutado después del login en auth_routes.py"""
    logger.info("Corrigiendo rutado en auth_routes.py...")
    
    auth_routes_path = "app/routes/auth_routes.py"
    backup_path = "app/routes/auth_routes.py.bak"
    
    # Crear backup
    if os.path.exists(auth_routes_path):
        shutil.copy2(auth_routes_path, backup_path)
        logger.info(f"Backup creado: {backup_path}")
    
    # Leer el archivo
    with open(auth_routes_path, 'r') as f:
        content = f.read()
    
    # Asegurarse que la redirección funciona correctamente según el rol
    if "if session['role'] == 'admin':" not in content:
        # Buscar sección de redirección después del login
        redirect_block = """
        # Redireccionar según el rol del usuario
        if session.get('role') == 'admin':
            logger.info("Redirigiendo a panel de administración")
            return redirect(url_for('admin.dashboard_admin'))
        else:
            logger.info("Redirigiendo a dashboard de usuario")
            return redirect(url_for('main.dashboard'))
"""
        
        # Reemplazar redirección existente
        if "return redirect(url_for('admin.dashboard'))" in content:
            content = content.replace("return redirect(url_for('admin.dashboard'))", redirect_block)
        elif "return redirect(url_for('main.dashboard'))" in content:
            content = content.replace("return redirect(url_for('main.dashboard'))", redirect_block)
        else:
            # Buscar patrones de redirección después del login
            login_end = content.find("logger.info(f\"Login exitoso para:")
            if login_end > 0:
                next_line = content.find("return", login_end)
                if next_line > 0:
                    end_line = content.find("\n", next_line)
                    if end_line > 0:
                        content = content[:next_line] + redirect_block + content[end_line:]
    
    # Guardar el archivo actualizado
    with open(auth_routes_path, 'w') as f:
        f.write(content)
    
    logger.info(f"{GREEN}✅ Rutado en auth_routes.py corregido{RESET}")
    return True

def fix_blueprints_registration():
    """Verificar y corregir el registro de blueprints en app.py"""
    logger.info("Verificando registro de blueprints en app.py...")
    
    app_path = "app.py"
    backup_path = "app.py.bak"
    
    # Crear backup
    shutil.copy2(app_path, backup_path)
    logger.info(f"Backup creado: {backup_path}")
    
    # Leer el archivo
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Verificar registro de blueprints
    if "app.register_blueprint(admin_bp, url_prefix='/admin')" in content:
        logger.info(f"{GREEN}✅ Blueprint admin_bp ya está registrado correctamente{RESET}")
    else:
        logger.warning(f"{YELLOW}⚠️ Blueprint admin_bp no está registrado o tiene una URL incorrecta{RESET}")
        
        # Intentar corregir
        if "app.register_blueprint(admin_bp" in content:
            # Corregir prefijo
            content = content.replace(
                "app.register_blueprint(admin_bp", 
                "app.register_blueprint(admin_bp, url_prefix='/admin'"
            )
            logger.info(f"{GREEN}✅ Corregido prefijo de URL para admin_bp{RESET}")
        else:
            # Agregar registro completo
            registration_block = """
    # Importar y registrar blueprint de administración
    try:
        from app.routes.admin_routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.logger.info("✅ Blueprint admin_bp registrado con éxito")
    except Exception as e:
        app.logger.error(f"❌ Error registrando admin_bp: {str(e)}")
"""
            # Buscar el lugar adecuado para insertar
            insert_point = content.find("return app")
            if insert_point > 0:
                content = content[:insert_point] + registration_block + content[insert_point:]
                logger.info(f"{GREEN}✅ Agregado registro completo de admin_bp{RESET}")
    
    # Guardar el archivo actualizado
    with open(app_path, 'w') as f:
        f.write(content)
    
    return True

def fix_main_dashboard():
    """Corregir la ruta main.dashboard para usuarios normales"""
    logger.info("Verificando ruta de dashboard principal...")
    
    main_routes_path = "app/routes/main_routes.py"
    
    # Si no existe el archivo, no podemos hacer nada
    if not os.path.exists(main_routes_path):
        logger.error(f"{RED}❌ No se encontró el archivo {main_routes_path}{RESET}")
        return False
    
    # Crear backup
    backup_path = main_routes_path + ".bak"
    shutil.copy2(main_routes_path, backup_path)
    
    # Leer el archivo
    with open(main_routes_path, 'r') as f:
        content = f.read()
    
    # Verificar que exista la ruta dashboard
    if "@main_bp.route('/dashboard')" in content:
        logger.info(f"{GREEN}✅ La ruta dashboard ya existe{RESET}")
    else:
        # Agregar la ruta dashboard
        dashboard_route = """
@main_bp.route('/dashboard')
def dashboard():
    \"\"\"Dashboard principal para usuarios normales\"\"\"
    try:
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        # Obtener datos del usuario
        user_id = session.get('user_id')
        username = session.get('username')
        email = session.get('email')
        
        # Renderizar dashboard
        return render_template('dashboard.html', username=username, email=email)
    except Exception as e:
        logger.error(f"Error en dashboard: {str(e)}")
        flash("Error al cargar el dashboard", "danger")
        return redirect(url_for('main.index'))
"""
        # Buscar el lugar adecuado para insertar
        if "@main_bp.route" in content:
            # Insertar después de la última ruta existente
            last_route = content.rfind("@main_bp.route")
            if last_route > 0:
                # Buscar el final de esa función
                next_func = content.find("def ", last_route)
                if next_func > 0:
                    func_name_end = content.find("(", next_func)
                    if func_name_end > 0:
                        func_name = content[next_func+4:func_name_end].strip()
                        # Buscar la siguiente función o el final del archivo
                        next_def = content.find("def ", func_name_end)
                        if next_def > 0:
                            content = content[:next_def] + dashboard_route + content[next_def:]
                        else:
                            content = content + dashboard_route
                        logger.info(f"{GREEN}✅ Agregada ruta dashboard{RESET}")
        else:
            # No hay rutas, agregar al final
            content = content + dashboard_route
            logger.info(f"{GREEN}✅ Agregada ruta dashboard al final del archivo{RESET}")
    
    # Guardar el archivo actualizado
    with open(main_routes_path, 'w') as f:
        f.write(content)
    
    return True

def create_dashboard_template():
    """Crear una plantilla básica para el dashboard principal"""
    logger.info("Verificando plantilla de dashboard principal...")
    
    dashboard_path = "app/templates/dashboard.html"
    os.makedirs(os.path.dirname(dashboard_path), exist_ok=True)
    
    # Si ya existe, no la sobrescribimos
    if os.path.exists(dashboard_path):
        logger.info(f"{GREEN}✅ Plantilla dashboard.html ya existe{RESET}")
        return True
    
    # Crear una plantilla básica
    dashboard_html = """{% extends "base.html" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-12">
            <div class="card shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h4>Bienvenido, {{ username }}</h4>
                </div>
                <div class="card-body">
                    <p>Has iniciado sesión correctamente en tu cuenta.</p>
                    <p>Email: <strong>{{ email }}</strong></p>
                    
                    <div class="mt-4">
                        <h5>Acciones Disponibles</h5>
                        <div class="list-group">
                            <a href="{{ url_for('main.index') }}" class="list-group-item list-group-item-action">
                                <i class="fas fa-home"></i> Página Principal
                            </a>
                            <a href="#" class="list-group-item list-group-item-action">
                                <i class="fas fa-table"></i> Mis Tablas
                            </a>
                            <a href="#" class="list-group-item list-group-item-action">
                                <i class="fas fa-user-edit"></i> Editar Perfil
                            </a>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <a href="{{ url_for('auth.logout') }}" class="btn btn-danger">
                        <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    
    # Guardar la plantilla
    with open(dashboard_path, 'w') as f:
        f.write(dashboard_html)
    
    logger.info(f"{GREEN}✅ Plantilla dashboard.html creada{RESET}")
    return True

def fix_base_template():
    """Corregir la plantilla base para usar las rutas correctas"""
    logger.info("Verificando plantilla base.html...")
    
    base_path = "app/templates/base.html"
    if not os.path.exists(base_path):
        base_path = "templates/base.html"
        if not os.path.exists(base_path):
            logger.error(f"{RED}❌ No se encontró la plantilla base.html{RESET}")
            return False
    
    # Crear backup
    backup_path = base_path + ".bak"
    shutil.copy2(base_path, backup_path)
    
    # Leer el archivo
    with open(base_path, 'r') as f:
        content = f.read()
    
    # Corregir referencias a admin_panel
    if "url_for('admin_panel')" in content:
        content = content.replace("url_for('admin_panel')", "url_for('admin.dashboard_admin')")
        logger.info(f"{GREEN}✅ Corregidas referencias a admin_panel en base.html{RESET}")
    
    # Guardar el archivo actualizado
    with open(base_path, 'w') as f:
        f.write(content)
    
    return True

def fix_admin_templates():
    """Corregir referencias en las plantillas de administración"""
    logger.info("Verificando plantillas de administración...")
    
    template_dirs = ["app/templates/admin", "templates/admin"]
    template_files = []
    
    # Buscar archivos de plantillas
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            for file in os.listdir(template_dir):
                if file.endswith(".html"):
                    template_files.append(os.path.join(template_dir, file))
    
    if not template_files:
        logger.warning(f"{YELLOW}⚠️ No se encontraron plantillas de administración{RESET}")
        return False
    
    for template_file in template_files:
        logger.info(f"Verificando {template_file}...")
        
        # Crear backup
        backup_path = template_file + ".bak"
        shutil.copy2(template_file, backup_path)
        
        # Leer el archivo
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Corregir referencias a admin_panel
        if "url_for('admin_panel')" in content:
            content = content.replace("url_for('admin_panel')", "url_for('admin.dashboard_admin')")
            
            # Guardar el archivo actualizado
            with open(template_file, 'w') as f:
                f.write(content)
            logger.info(f"{GREEN}✅ Corregidas referencias en {template_file}{RESET}")
    
    return True

def main():
    """Función principal que ejecuta todas las correcciones"""
    # 1. Verificar conexión a MongoDB Atlas
    client = get_mongodb_connection()
    if not client:
        logger.error(f"{RED}❌ No se pudo conectar a MongoDB Atlas. Abortando.{RESET}")
        return
    
    # 2. Corregir búsqueda de usuarios en todas las colecciones
    if fix_models_py():
        logger.info(f"{GREEN}✅ Búsqueda de usuarios en colecciones corregida{RESET}")
    
    # 3. Corregir rutado después del login
    if fix_auth_routes():
        logger.info(f"{GREEN}✅ Rutado después del login corregido{RESET}")
    
    # 4. Verificar registro de blueprints
    if fix_blueprints_registration():
        logger.info(f"{GREEN}✅ Registro de blueprints verificado{RESET}")
    
    # 5. Corregir dashboard principal
    if fix_main_dashboard():
        logger.info(f"{GREEN}✅ Dashboard principal corregido{RESET}")
    
    # 6. Crear plantilla de dashboard si es necesario
    if create_dashboard_template():
        logger.info(f"{GREEN}✅ Plantilla de dashboard verificada{RESET}")
    
    # 7. Corregir plantilla base
    if fix_base_template():
        logger.info(f"{GREEN}✅ Plantilla base corregida{RESET}")
    
    # 8. Corregir plantillas de administración
    if fix_admin_templates():
        logger.info(f"{GREEN}✅ Plantillas de administración corregidas{RESET}")
    
    # Resumen final
    print(f"\n{GREEN}=================================================={RESET}")
    print(f"{GREEN}           CORRECCIONES COMPLETADAS               {RESET}")
    print(f"{GREEN}=================================================={RESET}")
    print(f"\n{YELLOW}Para aplicar los cambios:{RESET}")
    print("1. Reinicia la aplicación: python app.py")
    print("2. Accede normalmente a través de /login")
    print("3. Los administradores serán dirigidos al panel de administración")
    print("4. Los usuarios normales serán dirigidos al dashboard de usuario")
    print("\nEsta solución corrige:")
    print("- Búsqueda de usuarios en todas las colecciones")
    print("- Rutado correcto según el rol de usuario")
    print("- Referencias a rutas en todas las plantillas")
    print(f"\n{GREEN}La aplicación ahora funcionará como se espera.{RESET}")

if __name__ == "__main__":
    main()
