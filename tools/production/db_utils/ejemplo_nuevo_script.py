#!/usr/bin/env python3
# Descripción: Script de ejemplo para demostrar el reconocimiento automático
# Autor: Sistema de Gestión de Scripts
# Fecha: 2025-08-11

import os
import sys
from datetime import datetime

def main():
    """
    Función principal del script de ejemplo
    """
    print("=== SCRIPT DE EJEMPLO - RECONOCIMIENTO AUTOMÁTICO ===")
    print(f"Fecha y hora: {datetime.now()}")
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    # Información del script
    print(f"\n📄 Información del script:")
    print(f"  Nombre: {os.path.basename(__file__)}")
    print(f"  Ruta: {os.path.abspath(__file__)}")
    print(f"  Tamaño: {os.path.getsize(__file__)} bytes")
    
    # Verificar permisos
    is_executable = os.access(__file__, os.X_OK)
    print(f"  Ejecutable: {'✅ Sí' if is_executable else '❌ No'}")
    
    print("\n✅ Este script será reconocido automáticamente por el sistema")
    print("🔄 Recarga la página del Gestor de Scripts para verlo")
    
    return {
        "status": "success",
        "message": "Script de ejemplo ejecutado correctamente",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    main()
