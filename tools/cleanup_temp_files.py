#!/usr/bin/env python3
"""
Script para limpiar archivos temporales de Google Drive
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position
from app.utils.backup_utils import GoogleDriveManager

def log_info(message):
    print(f"[INFO] {message}")

def log_error(message):
    print(f"[ERROR] {message}")

def log_warning(message):
    print(f"[WARNING] {message}")

def cleanup_temp_files():
    """Elimina archivos temporales de Google Drive."""
    try:
        print("🧹 Iniciando limpieza de archivos temporales en Google Drive...")
        
        # Inicializar Google Drive Manager
        drive_manager = GoogleDriveManager()
        
        # Listar todos los backups
        backups = drive_manager.list_backups()
        
        temp_files = []
        for backup in backups:
            filename = backup.get('name', '')
            file_id = backup.get('id', '')
            
            # Identificar archivos temporales
            if (filename.startswith('tmp') or
                    filename.startswith('backup_temp_') or
                    'tmp' in filename.lower()):
                temp_files.append({
                    'id': file_id,
                    'name': filename,
                    'size': backup.get('size', 0)
                })
        
        if not temp_files:
            print("✅ No se encontraron archivos temporales para eliminar.")
            return
        
        print(f"📋 Encontrados {len(temp_files)} archivos temporales:")
        for temp_file in temp_files:
            size_mb = temp_file['size'] / (1024 * 1024) if temp_file['size'] else 0
            print(f"   • {temp_file['name']} ({size_mb:.2f} MB) - ID: {temp_file['id']}")
        
        # Confirmar eliminación
        response = input(f"\n¿Deseas eliminar estos {len(temp_files)} archivos temporales? (s/N): ")
        if response.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada.")
            return
        
        # Eliminar archivos temporales
        deleted_count = 0
        for temp_file in temp_files:
            try:
                print(f"🗑️ Eliminando: {temp_file['name']}...")
                drive_manager.delete_file(temp_file['id'])
                deleted_count += 1
                print(f"✅ Eliminado: {temp_file['name']}")
            except Exception as e:
                print(f"❌ Error eliminando {temp_file['name']}: {e}")
        
        print(f"\n🎉 Limpieza completada: {deleted_count}/{len(temp_files)} archivos eliminados.")
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        log_error(f"Error en cleanup_temp_files: {e}")

def list_temp_files():
    """Lista archivos temporales sin eliminarlos."""
    try:
        print("🔍 Buscando archivos temporales en Google Drive...")
        
        # Inicializar Google Drive Manager
        drive_manager = GoogleDriveManager()
        
        # Listar todos los backups
        backups = drive_manager.list_backups()
        
        temp_files = []
        for backup in backups:
            filename = backup.get('name', '')
            file_id = backup.get('id', '')
            
            # Identificar archivos temporales
            if (filename.startswith('tmp') or
                    filename.startswith('backup_temp_') or
                    'tmp' in filename.lower()):
                temp_files.append({
                    'id': file_id,
                    'name': filename,
                    'size': backup.get('size', 0),
                    'created_date': backup.get('created_date', '')
                })
        
        if not temp_files:
            print("✅ No se encontraron archivos temporales.")
            return
        
        print(f"📋 Encontrados {len(temp_files)} archivos temporales:")
        print("-" * 80)
        for temp_file in temp_files:
            size_mb = temp_file['size'] / (1024 * 1024) if temp_file['size'] else 0
            created_date = temp_file.get('created_date', 'N/A')
            print(f"📄 {temp_file['name']}")
            print(f"   Tamaño: {size_mb:.2f} MB")
            print(f"   ID: {temp_file['id']}")
            print(f"   Fecha: {created_date}")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error listando archivos temporales: {e}")
        log_error(f"Error en list_temp_files: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_temp_files()
    else:
        cleanup_temp_files()
