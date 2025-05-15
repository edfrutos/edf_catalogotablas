import pytest
import sys
import os

# Añadir la raíz del proyecto al sys.path para que se pueda importar app.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Si usas Flask-WTF
    return app 