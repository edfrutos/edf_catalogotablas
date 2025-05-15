#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para mover TODOS los archivos de backup al directorio /backups.
Versión mejorada que busca patrones más complejos y extensiones compuestas.
"""

import os
import shutil
import re
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mover_todos_backups.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Directorios base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUPS_DIR = os.path.join(BASE_DIR, 'backups')

# Asegurar que el directorio de backups existe
os.makedirs(BACKUPS_DIR, exist_ok=True)

# Patrones para identificar archivos de backup
BACKUP_PATTERNS = [
    r'^.*\.bak.*$',  # Cualquier archivo que contenga .bak en cualquier parte de la extensión
    r'^.*\.backup.*$',
    r'^.*\.old.*$',
    r'^.*\.back.*$',
    r'^.*_backup.*$',
    r'^backup_.*$',
    r'^.*_old.*$',
    r'^.*_copy.*$',
    r'^copy_of_.*$',
    r'^.*\.tmp$',
    r'^.*\.swp$',
    r'^.*~$'  # Archivos temporales de editores como vim
]

# Directorios a excluir de la búsqueda
EXCLUDE_DIRS = [
    '.git',
    '.venv',
    'venv',
    'env',
    'node_modules',
    'backups',  # Excluimos el propio directorio de backups
    '__pycache__'  # Excluimos directorios de caché de Python
]

def is_backup_file(filename):
    """Determina si un archivo es un archivo de backup basado en su nombre."""
    basename = os.path.basename(filename)
    
    # Verificar patrones específicos
    for pattern in BACKUP_PATTERNS:
        if re.match(pattern, basename):
            return True
    
    # Verificar extensiones compuestas (como .bak.funcionalidad)
    if '.bak.' in basename:
        return True
    
    # Verificar otras extensiones comunes de backup
    extensions = ['.bak', '.backup', '.old', '.back', '.tmp', '.swp', '~']
    for ext in extensions:
        if basename.endswith(ext):
            return True
    
    return False

def should_exclude_dir(dirpath):
    """Determina si un directorio debe ser excluido de la búsqueda."""
    path_parts = dirpath.split(os.path.sep)
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in path_parts:
            return True
    
    # También excluimos directorios que contengan 'test' en su nombre
    for part in path_parts:
        if 'test' in part.lower() and 'templates' not in part.lower():
            return True
    
    return False

def mover_backups():
    """Mueve todos los archivos de backup al directorio /backups."""
    backup_files_moved = 0
    errors = 0

    # Crear un timestamp para el informe y para archivos duplicados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.info(f"Iniciando búsqueda exhaustiva de archivos de backup desde: {BASE_DIR}")
    logger.info(f"Directorio destino: {BACKUPS_DIR}")
    
    # Recorrer todos los archivos en el directorio base
    for root, dirs, files in os.walk(BASE_DIR):
        # Excluir directorios que no queremos procesar
        if should_exclude_dir(root):
            continue
        
        for file in files:
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, BASE_DIR)
            
            # Procesar archivos de backup
            if is_backup_file(file):
                try:
                    # Crear un nombre de archivo único en el directorio de backups
                    # Mantenemos la estructura de directorios relativa
                    rel_dir = os.path.dirname(relpath)
                    target_dir = os.path.join(BACKUPS_DIR, rel_dir)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    target_path = os.path.join(BACKUPS_DIR, relpath)
                    if not os.path.exists(target_path):
                        shutil.move(filepath, target_path)
                        logger.info(f"Archivo de backup movido: {relpath} -> {target_path}")
                        backup_files_moved += 1
                    else:
                        # Si ya existe, crear una copia con timestamp
                        filename, ext = os.path.splitext(file)
                        # Si la extensión tiene más partes (como .bak.funcionalidad)
                        if '.' in filename:
                            base_name = os.path.basename(filename)
                            new_filename = f"{base_name}_{timestamp}{ext}"
                        else:
                            new_filename = f"{filename}_{timestamp}{ext}"
                        target_path = os.path.join(target_dir, new_filename)
                        shutil.copy2(filepath, target_path)
                        os.remove(filepath)
                        logger.info(f"Archivo de backup duplicado, copiado con timestamp: {relpath} -> {target_path}")
                        backup_files_moved += 1
                
                except Exception as e:
                    logger.error(f"Error al procesar {relpath}: {str(e)}")
                    errors += 1
    
    # Mostrar resumen
    logger.info(f"Proceso completado:")
    logger.info(f"- Archivos de backup movidos: {backup_files_moved}")
    logger.info(f"- Errores encontrados: {errors}")
    
    return {
        'backup_files_moved': backup_files_moved,
        'errors': errors
    }

if __name__ == "__main__":
    print("Iniciando búsqueda exhaustiva y movimiento de archivos de backup...")
    results = mover_backups()
    print(f"\nResumen:")
    print(f"- Archivos de backup movidos: {results['backup_files_moved']}")
    print(f"- Errores encontrados: {results['errors']}")
    print("\nProceso completado. Consulta el archivo 'mover_todos_backups.log' para más detalles.")
