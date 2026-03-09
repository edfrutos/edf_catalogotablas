# NOTEBOOK.md — EDF Catálogo de Tablas

Documento de referencia para el proyecto: características, funcionalidades y mejoras susceptibles de implementar.

---

## 1. Características y Funcionalidades del Repositorio

### 1.1 Visión General

**edf_catalogotablas** es una aplicación web Flask para la gestión de catálogos/tablas con soporte de imágenes, usuarios y administración. Diseñada para producción en `/var/www/vhosts/edefrutos2025.xyz/httpdocs`.

### 1.2 Stack Tecnológico

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Flask | 3.0.2 | Framework web |
| Gunicorn | 23.0.0 | Servidor WSGI producción |
| MongoDB (PyMongo) | 4.10.1 | Base de datos |
| Flask-Login | 0.6.3 | Autenticación |
| boto3 | 1.34.34 | AWS S3 (imágenes) |
| pandas | 2.0.3 | Procesamiento de datos |
| Google APIs | 2.x | Integración Google Drive |

### 1.3 Módulos principales

#### 1.3.1 Factory y configuración

- **`app/factory.py`**: Creación de la app Flask, registro de blueprints, middleware, logging y caché.
- **`config.py`**: BaseConfig, DevelopmentConfig, ProductionConfig. Variables de entorno vía `python-dotenv`.

#### 1.3.2 Base de datos

- **`app/database.py`**: Conexión resiliente a MongoDB con reconexión automática.
- **`app/data_fallback.py`**: Modo fallback cuando MongoDB no está disponible.
- **`app/cache_system.py`**: Caché en disco para reducir consultas.

#### 1.3.3 Blueprints y rutas

| Blueprint | Prefijo | Función |
|-----------|---------|---------|
| `main_bp` | `""` | Página principal, dashboard |
| `auth_bp` | `""` | Login, registro, recuperación contraseña |
| `catalogs_bp` | `/catalogs` | CRUD de catálogos/tablas |
| `image_bp` | `/images` | Subida de imágenes a catálogos |
| `images_bp` | `""` | Servir imágenes (fallback S3 → local) |
| `usuarios_bp` | `/usuarios` | Usuarios y perfiles |
| `admin_bp` | `/admin` | Panel de administración |
| `admin_logs_bp` | `/admin` | Logs de auditoría |
| `scripts_bp` | `/admin/tools` | Ejecución de scripts |
| `scripts_tools_bp` | `/admin/scripts-tools-api` | API de scripts |
| `bp_dev_template` | `/dev-template` | Plantillas de desarrollo |
| `testing_bp` | `/dev-template/testing` | Pruebas |
| `emergency_bp` | `""` | Acceso de emergencia (bypass login) |

#### 1.3.4 Rutas de mantenimiento

Registradas dinámicamente en `factory.py`:

- `maintenance_bp` → `/admin/maintenance`
- `maintenance_api_bp` → `/admin/api`

### 1.4 Funcionalidades principales

1. **Gestión de catálogos**: Crear, editar, eliminar catálogos/tablas con soporte de imágenes.
2. **Imágenes**: Subida a S3, fallback S3 → local para servir `/imagenes_subidas/<filename>`.
3. **Usuarios**: Registro, login, recuperación de contraseña, roles (admin/user).
4. **Administración**: Panel admin, usuarios, backups, logs, base de datos.
5. **Scripts**: Ejecución segura vía `tools/script_runner.py`.
6. **Resiliencia**: Fallback cuando MongoDB no está disponible.
7. **Seguridad**: Middleware de seguridad, path traversal, headers HTTP.

### 1.5 Estructura de directorios

```
edf_catalogotablas/
├── app/                    # Aplicación Flask
│   ├── factory.py          # Creación de la app
│   ├── database.py         # Conexión MongoDB
│   ├── routes/             # Blueprints (~34 módulos)
│   ├── templates/          # Plantillas Jinja2
│   ├── static/             # CSS, JS, imágenes
│   ├── _archived_logging/  # Logging archivado
│   └── static/js/
│       ├── _archived_modals/  # Modales archivados
│       └── obsolete/         # Modales obsoletos
├── tools/                  # Scripts de utilidad
│   ├── Admin Utils/
│   ├── Scripts Principales/
│   ├── Users Tools/
│   └── script_runner.py
├── scripts/               # Scripts de mantenimiento
├── tests/                 # Pruebas pytest
├── config.py
└── requirements.txt
```

---

## 2. Correcciones y Mejoras Susceptibles

### 2.1 Seguridad (crítico)

#### 2.1.1 Rutas de bypass de autenticación

**Problema**: `app/routes/emergency_access.py` expone rutas públicas que permiten iniciar sesión sin credenciales:

- `/user_login_bypass` — sesión de usuario normal
- `/admin_login_bypass` — sesión de administrador

**Riesgo**: Cualquier persona puede acceder como admin o usuario sin autenticación.

**Recomendación**:

- Eliminar estas rutas en producción.
- Si se deben mantener para desarrollo:
  - Proteger con `@login_required` y rol admin.
  - O activar solo cuando `FLASK_ENV=development` o `DEBUG=True`.
  - O proteger con un token secreto en query string.

#### 2.1.2 Ruta de debug de SECRET_KEY

**Problema**: `app/routes/auth_routes.py` línea 683:

```python
@auth_bp.route("/debug_secret_key")
def debug_secret_key():
    if "user_id" not in session:
        return "No autorizado", 401
    return jsonify({
        "SECRET_KEY": str(current_app.secret_key),
        ...
    })
```

**Riesgo**: Cualquier usuario autenticado puede obtener la SECRET_KEY, lo que permite falsificar sesiones y cookies.

**Recomendación**: Eliminar esta ruta o restringirla a entorno de desarrollo con comprobación explícita de `FLASK_ENV=development`.

#### 2.1.3 Ruta de acceso directo definitivo

**Problema**: `auth_routes.py` línea 698:

```python
@auth_bp.route("/acceso_directo_definitivo")
def acceso_directo_definitivo():
    """Acceso directo que funciona definitivamente"""
    # Establece sesión sin verificación
```

**Riesgo**: Similar al bypass de emergencia: acceso sin autenticación.

**Recomendación**: Eliminar o proteger con la misma lógica que `emergency_access`.

#### 2.1.4 SECRET_KEY por defecto

**Problema**: Valores por defecto inseguros en varios archivos:

| Archivo | Valor por defecto |
|---------|-------------------|
| `app/factory.py` | `edf_secret_key_2025` |
| `config.py` | `clave-secreta-por-defecto` |
| `app/__init__.py` | `edf_secret_key_2025` |

**Recomendación**:

- Eliminar valores por defecto en producción.
- Usar `config_check.validate_required()` al arrancar en producción.
- Asegurar que `SECRET_KEY` se defina en `.env` o variables de entorno.

#### 2.1.5 Validación de config

**Problema**: `config_check.py` define `validate_required()` pero no se usa en `factory.py` ni en el punto de entrada.

**Recomendación**: Llamar a `validate_required()` al inicio de `create_app()` cuando `testing=False` y `FLASK_ENV=production`.

#### 2.1.6 Headers de seguridad

**Problema**: En `app/security_middleware.py` varios headers están comentados:

```python
# response.headers["X-Frame-Options"] = "SAMEORIGIN"
# response.headers["X-XSS-Protection"] = "1; mode=block"
# response.headers["Content-Security-Policy"] = ...
```

**Recomendación**: Activar en producción y ajustar CSP según necesidad. Mantener X-Frame-Options y X-XSS-Protection activos.

---

### 2.2 Código y archivos obsoletos

#### 2.2.1 Archivos archivados

**Archivos**: 21 en `_archived_*` y 5 en `obsolete/`:

- `app/_archived_logging/` — 3 archivos
- `app/static/js/_archived_modals/` — 18 archivos
- `app/static/js/obsolete/` — 5 archivos
- `_archived_requirements/requirements-python310-090925.txt`

**Recomendación**:

- Eliminar si no se usan.
- Si se quiere conservar: mover a un directorio fuera del repo (ej. `archive/` en `.gitignore`) o documentar en un `ARCHIVED.md` con motivo y fecha.

#### 2.2.2 Duplicación de archivos

**Problema**: `app/routes/maintenance_routes_refactored.py` con prefijo `/api` frente a `maintenance_routes.py` con `/admin/maintenance`. No está claro si ambos están en uso.

**Recomendación**: Revisar y unificar en un solo módulo de mantenimiento.

#### 2.2.3 Múltiples definiciones de admin_bp

**Problema**: `admin_bp` definido en:

- `app/admin_routes.py`
- `app/routes/admin_routes.py`
- `app/routes/admin/admin_main.py`

**Recomendación**: Centralizar en un único módulo y eliminar duplicados.

---

### 2.3 Consistencia de blueprints

#### 2.3.1 Prefijos vacíos

**Problema**: Blueprints con `url_prefix=""` o sin prefijo:

- `images_bp` → rutas `/imagenes_subidas/<filename>`
- `emergency_bp` → `/user_login_bypass`, `/admin_login_bypass`
- `auth_bp` → `/login`, `/register`, etc.

**Recomendación**: Valorar prefijos explícitos para agrupar:

- `/auth/login`, `/auth/register`
- `/emergency/user_login_bypass` (solo si se mantiene)
- `/images/imagenes_subidas/<filename>`

Esto mejora la organización y el mantenimiento.

#### 2.3.2 Registro en factory

**Problema**: En `factory.py` algunos blueprints usan `url_prefix=prefix`:

```python
(scripts_bp, None),
(scripts_tools_bp, None),
(bp_dev_template, None),
(testing_bp, None),
(images_bp, None),
(emergency_bp, None),
```

Cuando `prefix` es `None`, `register_blueprint(bp, url_prefix=None)` usa el prefijo definido en el Blueprint (o ninguno). Es coherente, pero conviene documentarlo.

---

### 2.4 Configuración

#### 2.4.1 Inconsistencia SECRET_KEY

**Problema**: `config.py` usa `BaseConfig.SECRET_KEY` y `factory.py` sobrescribe:

```python
app.secret_key = os.getenv("SECRET_KEY", "edf_secret_key_2025")
```

Ignora `app.config.from_object("config.Config")`.

**Recomendación**: Usar una única fuente de verdad. Configurar `SECRET_KEY` en `config.py` y no sobrescribir en `factory.py`, o documentar que `factory.py` tiene prioridad.

#### 2.4.2 BASE_DIR duplicado

**Problema**: En `config.py`:

```python
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# ...
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Línea 119
```

**Recomendación**: Eliminar la duplicación.

---

### 2.5 Tests

#### 2.5.1 Cobertura

**Problema**: `tests/` solo contiene 3 archivos:

- `test_profile_images.py`
- `conftest.py`
- `Scripts/conftest.py`

**Recomendación**:

- Añadir tests para rutas críticas (auth, catálogos, admin).
- Tests de integración para MongoDB y fallback.
- Tests de seguridad para rutas de bypass.
- Tests de `config_check.validate_required()`.

---

### 2.6 Documentación

#### 2.6.1 Comentarios en config.py

**Problema**: `config.py` usa plantillas genéricas:

```python
# Descripción: [Explica brevemente qué hace el script]
# Uso: python3 config.py [opciones]
```

**Recomendación**: Sustituir por descripciones reales para cada archivo de configuración.

---

### 2.7 Resumen de prioridades

| Prioridad | Mejora | Esfuerzo |
|-----------|--------|----------|
| Crítica | Eliminar/proteger rutas de bypass y debug_secret_key | Bajo |
| Crítica | Validar SECRET_KEY en producción (config_check) | Bajo |
| Alta | Eliminar SECRET_KEY por defecto en producción | Bajo |
| Alta | Activar headers de seguridad en producción | Medio |
| Media | Limpiar archivos archivados/obsoletos | Bajo |
| Media | Unificar rutas de mantenimiento y admin | Medio |
| Media | Aumentar cobertura de tests | Alto |
| Baja | Prefijos explícitos en blueprints | Medio |
| Baja | Corregir duplicados en config.py | Bajo |

---

## 3. Comandos útiles

```bash
# Linting
flake8
ruff check

# Formato
black .

# Tests
pytest

# Servidor desarrollo
python run_server.py

# Servidor multiproceso
python run_server_multi.py

# Scripts
python3 tools/script_runner.py <script>
```

---

*Documento generado para el proyecto EDF Catálogo de Tablas. Última actualización: revisión del repositorio.*
