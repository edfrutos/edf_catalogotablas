#!/usr/bin/env python3
"""
Gestor de imágenes inteligente que usa S3 como almacenamiento principal
y local como fallback para optimizar rendimiento y costos.
"""

import os
import logging
from typing import Optional, Dict, Any
from flask import current_app, url_for
from .s3_utils import get_s3_client, upload_file_to_s3, get_s3_url, delete_file_from_s3

logger = logging.getLogger(__name__)

class ImageManager:
    """Gestor inteligente de imágenes con S3 como principal y local como fallback"""
    
    def __init__(self):
        self.s3_bucket = os.environ.get('S3_BUCKET_NAME', 'edf-catalogo-tablas')
        self.aws_region = os.environ.get('AWS_REGION', 'eu-central-1')
        self.s3_client = get_s3_client()
        
    def _get_local_path(self):
        """Obtiene la ruta local de forma segura"""
        try:
            from flask import current_app
            return os.path.join(current_app.static_folder, 'imagenes_subidas')
        except:
            # Fallback si no hay contexto de aplicación
            return "/var/www/vhosts/edefrutos2025.xyz/httpdocs/app/static/imagenes_subidas"
        
    def get_image_url(self, image_name: str, use_s3: bool = True) -> str:
        """Obtiene la URL de una imagen, priorizando S3 si está disponible"""
        if not image_name:
            return self._get_placeholder_url()
            
        # Si se especifica usar S3 y está disponible
        if use_s3 and self.s3_client:
            try:
                # Intentar URL pública primero
                s3_url = get_s3_url(image_name, self.s3_bucket)
                
                # Si S3 no es público, usar URL firmada
                import requests
                response = requests.head(s3_url, timeout=5)
                if response.status_code == 403:
                    # S3 no es público, usar URL firmada
                    s3_url = self.s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': self.s3_bucket, 'Key': image_name},
                        ExpiresIn=3600  # 1 hora
                    )
                    print(f"      🔐 Usando URL firmada para: {image_name}")
                
                if s3_url:
                    return s3_url
            except Exception as e:
                print(f"      ⚠️  Error S3, usando local: {e}")
        
        # Fallback a local
        local_url = f"/imagenes_subidas/{image_name}"
        print(f"      📁 Usando URL local para: {image_name}")
        return local_url
    
    def upload_image(self, file_path: str, image_name: Optional[str] = None) -> Dict[str, Any]:
        """Sube una imagen a S3 y opcionalmente la guarda localmente como backup"""
        if not os.path.exists(file_path):
            return {'success': False, 'error': f"Archivo no encontrado: {file_path}"}
        
        # Generar nombre único si no se proporciona
        if not image_name:
            import uuid
            import hashlib
            file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            ext = os.path.splitext(file_path)[1]
            image_name = f"{file_hash}{ext}"
        
        result = {
            'success': False,
            'image_name': image_name,
            's3_url': None,
            'local_url': None,
            'error': None
        }
        
        # Intentar subir a S3
        if self.s3_client:
            s3_result = upload_file_to_s3(file_path, image_name, self.s3_bucket)
            if s3_result['success']:
                result['success'] = True
                result['s3_url'] = s3_result['url']
                logger.info(f"Imagen subida exitosamente a S3: {image_name}")
            else:
                result['error'] = f"Error S3: {s3_result['error']}"
                logger.warning(f"Error al subir a S3, usando local: {s3_result['error']}")
        
        # Si S3 falla o no está disponible, usar local
        if not result['success']:
            local_path = os.path.join(self._get_local_path(), image_name)
            try:
                import shutil
                shutil.copy2(file_path, local_path)
                result['success'] = True
                result['local_url'] = f"/imagenes_subidas/{image_name}"
                logger.info(f"Imagen guardada localmente: {image_name}")
            except Exception as e:
                result['error'] = f"Error local: {str(e)}"
                logger.error(f"Error al guardar imagen localmente: {str(e)}")
        
        return result
    
    def _get_placeholder_url(self) -> str:
        """Obtiene la URL de la imagen placeholder"""
        return url_for('static', filename='img/image-placeholder.png')

# Instancia global del gestor de imágenes
image_manager = ImageManager()

def get_image_url(image_name: str, use_s3: bool = True) -> str:
    """Función helper para obtener URL de imagen"""
    return image_manager.get_image_url(image_name, use_s3)

def upload_image(file_path: str, image_name: Optional[str] = None) -> Dict[str, Any]:
    """Función helper para subir imagen"""
    return image_manager.upload_image(file_path, image_name)
