# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) cuando trabaja con código en este repositorio.

## Comandos de Desarrollo

### Linting y Calidad de Código
```bash
# Ejecutar linting con flake8
flake8

# Ejecutar linting con ruff (linter alternativo con más reglas)
ruff check

# Formatear código con black
black .
```

### Pruebas
```bash
# Ejecutar pruebas con pytest
pytest

# Ejecutar archivo de prueba específico
pytest tests/test_filename.py
```

### Gestión del Servidor
```bash
# Reiniciar servidor de producción (servicio systemd)
systemctl restart edefrutos2025

# Servidor de desarrollo
python run_server.py

# Servidor de desarrollo multiproceso
python run_server_multi.py
```

### Ejecución de Scripts
```bash
# Ejecutar scripts de mantenimiento/utilidades a través del ejecutor de scripts
python3 tools/script_runner.py <ruta_del_script>

# Activar entorno virtual
source .venv/bin/activate
```

## Visión General de la Arquitectura

### Estructura Central de la Aplicación
- **Patrón Factory de Flask**: Creación de la app principal en `app/factory.py`
- **Base de Datos MongoDB**: Conexión resiliente con sistema de fallback en `app/database.py`
- **Enrutamiento basado en Blueprints**: Organización modular de rutas a través de múltiples blueprints
- **Entorno de Producción**: Diseñado para `/var/www/vhosts/edefrutos2025.xyz/httpdocs`

### Componentes Clave

#### Capa de Base de Datos (`app/database.py`)
- Conexión resiliente a MongoDB con reconexión automática
- Sistema de fallback para operación offline usando `app/data_fallback.py`
- Capa de caché vía `app/cache_system.py` para reducir consultas a la base de datos
- Gestión de conexión global con operaciones thread-safe
- Soporte para MongoDB Atlas con configuración SSL/TLS

#### Factory de la Aplicación (`app/factory.py`)
- Crea la app Flask con todos los blueprints registrados
- Inicializa la conexión a la base de datos y autenticación de usuarios
- Configura logging, middleware de seguridad y extensiones
- Maneja páginas de error y preprocesamiento de peticiones

#### Organización de Rutas
Las rutas están organizadas en blueprints lógicos:
- `main_routes.py` - Página principal y funcionalidad central
- `catalogs_routes.py` - Gestión de catálogos/hojas de cálculo (prefijo `/catalogs`)
- `auth_routes.py` - Autenticación de usuarios
- `admin_routes.py` - Panel de administración (prefijo `/admin`)
- `scripts_routes.py` - Interfaz de ejecución de scripts
- `maintenance_routes.py` - Endpoints de mantenimiento del sistema

#### Sistema de Herramientas y Scripts
- `tools/` - Scripts de utilidad organizados por categoría (Admin Utils, Scripts Principales, Users Tools, etc.)
- `scripts/local/` - Scripts de entorno local para mantenimiento, monitorización y utilidades
- `tools/script_runner.py` - Envoltorio de ejecución segura de scripts que devuelve resultados JSON

### Características Principales
- **Gestión de Catálogos**: Crear y gestionar catálogos de datos/hojas de cálculo con soporte de imágenes
- **Gestión de Usuarios**: Acceso basado en roles con capacidades de administrador
- **Manejo de Imágenes**: Integración con S3 para almacenamiento y gestión de imágenes
- **Herramientas de Mantenimiento**: Amplia colección de scripts de mantenimiento y diagnóstico
- **Integración MongoDB**: Capa de base de datos flexible con capacidades de fallback

### Configuración
- Variables de entorno cargadas vía `python-dotenv`
- Configuración principal en `config.py` con URI de MongoDB, credenciales AWS, gestión de sesiones
- Linting configurado vía `.flake8` y `pyproject.toml` (ruff)
- Entorno virtual en `.venv/` usando Python 3.8+

### Dependencias
Dependencias clave de producción desde `requirements.txt`:
- Flask 3.0.2 con Gunicorn para producción
- PyMongo 4.10.1 para conectividad MongoDB
- Flask-Login para autenticación
- boto3 para integración con AWS S3
- pandas para procesamiento de datos

### Notas de Desarrollo
- Estilo de código aplicado con flake8 (120 caracteres por línea) y formateo con black
- Manejo extensivo de errores y logging a lo largo de la aplicación
- Comentarios y nombres de variables en portugués/español reflejan la base de usuarios objetivo
- Sistemas de fallback integrales aseguran la disponibilidad de la aplicación durante problemas de base de datos