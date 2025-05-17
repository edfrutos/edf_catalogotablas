#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para acceso directo a la aplicación
Este script proporciona una forma directa de acceder a la aplicación
sin pasar por el sistema de autenticación normal.
"""

import os
import sys
from flask import Flask, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from bson import ObjectId

# Añadir el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def crear_app_minima():
    """Crea una aplicación Flask mínima para acceso directo"""
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = 'desarrollo_clave_secreta_fija_12345'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
    app.config['SESSION_COOKIE_NAME'] = 'edefrutos2025_session'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    
    # Asegurar que el directorio de sesiones existe
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Ruta para acceso directo como administrador
    @app.route('/admin_directo')
    def admin_directo():
        # Limpiar sesión anterior
        session.clear()
        
        # Configurar sesión de administrador
        session.permanent = True
        session['user_id'] = 'admin_id'
        session['username'] = 'administrator'
        session['email'] = 'admin@example.com'
        session['role'] = 'admin'
        session['logged_in'] = True
        
        # Forzar guardado de sesión
        session.modified = True
        
        # Mensaje de éxito
        flash('Acceso directo como administrador exitoso', 'success')
        
        # Redirigir al panel de administración
        return redirect('/admin/')
    
    # Ruta para acceso directo como usuario normal
    @app.route('/usuario_directo')
    def usuario_directo():
        # Limpiar sesión anterior
        session.clear()
        
        # Configurar sesión de usuario normal
        session.permanent = True
        session['user_id'] = 'usuario_id'
        session['username'] = 'usuario_normal'
        session['email'] = 'usuario@example.com'
        session['role'] = 'user'
        session['logged_in'] = True
        
        # Forzar guardado de sesión
        session.modified = True
        
        # Mensaje de éxito
        flash('Acceso directo como usuario normal exitoso', 'success')
        
        # Redirigir al dashboard
        return redirect('/dashboard')
    
    # Ruta para verificar la sesión actual
    @app.route('/verificar_sesion')
    def verificar_sesion():
        if session.get('logged_in'):
            return f"""
            <h1>Sesión activa</h1>
            <p>Usuario: {session.get('username')}</p>
            <p>Rol: {session.get('role')}</p>
            <p>ID: {session.get('user_id')}</p>
            <p>Email: {session.get('email')}</p>
            <p>Datos completos de sesión: {dict(session)}</p>
            <p><a href="/admin_directo">Acceder como administrador</a></p>
            <p><a href="/usuario_directo">Acceder como usuario normal</a></p>
            <p><a href="/limpiar_sesion">Limpiar sesión</a></p>
            """
        else:
            return """
            <h1>No hay sesión activa</h1>
            <p><a href="/admin_directo">Acceder como administrador</a></p>
            <p><a href="/usuario_directo">Acceder como usuario normal</a></p>
            """
    
    # Ruta para limpiar la sesión
    @app.route('/limpiar_sesion')
    def limpiar_sesion():
        session.clear()
        return redirect('/verificar_sesion')
    
    # Ruta principal
    @app.route('/')
    def index():
        return """
        <h1>Acceso directo a la aplicación</h1>
        <p><a href="/admin_directo">Acceder como administrador</a></p>
        <p><a href="/usuario_directo">Acceder como usuario normal</a></p>
        <p><a href="/verificar_sesion">Verificar sesión actual</a></p>
        """
    
    return app

if __name__ == '__main__':
    app = crear_app_minima()
    app.run(host='0.0.0.0', port=5002, debug=True)
