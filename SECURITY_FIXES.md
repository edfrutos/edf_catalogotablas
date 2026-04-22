# Correcciones de Seguridad - edf_catalogotablas

## Resumen

Se han corregido **5 vulnerabilidades críticas** de seguridad que permitían acceso no autorizado a la aplicación Flask.

## Vulnerabilidades Corregidas

### 1. ❌ Rutas de Bypass de Autenticación (ELIMINADAS)

**Problema**: Dos rutas permitían acceso directo sin credenciales:
- `POST /user_login_bypass` — Sesión de usuario normal sin validación
- `POST /admin_login_bypass` — Sesión de admin sin validación
- `POST /acceso_directo_definitivo` — Acceso directo admin hardcodeado
- `POST /acceso_raiz` — Acceso admin desde raíz
- `POST /login_direct` — Login con credenciales hardcodeadas

**Ubicación**: `app/routes/emergency_access.py`, `app/routes/auth_routes.py`

**Riesgo**: Cualquier persona podía acceder como admin o usuario autenticado sin conocer contraseña

**Corrección**:
- ✅ `/user_login_bypass` y `/admin_login_bypass`: Reescrito con validaciones:
  - Solo funcionan en `FLASK_ENV=development`
  - Requieren token VALID de emergencia en variable de entorno `EMERGENCY_TOKEN`
  - Logs de advertencia que registran todos los accesos
  
- ✅ `/acceso_directo_definitivo`, `/acceso_raiz`, `/login_direct`: ELIMINADAS completamente
  - Remplazadas con comentarios que explican por qué fueron removidas

### 2. ❌ Exposición de SECRET_KEY (ELIMINADA)

**Problema**: Ruta `/debug_secret_key` exponía la SECRET_KEY a través de HTTP
```python
@auth_bp.route("/debug_secret_key")
def debug_secret_key():
    return jsonify({"SECRET_KEY": str(current_app.secret_key), ...})
```

**Riesgo**: Cualquier usuario autenticado podía obtener la SECRET_KEY, permitiendo falsificar cookies y sesiones

**Corrección**: ✅ Ruta eliminada completamente
- La SECRET_KEY nunca debe exponerse a través de endpoints HTTP
- Marcada como deprecated en código comentado

### 3. ❌ SECRET_KEY por Defecto Insegura (CORREGIDA)

**Problema**: `config.py` y `factory.py` usaban SECRET_KEY por defecto débil:
```python
SECRET_KEY = os.environ.get("SECRET_KEY", "clave-secreta-por-defecto")  # ❌
app.secret_key = os.getenv("SECRET_KEY", "edf_secret_key_2025")  # ❌
```

**Riesgo**: En producción, si la variable de entorno no se configuraba, la app usaba una clave conocida

**Corrección**: ✅ Validación obligatoria en startup
```python
# En factory.py
if not testing:
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("❌ CRÍTICO: SECRET_KEY no está configurado...")
    if len(secret_key) < 32:
        raise ValueError("❌ CRÍTICO: SECRET_KEY es muy corta...")
    app.secret_key = secret_key
```

- ✅ `config.py`: `SECRET_KEY = None` (sin defecto inseguro)
- ✅ `factory.py`: Valida que SECRET_KEY existe y es >32 caracteres

### 4. ❌ Headers de Seguridad Desactivados (ACTIVADOS)

**Problema**: Headers críticos estaban comentados en `security_middleware.py`:
```python
# response.headers["X-Frame-Options"] = "SAMEORIGIN"  # ❌ Comentado
# response.headers["X-XSS-Protection"] = "1; mode=block"  # ❌ Comentado
# response.headers["Content-Security-Policy"] = ...  # ❌ Comentado
```

**Riesgo**: La aplicación era vulnerable a:
- Clickjacking (X-Frame-Options)
- XSS (X-XSS-Protection, CSP)
- MIME type sniffing

**Corrección**: ✅ Headers activados en `security_middleware.py`
```python
response.headers["X-Content-Type-Options"] = "nosniff"  # ✅ Activo
response.headers["X-Frame-Options"] = "SAMEORIGIN"  # ✅ Activo
response.headers["X-XSS-Protection"] = "1; mode=block"  # ✅ Activo
response.headers["Content-Security-Policy"] = "..."  # ✅ Activo
```

## Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `app/routes/emergency_access.py` | Reescrito con validaciones de seguridad |
| `app/routes/auth_routes.py` | Eliminadas rutas inseguras (debug_secret_key, acceso_directo, etc.) |
| `config.py` | SECRET_KEY sin valor por defecto inseguro |
| `app/factory.py` | Validación obligatoria de SECRET_KEY en startup |
| `app/security_middleware.py` | Headers de seguridad activados (X-Frame-Options, CSP, XSS, etc.) |

## Requisitos para Producción

Ahora, **en producción es OBLIGATORIO**:

1. **Definir SECRET_KEY en variables de entorno**:
   ```bash
   export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
   ```

2. **No usar bypass de emergencia en producción**:
   - `FLASK_ENV` debe ser `production`
   - Las rutas `/user_login_bypass` y `/admin_login_bypass` estarán deshabilitadas

3. **Verificar que SECRET_KEY tiene >32 caracteres**:
   - El app la validará al startup si no cumple

## Testing

Las correcciones mantienen funcionalidad para desarrollo:

```bash
# En desarrollo
export FLASK_ENV=development
export SECRET_KEY="test-secret-key-12345"  # Para tests
export EMERGENCY_TOKEN="my-emergency-token-123"

# Las rutas de bypass funcionarán SOLO en desarrollo
python run_server.py
```

## Impacto de Seguridad

| Vulnerabilidad | Antes | Después | Severidad |
|---|---|---|---|
| Bypass de autenticación | ❌ Abierto a todos | ✅ Solo dev + token | CRÍTICA |
| Exposición SECRET_KEY | ❌ Vía HTTP | ✅ Nunca expuesta | CRÍTICA |
| SECRET_KEY débil | ❌ Por defecto insegura | ✅ Validada en startup | ALTA |
| Headers de seguridad | ❌ Desactivados | ✅ Activos | ALTA |

## Nota para Deployers

Cuando hagan deploy a producción:

1. **Generar SECRET_KEY segura**:
   ```bash
   python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
   ```

2. **Establecer variable de entorno**:
   ```bash
   # .env o variables de sistema
   SECRET_KEY="<output_del_paso_anterior>"
   FLASK_ENV="production"
   ```

3. **Verificar que las rutas de bypass NO están accesibles**:
   ```bash
   curl -i http://localhost:5002/user_login_bypass
   # Debe retornar 403 Forbidden en producción
   ```

---

Commit: chore(security): Fix critical security vulnerabilities
- Remove authentication bypass routes
- Remove SECRET_KEY exposure endpoint
- Enforce SECRET_KEY validation in production
- Activate security headers
