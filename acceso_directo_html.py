#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Acceso Directo</title>
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
                flex-direction: column;
                align-items: center;
                margin-top: 30px;
            }
            .btn {
                display: block;
                padding: 15px 25px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                text-align: center;
                width: 80%;
                margin: 10px 0;
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Acceso Directo</h1>
            <p>Haz clic en los enlaces para acceder directamente:</p>
            
            <div class="btn-container">
                <a href="http://127.0.0.1:8002/catalogs/" class="btn" target="_blank">Ver Catálogos</a>
                <a href="http://127.0.0.1:8002/dashboard_user" class="btn btn-dashboard" target="_blank">Dashboard de Usuario</a>
                <a href="http://127.0.0.1:8002/admin/" class="btn btn-admin" target="_blank">Panel de Administración</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    print("Acceso directo HTML iniciado en http://127.0.0.1:5010")
    print("Accede a http://127.0.0.1:5010 para ver los enlaces directos")
    app.run(host='127.0.0.1', port=5010, debug=True)
