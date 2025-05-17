#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('http://127.0.0.1:8002/catalogs/')

if __name__ == '__main__':
    print("Acceso directo a catálogos iniciado en http://127.0.0.1:5001")
    print("Accede a http://127.0.0.1:5001 para ser redirigido automáticamente a los catálogos")
    app.run(host='127.0.0.1', port=5001, debug=True)
