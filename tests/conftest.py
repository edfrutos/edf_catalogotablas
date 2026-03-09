# conftest.py - Configuración global de pytest para el proyecto
import os
import sys

# Añadir la raíz del proyecto al sys.path
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)
