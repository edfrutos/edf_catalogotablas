#!/usr/bin/env python3
# Script de prueba simple para verificar la ejecución de scripts
# Este script imprime información sobre el entorno y devuelve un código de salida 0

import os
import sys
import platform
import datetime

def main():
    print("=== SCRIPT DE PRUEBA SIMPLE ===")
    print(f"Fecha y hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version}")
    print(f"Sistema operativo: {platform.system()} {platform.release()}")
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Ruta del script: {os.path.abspath(__file__)}")
    print(f"Usuario: {os.getenv('USER', 'desconocido')}")
    print(f"Variables de entorno PATH: {os.getenv('PATH', 'no disponible')}")
    print("=== FIN DE LA PRUEBA ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
