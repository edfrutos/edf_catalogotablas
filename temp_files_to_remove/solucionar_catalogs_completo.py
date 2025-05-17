#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
import traceback
from pymongo import MongoClient
from bson.objectid import ObjectId
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

def verificar_plantillas():
    """Verifica y corrige las plantillas necesarias para los catálogos."""
    templates_dir = "app/templates"
    plantillas_requeridas = {
        "catalogs.html": """{% extends "base.html" %}
{% block title %}Catálogos{% endblock %}
{% block content %}
<div class="container mt-4">
    <h1>Catálogos</h1>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <div class="row mb-4">
        <div class="col-md-12">
            <a href="{{ url_for('catalogs.create') }}" class="btn btn-primary">
                <i class="fas fa-plus"></i> Crear Nuevo Catálogo
            </a>
        </div>
    </div>
    
    {% if catalogs %}
        <div class="row">
            {% for catalog in catalogs %}
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="card-title mb-0">{{ catalog.name }}</h5>
                        </div>
                        <div class="card-body">
                            <p class="card-text">
                                <strong>Filas:</strong> {{ catalog.row_count }}
                            </p>
                            <p class="card-text">
                                <strong>Columnas:</strong> {{ catalog.headers|length }}
                            </p>
                        </div>
                        <div class="card-footer">
                            <a href="{{ url_for('catalogs.view', catalog_id=catalog._id_str) }}" class="btn btn-primary btn-sm">
                                <i class="fas fa-eye"></i> Ver
                            </a>
                            <a href="{{ url_for('catalogs.edit', catalog_id=catalog._id_str) }}" class="btn btn-secondary btn-sm">
                                <i class="fas fa-edit"></i> Editar
                            </a>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% else %}
        <div class="alert alert-info">
            No hay catálogos disponibles. Crea uno para comenzar.
        </div>
    {% endif %}
</div>
{% endblock %}""",
        
        "ver_catalogo.html": """{% extends "base.html" %}

{% block title %}Ver Catálogo{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row justify-content-center">
        <div class="col-md-10">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h2 class="mb-0">{{ catalog.name }}</h2>
                    <div>
                        <a href="{{ url_for('catalogs.edit', catalog_id=catalog._id) }}" class="btn btn-primary">
                            <i class="fas fa-edit"></i> Editar
                        </a>
                        <a href="{{ url_for('catalogs.list') }}" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i> Volver
                        </a>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <h5>Información General</h5>
                            <p><strong>Descripción:</strong> {{ catalog.description }}</p>
                            <p><strong>Estado:</strong> 
                                <span class="badge bg-success">Activo</span>
                            </p>
                            <p><strong>Fecha de creación:</strong> {% if catalog.created_at %}{{ catalog.created_at.strftime('%d/%m/%Y %H:%M') }}{% else %}No disponible{% endif %}</p>
                            <p><strong>Última actualización:</strong> {% if catalog.updated_at %}{{ catalog.updated_at.strftime('%d/%m/%Y %H:%M') }}{% else %}No disponible{% endif %}</p>
                        </div>
                        <div class="col-md-6">
                            <h5>Estadísticas</h5>
                            <p><strong>Total de filas:</strong> {{ catalog.rows|length }}</p>
                            <p><strong>Columnas:</strong> {{ catalog.headers|length }}</p>
                        </div>
                    </div>

                    <h5 class="mb-3">Filas del Catálogo</h5>
                    {% if catalog.rows %}
                        <div class="table-responsive">
                            <table class="table table-bordered table-hover mt-4">
                                <thead>
                                    <tr>
                                        {% for header in catalog.headers %}
                                        <th>{{ header }}</th>
                                        {% endfor %}
                                        <th>Imágenes</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for row in catalog.rows %}
                                    <tr>
                                        {% for header in catalog.headers %}
                                        <td>{{ row[header] }}</td>
                                        {% endfor %}
                                        <td>
                                            {% if row.imagenes and row.imagenes|length > 0 %}
                                                <div class="d-flex flex-wrap gap-2">
                                                    {% for img in row.imagenes %}
                                                        <a href="{{ url_for('static', filename='uploads/' ~ img) }}" target="_blank">
                                                            <img src="{{ url_for('static', filename='uploads/' ~ img) }}" alt="Imagen" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; border: 1px solid #ccc;">
                                                </a>
                                                {% endfor %}
                                            </div>
                                            {% else %}
                                                <span class="text-muted">Sin imágenes</span>
                                            {% endif %}
                                        </td>
                                        <td>
                                            <div class="btn-group" role="group">
                                                <a href="{{ url_for('catalogs.edit_row', catalog_id=catalog._id, row_index=loop.index0) }}" class="btn btn-sm btn-primary">
                                                    <i class="fas fa-edit"></i> Editar
                                                </a>
                                                <button class="btn btn-sm btn-danger" onclick="eliminarFila('{{ loop.index0 }}')">
                                                    <i class="fas fa-trash"></i> Eliminar
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    {% else %}
                        <div class="alert alert-info">
                            No hay filas en este catálogo.
                        </div>
                    {% endif %}

                    <div class="mt-4">
                        <a href="{{ url_for('catalogs.add_row', catalog_id=catalog._id) }}" class="btn btn-success">
                            <i class="fas fa-plus"></i> Agregar Fila
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal de confirmación para eliminar fila -->
<div class="modal fade" id="eliminarModal" tabindex="-1" aria-labelledby="eliminarModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="eliminarModalLabel">Confirmar Eliminación</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                ¿Está seguro que desea eliminar esta fila? Esta acción no se puede deshacer.
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <form id="eliminarForm" method="POST" class="d-inline">
                    <button type="submit" class="btn btn-danger">Eliminar</button>
                </form>
            </div>
        </div>
    </div>
</div>

{% endblock %}

{% block scripts %}
<script>
function eliminarFila(rowIndex) {
    const modal = new bootstrap.Modal(document.getElementById('eliminarModal'));
    const form = document.getElementById('eliminarForm');
    const baseUrl = "{{ url_for('catalogs.delete_row', catalog_id=catalog._id, row_index=0) }}";
    form.action = baseUrl.replace(/0$/, rowIndex);
    modal.show();
}
</script>
{% endblock %}""",
        
        "editar_catalogo.html": """{% extends "base.html" %}
{% block title %}Editar Catálogo{% endblock %}
{% block content %}
<div class="container mt-4">
    <h1>Editar Catálogo</h1>
    <form method="post">
        <div class="mb-3">
            <label for="name" class="form-label">Nombre del Catálogo</label>
            <input type="text" class="form-control" id="name" name="name" value="{{ catalog.name }}" required>
        </div>
        <div class="mb-3">
            <label for="headers" class="form-label">Encabezados (separados por comas)</label>
            <input type="text" class="form-control" id="headers" name="headers" value="{{ catalog.headers|join(', ') }}" required>
        </div>
        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
        <a href="{{ url_for('catalogs.view', catalog_id=catalog._id) }}" class="btn btn-secondary">Cancelar</a>
    </form>
</div>
{% endblock %}""",
        
        "agregar_fila.html": """{% extends "base.html" %}
{% block title %}Agregar Fila{% endblock %}
{% block content %}
<div class="container mt-4">
    <h1>Agregar Fila a "{{ catalog.name }}"</h1>
    <form method="post" enctype="multipart/form-data">
        {% for header in catalog.headers %}
        <div class="mb-3">
            <label for="{{ header }}" class="form-label">{{ header }}</label>
            <input type="text" class="form-control" id="{{ header }}" name="{{ header }}">
        </div>
        {% endfor %}
        <div class="mb-3">
            <label for="imagenes" class="form-label">Imágenes (opcional)</label>
            <input type="file" class="form-control" id="imagenes" name="imagenes" multiple accept="image/*">
            <div class="form-text">Puede seleccionar múltiples imágenes.</div>
        </div>
        <button type="submit" class="btn btn-primary">Guardar</button>
        <a href="{{ url_for('catalogs.view', catalog_id=catalog._id) }}" class="btn btn-secondary">Cancelar</a>
    </form>
</div>
{% endblock %}""",
        
        "editar_fila.html": """{% extends "base.html" %}
{% block title %}Editar Fila{% endblock %}
{% block content %}
<div class="container mt-4">
    <h1>Editar Fila de "{{ catalog.name }}"</h1>
    <form method="post" enctype="multipart/form-data">
        {% for header in headers %}
        <div class="mb-3">
            <label for="{{ header }}" class="form-label">{{ header }}</label>
            <input type="text" class="form-control" id="{{ header }}" name="{{ header }}" value="{{ fila[header] }}">
        </div>
        {% endfor %}
        <div class="mb-3">
            <label for="imagenes" class="form-label">Imágenes (opcional)</label>
            <input type="file" class="form-control" id="imagenes" name="imagenes" multiple accept="image/*">
            <div class="form-text">Puede seleccionar múltiples imágenes. Si sube nuevas imágenes, reemplazarán a las existentes.</div>
        </div>
        {% if fila.imagenes and fila.imagenes|length > 0 %}
        <div class="mb-3">
            <label class="form-label">Imágenes actuales</label>
            <div class="d-flex flex-wrap gap-2">
                {% for img in fila.imagenes %}
                <div class="position-relative">
                    <img src="{{ url_for('static', filename='uploads/' ~ img) }}" alt="Imagen" style="width: 100px; height: 100px; object-fit: cover; border-radius: 4px; border: 1px solid #ccc;">
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
        <a href="{{ url_for('catalogs.view', catalog_id=catalog._id) }}" class="btn btn-secondary">Cancelar</a>
    </form>
</div>
{% endblock %}"""
    }
    
    plantillas_encontradas = []
    plantillas_creadas = []
    
    for plantilla, contenido in plantillas_requeridas.items():
        ruta_plantilla = os.path.join(templates_dir, plantilla)
        if os.path.exists(ruta_plantilla):
            plantillas_encontradas.append(plantilla)
            # Hacer backup de la plantilla existente
            backup_path = f"{ruta_plantilla}.bak"
            shutil.copy2(ruta_plantilla, backup_path)
            logger.info(f"✅ Backup creado para {plantilla}")
            
            # Reemplazar la plantilla con la versión corregida
            with open(ruta_plantilla, 'w') as f:
                f.write(contenido)
            logger.info(f"✅ Plantilla {plantilla} actualizada")
        else:
            # Crear la plantilla si no existe
            os.makedirs(os.path.dirname(ruta_plantilla), exist_ok=True)
            with open(ruta_plantilla, 'w') as f:
                f.write(contenido)
            plantillas_creadas.append(plantilla)
            logger.info(f"✅ Plantilla {plantilla} creada")
    
    return plantillas_encontradas, plantillas_creadas

def corregir_rutas_catalogs():
    """Corrige las rutas en el archivo catalogs_routes.py."""
    catalogs_routes_path = "app/routes/catalogs_routes.py"
    
    try:
        # Leer el archivo original
        with open(catalogs_routes_path, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{catalogs_routes_path}.bak"
        with open(backup_path, 'w') as f:
            f.write(contenido)
        logger.info(f"✅ Backup creado para {catalogs_routes_path}")
        
        # Correcciones a realizar
        correcciones = [
            # Corregir la ruta de la plantilla en la función edit
            ("return render_template(\"admin/editar_catalogo.html\", catalog=catalog, session=session)", 
             "return render_template(\"editar_catalogo.html\", catalog=catalog, session=session)"),
            
            # Asegurarse de que las rutas de delete_row y delete_catalog estén implementadas correctamente
            ("def delete_row(catalog_id, row_index, catalog):\n    if not is_mongo_available():\n        flash(\"Error de conexión a la base de datos.\", \"danger\")\n        return redirect(url_for(\"catalogs.view\", catalog_id=catalog_id))\n    return redirect(url_for(\"catalogs.view\", catalog_id=catalog_id))",
             "def delete_row(catalog_id, row_index, catalog):\n    if not is_mongo_available():\n        flash(\"Error de conexión a la base de datos.\", \"danger\")\n        return redirect(url_for(\"catalogs.view\", catalog_id=catalog_id))\n    try:\n        # Eliminar la fila del catálogo\n        mongo.db.catalogs.update_one(\n            {\"_id\": ObjectId(catalog_id)},\n            {\"$pull\": {\"rows\": catalog[\"rows\"][row_index]}}\n        )\n        flash(\"Fila eliminada correctamente\", \"success\")\n    except Exception as e:\n        current_app.logger.error(f\"Error al eliminar fila: {str(e)}\")\n        flash(f\"Error al eliminar fila: {str(e)}\", \"danger\")\n    return redirect(url_for(\"catalogs.view\", catalog_id=catalog_id))"),
            
            ("def delete_catalog(catalog_id, catalog):\n    if not is_mongo_available():\n        flash(\"Error de conexión a la base de datos.\", \"danger\")\n        return redirect(url_for(\"catalogs.list\"))\n    return redirect(url_for(\"catalogs.list\"))",
             "def delete_catalog(catalog_id, catalog):\n    if not is_mongo_available():\n        flash(\"Error de conexión a la base de datos.\", \"danger\")\n        return redirect(url_for(\"catalogs.list\"))\n    try:\n        # Eliminar el catálogo\n        mongo.db.catalogs.delete_one({\"_id\": ObjectId(catalog_id)})\n        flash(\"Catálogo eliminado correctamente\", \"success\")\n    except Exception as e:\n        current_app.logger.error(f\"Error al eliminar catálogo: {str(e)}\")\n        flash(f\"Error al eliminar catálogo: {str(e)}\", \"danger\")\n    return redirect(url_for(\"catalogs.list\"))")
        ]
        
        # Aplicar correcciones
        contenido_corregido = contenido
        for original, correccion in correcciones:
            contenido_corregido = contenido_corregido.replace(original, correccion)
        
        # Guardar el archivo corregido
        with open(catalogs_routes_path, 'w') as f:
            f.write(contenido_corregido)
        
        logger.info(f"✅ Rutas corregidas en {catalogs_routes_path}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al corregir rutas: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def corregir_permisos_catalogs(db):
    """Corrige los problemas de permisos en la colección catalogs."""
    # 1. Asegurarse de que todos los documentos tengan el campo created_by
    docs_sin_created_by = list(db.catalogs.find({"created_by": {"$exists": False}}))
    
    if docs_sin_created_by:
        logger.info(f"Corrigiendo {len(docs_sin_created_by)} documentos sin created_by...")
        
        for doc in docs_sin_created_by:
            db.catalogs.update_one(
                {"_id": doc["_id"]},
                {"$set": {"created_by": "admin@example.com"}}
            )
        logger.info("✅ Documentos actualizados con created_by")
    else:
        logger.info("✅ Todos los documentos tienen el campo created_by")
    
    # 2. Verificar si hay catálogos sin filas (rows)
    docs_sin_rows = list(db.catalogs.find({"rows": {"$exists": False}}))
    
    if docs_sin_rows:
        logger.info(f"Corrigiendo {len(docs_sin_rows)} documentos sin el campo rows...")
        
        for doc in docs_sin_rows:
            db.catalogs.update_one(
                {"_id": doc["_id"]},
                {"$set": {"rows": []}}
            )
        logger.info("✅ Documentos actualizados con el campo rows")
    else:
        logger.info("✅ Todos los documentos tienen el campo rows")
    
    # 3. Verificar si hay catálogos sin headers
    docs_sin_headers = list(db.catalogs.find({"headers": {"$exists": False}}))
    
    if docs_sin_headers:
        logger.info(f"Corrigiendo {len(docs_sin_headers)} documentos sin el campo headers...")
        
        for doc in docs_sin_headers:
            # Asignar headers predeterminados
            db.catalogs.update_one(
                {"_id": doc["_id"]},
                {"$set": {"headers": ["Número", "Descripción", "Valor"]}}
            )
        logger.info("✅ Documentos actualizados con el campo headers")
    else:
        logger.info("✅ Todos los documentos tienen el campo headers")
    
    return True

def crear_catalogo_prueba(db):
    """Crea un catálogo de prueba si no existe."""
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
        return True
    else:
        logger.info("ℹ️ El catálogo de prueba ya existe")
        return False

def main():
    """Función principal que ejecuta la corrección completa."""
    logger.info("Iniciando solución completa para los catálogos...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # 1. Verificar y corregir plantillas
        plantillas_encontradas, plantillas_creadas = verificar_plantillas()
        
        # 2. Corregir rutas en catalogs_routes.py
        rutas_corregidas = corregir_rutas_catalogs()
        
        # 3. Corregir permisos en catalogs
        permisos_corregidos = corregir_permisos_catalogs(db)
        
        # 4. Crear catálogo de prueba
        catalogo_creado = crear_catalogo_prueba(db)
        
        # Resumen
        logger.info("\n=== RESUMEN DE LA SOLUCIÓN COMPLETA ===")
        logger.info(f"1. Plantillas encontradas: {plantillas_encontradas}")
        logger.info(f"2. Plantillas creadas/actualizadas: {plantillas_creadas}")
        logger.info(f"3. Rutas corregidas: {'✅ Sí' if rutas_corregidas else '❌ No'}")
        logger.info(f"4. Permisos corregidos: {'✅ Sí' if permisos_corregidos else '❌ No'}")
        logger.info(f"5. Catálogo de prueba: {'✅ Creado' if catalogo_creado else 'ℹ️ Ya existía'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Accede a la aplicación en http://127.0.0.1:8002")
        logger.info("3. Inicia sesión con credenciales de administrador:")
        logger.info("   - Email: admin@example.com")
        logger.info("   - Contraseña: admin123")
        logger.info("4. Navega a http://127.0.0.1:8002/catalogs para ver los catálogos")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante la solución completa: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    
    finally:
        if client:
            client.close()
            logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
