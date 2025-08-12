# 📁 UBICACIONES DE SCRIPTS Y FUNCIONALIDAD DEL SISTEMA

## 🎯 **Resumen del Diagnóstico**

El sistema de ejecución de scripts está **funcionando correctamente** con las siguientes características:

- ✅ **473 scripts** encontrados en el proyecto
- ✅ __script_runner.py__ principal ubicado en `/tools/script_runner.py`
- ✅ __scripts_routes.py__ configurado correctamente en `/app/routes/scripts_routes.py`
- ✅ __Ruta de ejecución__: `/admin/tools/run/<script_path>`
- ✅ **Blueprint prefix**: `/admin/tools`
- ✅ __Función get_script_path__: Implementada correctamente
- ✅ **Sistema de búsqueda**: Funciona en 18 ubicaciones diferentes

---

## 📂 **Ubicaciones Principales de Scripts**

### 🔧 **Scripts Principales** (`/tools/Scripts Principales/`)


- __supervise_gunicorn.sh__ - Supervisión de Gunicorn (requiere root)
- __supervise_gunicorn_web.sh__ - Supervisión web de Gunicorn ✅
- __script_runner.py__ - Ejecutor de scripts ✅
- __03_validar_integridad.py__ - Validación de integridad de BD
- __04_limpieza_automatizada.py__ - Limpieza automática
- __08_backup_colecciones.py__ - Backup de colecciones
- __09_backup_restore_total.py__ - Backup y restauración total
- __10_backup_incremental.py__ - Backup incremental

### 🏭 **Scripts de Producción** (`/tools/producción/`)

- __supervise_gunicorn.sh__ - Supervisión de Gunicorn
- __supervise_gunicorn_web.sh__ - Supervisión web de Gunicorn ✅
- __start_app.sh__ - Inicio de aplicación
- __start_gunicorn.sh__ - Inicio de Gunicorn
- __restart_server.sh__ - Reinicio del servidor

### 🛠️ **Scripts de Mantenimiento** (`/scripts/maintenance/`)

- __supervise_gunicorn.sh__ - Supervisión de Gunicorn
- __supervise_gunicorn_web.sh__ - Supervisión web de Gunicorn ✅
- __script_runner.py__ - Ejecutor de scripts
- __clean_images.py__ - Limpieza de imágenes
- __monitor_mongodb.py__ - Monitoreo de MongoDB

### 🔍 **Scripts de Diagnóstico** (`/tools/diagnostico/`)

- __debug_users.py__ - Diagnóstico de usuarios ✅
- __diagnose_script_execution.py__ - Diagnóstico de ejecución ✅
- __test_script_execution.py__ - Pruebas de ejecución
- __03_validar_integridad.py__ - Validación de integridad

### 👥 **Scripts de Usuarios** (`/tools/Users Tools/`)

- __check_users.py__ - Verificación de usuarios
- __debug_users.py__ - Depuración de usuarios
- __check_user.py__ - Verificación de usuario individual
- __migrate_users.py__ - Migración de usuarios

### 🔐 **Scripts de Administración** (`/tools/Admin Utils/`)

- __show_admin_user.py__ - Mostrar usuario admin
- __06_eliminar_duplicados_users.py__ - Eliminar duplicados
- __normalize_users.py__ - Normalización de usuarios

---

## 🚀 **Funcionalidad del Sistema**

### **1. Ejecución de Scripts**

- __Ruta__: `/admin/tools/run/<script_path>`
- **Método**: POST
- **Autenticación**: Requiere rol admin
- **Timeout**: 5 minutos

### __2. script_runner.py Principal__

- __Ubicación__: `/tools/script_runner.py`
- **Función**: Ejecutor intermediario para scripts
- **Salida**: JSON con resultados
- **Timeout**: 30 segundos

### **3. Búsqueda de Scripts**

El sistema busca scripts en múltiples ubicaciones:

1. `/tools/Scripts Principales/`
2. `/tools/maintenance/`
3. `/tools/producción/`
4. `/scripts/maintenance/`
5. `/tools/db_utils/`
6. `/tools/diagnostico/`
7. `/tools/system/`
8. `/tools/Users Tools/`
9. `/tools/Admin Utils/`
10. `/tools/utils/`
11. `/tools/monitoring/`
12. `/tools/aws_utils/`
13. `/tools/Test Scripts/`
14. `/tools/app/`
15. `/tools/src/`
16. `/tools/`
17. `/scripts/`

---

## ⚠️ **Scripts que Requieren Atención**

### **Scripts que Requieren Root**

- __supervise_gunicorn.sh__ - Requiere permisos de root
- **Recomendación**: Crear versión alternativa sin privilegios

### **Scripts Funcionando Correctamente**

- __supervise_gunicorn_web.sh__ ✅
- __debug_users.py__ ✅
- __script_runner.py__ ✅
- __test_script.sh__ ✅

---

## 🔧 **Configuración del Sistema**

### **Variables de Entorno Requeridas**

- `MONGO_URI` - Conexión a MongoDB
- `SECRET_KEY` - Clave secreta de Flask
- `AWS_ACCESS_KEY_ID` - Credenciales AWS (opcional)
- `AWS_SECRET_ACCESS_KEY` - Credenciales AWS (opcional)

### **Permisos de Archivos**

- Scripts ejecutables: `chmod +x`
- Archivos de configuración: `chmod 644`
- Directorios: `chmod 755`

---

## 📊 **Estadísticas del Proyecto**

- **Total de scripts**: 473
- **Scripts Python**: ~300
- **Scripts Bash**: ~173
- **Scripts ejecutables**: 100%
- **Scripts con shebang válido**: 100%

---

## 🎯 **Recomendaciones**

1. ✅ **Mantener permisos de ejecución** en todos los scripts
2. ✅ **Evitar scripts que requieran root** para ejecución web
3. ✅ **Usar rutas relativas** dentro de scripts
4. ✅ **Verificar shebang** en todos los scripts
5. ✅ **Crear versiones alternativas** para scripts que requieren root
6. ✅ **Mantener documentación** actualizada

---

## 📝 **Notas del Diagnóstico**

- **Fecha**: 2025-08-07 10:26:55
- **Sistema**: macOS-15.6-arm64-arm-64bit
- **Python**: 3.10.1
- **Usuario**: edefrutos
- **Estado**: ✅ **SISTEMA FUNCIONANDO CORRECTAMENTE**

---

*Documento generado automáticamente por el script de diagnóstico*