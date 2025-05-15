#!/usr/bin/env python3
# Script para verificar la configuración actual de la aplicación Flask
# Ejecutar con: python verificar_configuracion.py

import os
import sys
import logging
from flask import Flask

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def verificar_configuracion():
    """Verifica la configuración actual de la aplicación Flask"""
    try:
        # Importar la aplicación Flask desde app.py
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import create_app
        app = create_app()
        
        # Mostrar información sobre la configuración de sesión
        print("\n\nCONFIGURACIÓN DE SESIÓN EN LA APLICACIÓN PRINCIPAL:")
        print("-" * 50)
        
        # Verificar configuración de sesión
        session_keys = [
            'SESSION_TYPE', 
            'SESSION_FILE_DIR', 
            'SESSION_COOKIE_NAME', 
            'SESSION_COOKIE_SECURE', 
            'SESSION_COOKIE_HTTPONLY', 
            'SESSION_COOKIE_SAMESITE',
            'SESSION_PERMANENT',
            'PERMANENT_SESSION_LIFETIME',
            'SESSION_REFRESH_EACH_REQUEST',
            'SESSION_USE_SIGNER',
            'SECRET_KEY'
        ]
        
        for key in session_keys:
            value = app.config.get(key, 'No configurado')
            if key == 'SECRET_KEY' and value != 'No configurado':
                value = '*' * len(str(value))
            print(f"{key}: {value}")
        
        # Verificar blueprints registrados
        print("\n\nBLUEPRINTS REGISTRADOS:")
        print("-" * 50)
        for name, blueprint in app.blueprints.items():
            print(f"Blueprint: {name}")
            print(f"  URL Prefix: {blueprint.url_prefix}")
            print(f"  Import Name: {blueprint.import_name}")
            print()
        
        # Verificar rutas de prueba de sesión
        print("\n\nRUTAS DE PRUEBA DE SESIÓN:")
        print("-" * 50)
        prueba_sesion_routes = [r for r in app.url_map.iter_rules() if 'prueba_sesion' in str(r)]
        if prueba_sesion_routes:
            for route in prueba_sesion_routes:
                print(f"  {route} -> {route.endpoint}")
        else:
            print("  No se encontraron rutas de prueba de sesión")
        
        test_session_routes = [r for r in app.url_map.iter_rules() if 'test_session' in str(r)]
        if test_session_routes:
            for route in test_session_routes:
                print(f"  {route} -> {route.endpoint}")
        
        # Verificar directorio de sesiones
        session_dir = app.config.get('SESSION_FILE_DIR', 'No configurado')
        if session_dir != 'No configurado':
            print("\n\nDIRECTORIO DE SESIONES:")
            print("-" * 50)
            if os.path.exists(session_dir):
                print(f"✅ El directorio de sesiones existe: {session_dir}")
                # Verificar permisos
                if os.access(session_dir, os.R_OK | os.W_OK):
                    print(f"✅ Permisos correctos en el directorio de sesiones")
                else:
                    print(f"⚠️ Permisos insuficientes en el directorio de sesiones")
                
                # Listar archivos de sesión
                archivos = os.listdir(session_dir)
                print(f"📁 Archivos de sesión encontrados: {len(archivos)}")
            else:
                print(f"❌ El directorio de sesiones no existe: {session_dir}")
        
        return True
    except Exception as e:
        logging.error(f"❌ Error al verificar la configuración: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    print("\n🔍 Verificando configuración de la aplicación Flask...")
    verificar_configuracion()
