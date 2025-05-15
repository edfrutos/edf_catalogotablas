#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalogs')
def catalogs():
    return redirect('http://127.0.0.1:8002/catalogs/')

@app.route('/dashboard')
def dashboard():
    return redirect('http://127.0.0.1:8002/dashboard_user')

@app.route('/admin')
def admin():
    return redirect('http://127.0.0.1:8002/admin/')

if __name__ == '__main__':
    # Crear la plantilla HTML necesaria
    import os
    os.makedirs('templates', exist_ok=True)
    with open('templates/index.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Acceso Directo Completo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .btn-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            margin-top: 30px;
        }
        .btn {
            display: inline-block;
            padding: 15px 25px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            text-align: center;
            min-width: 200px;
            margin: 10px;
        }
        .btn-admin {
            background-color: #2196F3;
        }
        .btn-dashboard {
            background-color: #FF9800;
        }
        .btn:hover {
            opacity: 0.9;
        }
        .note {
            margin-top: 30px;
            padding: 10px;
            background-color: #fffde7;
            border-left: 4px solid #ffd600;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Acceso Directo Completo</h1>
        <p>Utiliza los siguientes botones para acceder directamente a las diferentes secciones de la aplicación:</p>
        
        <div class="btn-container">
            <a href="/catalogs" class="btn">Catálogos</a>
            <a href="/dashboard" class="btn btn-dashboard">Dashboard de Usuario</a>
            <a href="/admin" class="btn btn-admin">Panel de Administración</a>
        </div>
        
        <div class="note">
            <p><strong>Nota:</strong> Este acceso directo permite acceder a todas las secciones de la aplicación sin necesidad de iniciar sesión. 
            Es una herramienta de desarrollo y no debe utilizarse en producción.</p>
        </div>
    </div>
</body>
</html>""")
    
    print("Acceso directo completo iniciado en http://127.0.0.1:5002")
    print("Accede a http://127.0.0.1:5002 para seleccionar la sección a la que quieres acceder")
    app.run(host='127.0.0.1', port=5002, debug=True)
