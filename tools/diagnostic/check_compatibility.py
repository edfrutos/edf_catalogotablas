#!/usr/bin/env python3
# Descripción: Verifica la compatibilidad del sistema
"""
Script para verificar compatibilidad de paquetes con Python 3.8
y generar un archivo requirements.txt funcional
"""

import subprocess
import sys
import re

def get_available_versions(package_name):
    """Obtiene las versiones disponibles de un paquete"""
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'index', 'versions', package_name
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Extraer versiones de la salida
            versions = []
            for line in result.stdout.split('\n'):
                if 'Available versions:' in line:
                    version_str = line.split('Available versions:')[1].strip()
                    versions = [v.strip() for v in version_str.split(',')]
                    break
            return versions
        else:
            # Intentar con pip search como alternativa
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'search', package_name
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Extraer versiones de la salida de búsqueda
                versions = []
                for line in result.stdout.split('\n'):
                    if package_name in line and '(' in line and ')' in line:
                        version_match = re.search(r'\(([^)]+)\)', line)
                        if version_match:
                            version_str = version_match.group(1)
                            if version_str != 'latest':
                                versions.append(version_str)
                return versions
    except Exception as e:
        print(f"Error obteniendo versiones para {package_name}: {e}")
    
    return []

def find_compatible_version(package_name, target_version):
    """Encuentra una versión compatible con Python 3.8"""
    available_versions = get_available_versions(package_name)
    
    if not available_versions:
        print(f"No se pudieron obtener versiones para {package_name}")
        return target_version
    
    # Ordenar versiones (asumiendo formato semver)
    try:
        from packaging import version
        sorted_versions = sorted(available_versions, key=version.parse, reverse=True)
        
        # Buscar la versión más alta que sea menor o igual a la target
        target_v = version.parse(target_version)
        for v in sorted_versions:
            try:
                v_parsed = version.parse(v)
                if v_parsed <= target_v:
                    return v
            except:
                continue
                
    except ImportError:
        # Fallback simple si no hay packaging
        pass
    
    # Si no encontramos una versión compatible, usar la más reciente disponible
    return available_versions[0] if available_versions else target_version

def main():
    # Paquetes problemáticos conocidos y sus versiones compatibles con Python 3.8
    problematic_packages = {
        'Authlib': '1.3.2',
        'anyio': '4.5.2',
        'asgiref': '3.8.1',
        'astroid': '3.2.4',
        'fastapi': '0.104.1',
        'starlette': '0.27.0',
        'uvicorn': '0.24.0',
        'pydantic': '2.5.0',
        'pydantic_core': '2.14.5',
        'msgspec': '1.0.5',
        'typing_extensions': '4.8.0',
        'importlib_metadata': '6.8.0',
        'packaging': '23.2',
        'numpy': '1.24.4',
        'pandas': '2.0.3',
        'scipy': '1.11.4',
        'pillow': '10.1.0',
        'cryptography': '41.0.7',
        'grpcio': '1.59.3',
        'protobuf': '4.25.1',
        'google-cloud-aiplatform': '1.38.1',
        'google-cloud-bigquery': '3.13.0',
        'google-cloud-storage': '2.10.0',
        'google-auth': '2.23.4',
        'google-api-python-client': '2.108.0',
        'boto3': '1.34.0',
        'botocore': '1.34.0',
        'requests': '2.31.0',
        'urllib3': '2.0.7',
        'httpx': '0.25.2',
        'httpcore': '1.0.2',
        'websockets': '12.0',
        'redis': '5.0.1',
        'pymongo': '4.6.0',
        'sqlalchemy': '2.0.23',
        'flask': '3.0.0',
        'werkzeug': '3.0.1',
        'jinja2': '3.1.2',
        'click': '8.1.7',
        'itsdangerous': '2.1.2',
        'markupsafe': '2.1.3',
        'gunicorn': '21.2.0',
        'pytest': '7.4.3',
        'black': '23.11.0',
        'isort': '5.12.0',
        'pylint': '3.0.3',
        'mypy_extensions': '1.0.0',
        'typing-inspection': '0.9.0',
        'rich': '13.7.0',
        'tqdm': '4.66.1',
        'python-dateutil': '2.8.2',
        'python-dotenv': '1.0.0',
        'pytz': '2023.3',
        'tzdata': '2023.3',
        'certifi': '2023.11.17',
        'charset-normalizer': '3.3.2',
        'idna': '3.6',
        'six': '1.16.0',
        'cffi': '1.16.0',
        'pycparser': '2.21',
        'bcrypt': '4.1.2',
        'passlib': '1.7.4',
        'email-validator': '2.1.0',
        'wtforms': '3.1.1',
        'flask-wtf': '1.2.1',
        'flask-login': '0.6.3',
        'flask-mail': '0.9.1',
        'flask-session': '0.5.0',
        'flask-limiter': '3.5.0',
        'flask-pymongo': '2.3.0',
        'flask-redis': '0.4.0',
        'beautifulsoup4': '4.12.2',
        'lxml': '4.9.3',
        'openpyxl': '3.1.2',
        'qrcode': '7.4.2',
        'pyotp': '2.9.0',
        'faker': '20.1.0',
        'duckduckgo-search': '4.1.1',
        'httpx-sse': '0.3.2',
        'sse-starlette': '1.8.2',
        'python-multipart': '0.0.6',
        'tenacity': '8.2.3',
        'tabulate': '0.9.0',
        'platformdirs': '4.0.0',
        'pluggy': '1.3.0',
        'iniconfig': '2.0.0',
        'tomli': '2.0.1',
        'tomlkit': '0.12.3',
        'pathspec': '0.11.2',
        'mdurl': '0.1.2',
        'markdown-it-py': '3.0.0',
        'docstring-parser': '0.15',
        'typer': '0.9.0',
        'shellingham': '1.5.4',
        'more-itertools': '10.1.0',
        'jaraco.text': '3.0.0',
        'jaraco.functools': '3.5.2',
        'jaraco.context': '4.3.0',
        'autocommand': '2.2.2',
        'prettier': '0.0.7',
        'primp': '0.15.0',
        'print': '1.3.0',
        'debugger': '1.3',
        'debugpy': '1.8.0',
        'deprecated': '1.2.14',
        'dill': '0.3.7',
        'cloudpickle': '3.0.0',
        'psutil': '5.9.6',
        'watchdog': '3.0.0',
        'pywebview': '4.4.1',
        'pyobjc-core': '10.1',
        'pyobjc-framework-Cocoa': '10.1',
        'pyobjc-framework-Quartz': '10.1',
        'pyobjc-framework-Security': '10.1',
        'pyobjc-framework-WebKit': '10.1',
        'py2app': '0.28.6',
        'macholib': '1.16.3',
        'modulegraph': '0.19.4',
        'altgraph': '0.17.4',
        'appdirs': '1.4.4',
        'pyparsing': '3.1.1',
        'packaging': '23.2',
        'setuptools': '68.2.2',
        'wheel': '0.41.6',
        'pip': '23.3.1'
    }
    
    print("Verificando compatibilidad con Python 3.8...")
    print(f"Python version: {sys.version}")
    
    # Leer el archivo requirements.txt original
    try:
        with open('requirements.txt', 'r') as f:
            original_requirements = f.readlines()
    except FileNotFoundError:
        print("No se encontró requirements.txt")
        return
    
    # Procesar cada línea
    updated_requirements = []
    for line in original_requirements:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Extraer nombre y versión del paquete
        if '==' in line:
            package_name, version = line.split('==', 1)
            package_name = package_name.strip()
            version = version.strip()
            
            # Verificar si es un paquete problemático
            if package_name in problematic_packages:
                compatible_version = problematic_packages[package_name]
                updated_line = f"{package_name}=={compatible_version}"
                print(f"Actualizando {package_name}: {version} -> {compatible_version}")
            else:
                updated_line = line
                print(f"Manteniendo {package_name}: {version}")
            
            updated_requirements.append(updated_line)
        else:
            # Paquete sin versión específica
            updated_requirements.append(line)
            print(f"Manteniendo {line} (sin versión específica)")
    
    # Escribir el archivo actualizado
    with open('requirements_python38_fixed.txt', 'w') as f:
        for line in updated_requirements:
            f.write(line + '\n')
    
    print(f"\nArchivo actualizado guardado como: requirements_python38_fixed.txt")
    print("Ahora puedes probar: pip install -r requirements_python38_fixed.txt")

if __name__ == "__main__":
    main()
