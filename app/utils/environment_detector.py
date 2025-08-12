#!/usr/bin/env python3
"""
Módulo para detectar el entorno de ejecución y buscar scripts en directorios específicos
"""

import os
import socket
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class EnvironmentDetector:
    """
    Clase para detectar el entorno de ejecución y gestionar rutas de scripts
    """
    
    def __init__(self):
        self.environment = self._detect_environment()
        self.base_path = self._get_base_path()
        self.script_paths = self._get_script_paths()
        
    def _detect_environment(self) -> str:
        """
        Detecta si la aplicación está ejecutándose en desarrollo o producción
        """
        # Obtener la ruta absoluta del archivo actual
        current_file = os.path.abspath(__file__)
        
        # Detectar por ruta del archivo
        if '/Users/edefrutos/_Repositorios/' in current_file:
            return 'development'
        elif '/var/www/vhosts/edefrutos2025.xyz/httpdocs' in current_file:
            return 'production'
        
        # Detectar por hostname como respaldo
        hostname = socket.gethostname()
        if 'localhost' in hostname or '127.0.0.1' in hostname:
            return 'development'
        else:
            return 'production'
    
    def _get_base_path(self) -> str:
        """
        Obtiene la ruta base según el entorno detectado
        """
        if self.environment == 'development':
            return '/Users/edefrutos/_Repositorios/01.IDE_Cursor/edf_catalogotablas/branch_edf_catalogotablas/edf_catalogotablas'
        else:
            return '/var/www/vhosts/edefrutos2025.xyz/httpdocs'
    
    def _get_script_paths(self) -> Dict[str, str]:
        """
        Obtiene las rutas de los directorios de scripts según el entorno
        """
        base = self.base_path
        
        return {
            'scripts': os.path.join(base, 'scripts', self.environment),
            'tests': os.path.join(base, 'tests', self.environment),
            'tools': os.path.join(base, 'tools', self.environment),
            'maintenance': os.path.join(base, 'scripts', 'maintenance'),
            'utils': os.path.join(base, 'tools', 'utils'),
            'db_utils': os.path.join(base, 'tools', 'db_utils'),
            'admin_utils': os.path.join(base, 'tools', 'admin_utils'),
            'password_utils': os.path.join(base, 'tools', 'password_utils'),
            'image_utils': os.path.join(base, 'tools', 'image_utils'),
            'session_utils': os.path.join(base, 'tools', 'session_utils'),
            'monitoring': os.path.join(base, 'tools', 'monitoring'),
            'deployment': os.path.join(base, 'tools', 'deployment'),
        }
    
    def get_script_path(self, script_type: str, script_name: str) -> Optional[str]:
        """
        Obtiene la ruta completa de un script específico
        
        Args:
            script_type: Tipo de script ('scripts', 'tests', 'tools', etc.)
            script_name: Nombre del archivo del script
            
        Returns:
            Ruta completa del script si existe, None si no existe
        """
        if script_type not in self.script_paths:
            logger.warning(f"Tipo de script '{script_type}' no reconocido")
            return None
        
        script_dir = self.script_paths[script_type]
        script_path = os.path.join(script_dir, script_name)
        
        if os.path.exists(script_path):
            return script_path
        else:
            logger.warning(f"Script '{script_name}' no encontrado en '{script_dir}'")
            return None
    
    def list_available_scripts(self, script_type: str) -> List[str]:
        """
        Lista todos los scripts disponibles en un directorio específico
        
        Args:
            script_type: Tipo de script ('scripts', 'tests', 'tools', etc.)
            
        Returns:
            Lista de nombres de archivos disponibles
        """
        if script_type not in self.script_paths:
            logger.warning(f"Tipo de script '{script_type}' no reconocido")
            return []
        
        script_dir = self.script_paths[script_type]
        
        if not os.path.exists(script_dir):
            logger.warning(f"Directorio '{script_dir}' no existe")
            return []
        
        try:
            files = [f for f in os.listdir(script_dir) 
                    if os.path.isfile(os.path.join(script_dir, f))]
            return sorted(files)
        except Exception as e:
            logger.error(f"Error al listar scripts en '{script_dir}': {e}")
            return []
    
    def execute_script(self, script_type: str, script_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un script específico
        
        Args:
            script_type: Tipo de script ('scripts', 'tests', 'tools', etc.)
            script_name: Nombre del archivo del script
            *args: Argumentos posicionales para el script
            **kwargs: Argumentos nombrados para el script
            
        Returns:
            Diccionario con el resultado de la ejecución
        """
        script_path = self.get_script_path(script_type, script_name)
        
        if not script_path:
            return {
                'success': False,
                'error': f"Script '{script_name}' no encontrado en tipo '{script_type}'"
            }
        
        try:
            # Importar y ejecutar el script
            import importlib.util
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Si el módulo tiene una función main, ejecutarla
            if hasattr(module, 'main'):
                result = module.main(*args, **kwargs)
                return {
                    'success': True,
                    'result': result,
                    'script_path': script_path
                }
            else:
                return {
                    'success': True,
                    'result': 'Script ejecutado (sin función main)',
                    'script_path': script_path
                }
                
        except Exception as e:
            logger.error(f"Error ejecutando script '{script_path}': {e}")
            return {
                'success': False,
                'error': str(e),
                'script_path': script_path
            }
    
    def get_environment_info(self) -> Dict[str, Any]:
        """
        Obtiene información completa del entorno detectado
        
        Returns:
            Diccionario con información del entorno
        """
        return {
            'environment': self.environment,
            'base_path': self.base_path,
            'hostname': socket.gethostname(),
            'script_paths': self.script_paths,
            'current_file': os.path.abspath(__file__)
        }

# Instancia global del detector de entorno
env_detector = EnvironmentDetector()

def get_script_path(script_type: str, script_name: str) -> Optional[str]:
    """
    Función de conveniencia para obtener la ruta de un script
    """
    return env_detector.get_script_path(script_type, script_name)

def list_scripts(script_type: str) -> List[str]:
    """
    Función de conveniencia para listar scripts disponibles
    """
    return env_detector.list_available_scripts(script_type)

def execute_script(script_type: str, script_name: str, *args, **kwargs) -> Dict[str, Any]:
    """
    Función de conveniencia para ejecutar un script
    """
    return env_detector.execute_script(script_type, script_name, *args, **kwargs)

def get_environment() -> str:
    """
    Función de conveniencia para obtener el entorno actual
    """
    return env_detector.environment

def is_development() -> bool:
    """
    Función de conveniencia para verificar si está en desarrollo
    """
    return env_detector.environment == 'development'

def is_production() -> bool:
    """
    Función de conveniencia para verificar si está en producción
    """
    return env_detector.environment == 'production'
