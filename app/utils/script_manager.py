#!/usr/bin/env python3
"""
Módulo para gestionar scripts usando el detector de entorno
"""

import os
import logging
from typing import Optional, Dict, Any, List
from .environment_detector import env_detector, get_environment, is_development, is_production

logger = logging.getLogger(__name__)

class ScriptManager:
    """
    Clase para gestionar la ejecución de scripts según el entorno
    """
    
    def __init__(self):
        self.environment = get_environment()
        self.env_detector = env_detector
    
    def run_maintenance_script(self, script_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un script de mantenimiento
        
        Args:
            script_name: Nombre del script
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Resultado de la ejecución
        """
        logger.info(f"Ejecutando script de mantenimiento: {script_name}")
        return self.env_detector.execute_script('maintenance', script_name, *args, **kwargs)
    
    def run_db_script(self, script_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un script de base de datos
        
        Args:
            script_name: Nombre del script
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Resultado de la ejecución
        """
        logger.info(f"Ejecutando script de base de datos: {script_name}")
        return self.env_detector.execute_script('db_utils', script_name, *args, **kwargs)
    
    def run_utility_script(self, script_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un script de utilidades
        
        Args:
            script_name: Nombre del script
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Resultado de la ejecución
        """
        logger.info(f"Ejecutando script de utilidades: {script_name}")
        return self.env_detector.execute_script('utils', script_name, *args, **kwargs)
    
    def run_admin_script(self, script_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un script de administración
        
        Args:
            script_name: Nombre del script
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Resultado de la ejecución
        """
        logger.info(f"Ejecutando script de administración: {script_name}")
        return self.env_detector.execute_script('admin_utils', script_name, *args, **kwargs)
    
    def run_password_script(self, script_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un script de gestión de contraseñas
        
        Args:
            script_name: Nombre del script
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Resultado de la ejecución
        """
        logger.info(f"Ejecutando script de contraseñas: {script_name}")
        return self.env_detector.execute_script('password_utils', script_name, *args, **kwargs)
    
    def run_image_script(self, script_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un script de gestión de imágenes
        
        Args:
            script_name: Nombre del script
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Resultado de la ejecución
        """
        logger.info(f"Ejecutando script de imágenes: {script_name}")
        return self.env_detector.execute_script('image_utils', script_name, *args, **kwargs)
    
    def run_monitoring_script(self, script_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un script de monitoreo
        
        Args:
            script_name: Nombre del script
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Resultado de la ejecución
        """
        logger.info(f"Ejecutando script de monitoreo: {script_name}")
        return self.env_detector.execute_script('monitoring', script_name, *args, **kwargs)
    
    def get_available_scripts(self) -> Dict[str, List[str]]:
        """
        Obtiene todos los scripts disponibles organizados por tipo
        
        Returns:
            Diccionario con scripts disponibles por tipo
        """
        script_types = [
            'maintenance', 'db_utils', 'utils', 'admin_utils', 
            'password_utils', 'image_utils', 'monitoring', 'deployment'
        ]
        
        available_scripts = {}
        for script_type in script_types:
            scripts = self.env_detector.list_available_scripts(script_type)
            if scripts:
                available_scripts[script_type] = scripts
        
        return available_scripts
    
    def find_script(self, script_name: str) -> Optional[Dict[str, str]]:
        """
        Busca un script en todos los directorios disponibles
        
        Args:
            script_name: Nombre del script a buscar
            
        Returns:
            Diccionario con información del script si se encuentra, None si no
        """
        script_types = [
            'maintenance', 'db_utils', 'utils', 'admin_utils', 
            'password_utils', 'image_utils', 'monitoring', 'deployment'
        ]
        
        for script_type in script_types:
            script_path = self.env_detector.get_script_path(script_type, script_name)
            if script_path:
                return {
                    'script_type': script_type,
                    'script_name': script_name,
                    'script_path': script_path,
                    'environment': self.environment
                }
        
        return None
    
    def run_script_by_name(self, script_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un script buscándolo automáticamente en todos los directorios
        
        Args:
            script_name: Nombre del script
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Resultado de la ejecución
        """
        script_info = self.find_script(script_name)
        
        if not script_info:
            return {
                'success': False,
                'error': f"Script '{script_name}' no encontrado en ningún directorio"
            }
        
        logger.info(f"Ejecutando script '{script_name}' desde '{script_info['script_type']}'")
        return self.env_detector.execute_script(
            script_info['script_type'], 
            script_name, 
            *args, 
            **kwargs
        )

# Instancia global del gestor de scripts
script_manager = ScriptManager()

def run_maintenance_script(script_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Función de conveniencia para ejecutar scripts de mantenimiento"""
    return script_manager.run_maintenance_script(script_name, *args, **kwargs)

def run_db_script(script_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Función de conveniencia para ejecutar scripts de base de datos"""
    return script_manager.run_db_script(script_name, *args, **kwargs)

def run_utility_script(script_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Función de conveniencia para ejecutar scripts de utilidades"""
    return script_manager.run_utility_script(script_name, *args, **kwargs)

def run_admin_script(script_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Función de conveniencia para ejecutar scripts de administración"""
    return script_manager.run_admin_script(script_name, *args, **kwargs)

def run_password_script(script_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Función de conveniencia para ejecutar scripts de contraseñas"""
    return script_manager.run_password_script(script_name, *args, **kwargs)

def run_image_script(script_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Función de conveniencia para ejecutar scripts de imágenes"""
    return script_manager.run_image_script(script_name, *args, **kwargs)

def run_monitoring_script(script_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Función de conveniencia para ejecutar scripts de monitoreo"""
    return script_manager.run_monitoring_script(script_name, *args, **kwargs)

def find_script(script_name: str) -> Optional[Dict[str, str]]:
    """Función de conveniencia para buscar un script"""
    return script_manager.find_script(script_name)

def run_script_by_name(script_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Función de conveniencia para ejecutar un script por nombre"""
    return script_manager.run_script_by_name(script_name, *args, **kwargs)

def get_available_scripts() -> Dict[str, List[str]]:
    """Función de conveniencia para obtener scripts disponibles"""
    return script_manager.get_available_scripts()
