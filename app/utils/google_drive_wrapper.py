#!/usr/bin/env python3
"""
Wrapper para google_drive_utils usando el sistema de detección de entorno
"""

import sys
import os
from typing import Dict, Any, Optional, List, Union

def _get_google_drive_module():
    """Obtiene el módulo de google_drive_utils según el entorno"""
    from app.utils.environment_detector import get_environment
    
    environment = get_environment()
    
    if environment == 'production':
        module_path = 'tools/production/db_utils/google_drive_utils.py'
    else:
        module_path = 'tools/db_utils/google_drive_utils.py'
    
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"No se encontró google_drive_utils.py en {module_path}")
    
    # Importar el módulo dinámicamente
    import importlib.util
    spec = importlib.util.spec_from_file_location("google_drive_utils", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module

def get_drive():
    """Wrapper para get_drive()"""
    try:
        module = _get_google_drive_module()
        return module.get_drive()
    except Exception as e:
        raise Exception(f"Error obteniendo drive: {e}")

def upload_to_drive(file_path: str, folder_name: str = 'Backups_CatalogoTablas') -> Dict[str, Any]:
    """Wrapper para upload_to_drive()"""
    try:
        module = _get_google_drive_module()
        return module.upload_to_drive(file_path, folder_name)
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def list_files_in_folder(folder_name: str = 'Backups_CatalogoTablas') -> List[Dict[str, Any]]:
    """Wrapper para list_files_in_folder()"""
    try:
        module = _get_google_drive_module()
        return module.list_files_in_folder(folder_name)
    except Exception as e:
        raise Exception(f"Error listando archivos: {e}")

def download_file(file_id: str, output_path: Optional[str] = None) -> Union[bytes, str]:
    """Wrapper para download_file()"""
    try:
        module = _get_google_drive_module()
        return module.download_file(file_id, output_path)
    except Exception as e:
        raise Exception(f"Error descargando archivo: {e}")

def delete_file(file_id: str) -> bool:
    """Wrapper para delete_file()"""
    try:
        module = _get_google_drive_module()
        return module.delete_file(file_id)
    except Exception as e:
        raise Exception(f"Error eliminando archivo: {e}")

def get_or_create_folder(drive, folder_name: str) -> str:
    """Wrapper para get_or_create_folder()"""
    try:
        module = _get_google_drive_module()
        return module.get_or_create_folder(drive, folder_name)
    except Exception as e:
        raise Exception(f"Error creando/obteniendo carpeta: {e}")

def reset_gdrive_token() -> Dict[str, Any]:
    """Wrapper para reset_gdrive_token()"""
    try:
        module = _get_google_drive_module()
        return module.reset_gdrive_token()
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
