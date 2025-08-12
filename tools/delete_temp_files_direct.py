#!/usr/bin/env python3
"""
Script directo para eliminar archivos temporales de Google Drive
"""

import os
import sys
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configuración
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_NAME = 'Backups_CatalogoTablas'

def get_google_drive_service():
    """Obtiene el servicio de Google Drive."""
    creds = None
    creds_file = os.path.join(os.path.dirname(__file__), 'production/db_utils/credentials.json')
    token_file = os.path.join(os.path.dirname(__file__), 'production/db_utils/token.pickle')
    
    # Cargar credenciales si existen
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas, autenticar
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar credenciales para la próxima vez
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def get_folder_id(service, folder_name):
    """Obtiene el ID de la carpeta de backups."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    if items:
        return items[0]['id']
    return None

def list_temp_files(service, folder_id):
    """Lista archivos temporales en la carpeta."""
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, size, createdTime)").execute()
    files = results.get('files', [])
    
    temp_files = []
    for file_info in files:
        filename = file_info['name']
        if (filename.startswith('tmp') or 
            filename.startswith('backup_temp_') or
            'tmp' in filename.lower()):
            temp_files.append({
                'id': file_info['id'],
                'name': filename,
                'size': int(file_info.get('size', 0)),
                'created': file_info.get('createdTime', '')
            })
    
    return temp_files

def delete_temp_files():
    """Elimina archivos temporales de Google Drive."""
    try:
        print("🧹 Iniciando limpieza de archivos temporales en Google Drive...")
        
        # Obtener servicio de Google Drive
        service = get_google_drive_service()
        
        # Obtener ID de la carpeta
        folder_id = get_folder_id(service, FOLDER_NAME)
        if not folder_id:
            print(f"❌ No se encontró la carpeta '{FOLDER_NAME}'")
            return
        
        # Listar archivos temporales
        temp_files = list_temp_files(service, folder_id)
        
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
                service.files().delete(fileId=temp_file['id']).execute()
                deleted_count += 1
                print(f"✅ Eliminado: {temp_file['name']}")
            except Exception as e:
                print(f"❌ Error eliminando {temp_file['name']}: {e}")
        
        print(f"\n🎉 Limpieza completada: {deleted_count}/{len(temp_files)} archivos eliminados.")
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")

def list_temp_files_only():
    """Solo lista archivos temporales sin eliminarlos."""
    try:
        print("🔍 Buscando archivos temporales en Google Drive...")
        
        # Obtener servicio de Google Drive
        service = get_google_drive_service()
        
        # Obtener ID de la carpeta
        folder_id = get_folder_id(service, FOLDER_NAME)
        if not folder_id:
            print(f"❌ No se encontró la carpeta '{FOLDER_NAME}'")
            return
        
        # Listar archivos temporales
        temp_files = list_temp_files(service, folder_id)
        
        if not temp_files:
            print("✅ No se encontraron archivos temporales.")
            return
        
        print(f"📋 Encontrados {len(temp_files)} archivos temporales:")
        print("-" * 80)
        for temp_file in temp_files:
            size_mb = temp_file['size'] / (1024 * 1024) if temp_file['size'] else 0
            print(f"📄 {temp_file['name']}")
            print(f"   Tamaño: {size_mb:.2f} MB")
            print(f"   ID: {temp_file['id']}")
            print(f"   Fecha: {temp_file['created']}")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error listando archivos temporales: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_temp_files_only()
    else:
        delete_temp_files()
