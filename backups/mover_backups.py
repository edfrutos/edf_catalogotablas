#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para mover todos los archivos de backup al directorio /backups.
Basado en organizar_archivos.py pero enfocado solo en archivos de backup.
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
        logging.FileHandler('mover_backups.log'),
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
    r'^.*\.bak$',
    r'^.*\.bak\.\d+$',  # Para archivos como .bak.1, .bak.2, etc.
    r'^.*\.backup$',
    r'^.*\.old$',
    r'^.*\.back$',
    r'^.*_backup.*$',
    r'^backup_.*$',
    r'^.*_old$',
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
    'backups'  # Excluimos el propio directorio de backups
]

def is_backup_file(filename):
    """Determina si un archivo es un archivo de backup basado en su nombre."""
    for pattern in BACKUP_PATTERNS:
        if re.match(pattern, os.path.basename(filename)):
            return True
    return False

def should_exclude_dir(dirpath):
    """Determina si un directorio debe ser excluido de la búsqueda."""
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in dirpath.split(os.path.sep):
            return True
    return False

def mover_backups():
    """Mueve todos los archivos de backup al directorio /backups."""
    backup_files_moved = 0
    errors = 0

    # Crear un timestamp para el informe y para archivos duplicados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.info(f"Iniciando búsqueda de archivos de backup desde: {BASE_DIR}")
    logger.info(f"Directorio destino: {BACKUPS_DIR}")
    
    # Recorrer todos los archivos en el directorio base
    for root, dirs, files in os.walk(BASE_DIR):
        # Excluir directorios que no queremos procesar
        if should_exclude_dir(root):
            logger.debug(f"Directorio excluido: {root}")
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
    print("Iniciando búsqueda y movimiento de archivos de backup...")
    results = mover_backups()
    print(f"\nResumen:")
    print(f"- Archivos de backup movidos: {results['backup_files_moved']}")
    print(f"- Errores encontrados: {results['errors']}")
    print("\nProceso completado. Consulta el archivo 'mover_backups.log' para más detalles.")
