# Reorganización de Scripts del Proyecto

## Resumen de la Reorganización

Se ha realizado una limpieza y reorganización completa de los scripts del proyecto, moviendo los archivos desde el directorio raíz a subdirectorios específicos según su funcionalidad.

## Estructura Actual

### Archivos Mantenidos en el Directorio Raíz
Los siguientes archivos se han mantenido en el directorio raíz por ser esenciales para el funcionamiento del proyecto:

- **app.py**: Punto de entrada principal de la aplicación
- **config.py**: Configuración principal del proyecto
- **wsgi.py**: Punto de entrada WSGI para servidores web
- **passenger_wsgi.py**: Punto de entrada para Passenger
- **gunicorn.conf.py** y **gunicorn_config.py**: Configuración de Gunicorn

### Scripts Organizados por Categoría

#### 1. Scripts de Administración (`/scripts/admin_utils/`)
- **admin_shell.py**: Acceso directo a funciones administrativas
- **admin_utils.py**: Utilidades para administración
- **create_admin.py**: Creación de usuario administrador
- **init_admin.py**: Inicialización de administrador
- **repair_admin.py**: Reparación de cuenta de administrador

#### 2. Scripts para Ejecutar la Aplicación (`/scripts/app_runners/`)
- **ejecutar_flask_directo.py**: Ejecución directa de Flask sin Gunicorn
- **flask_app.py**: Aplicación Flask simplificada
- **simple_app.py** y **simple.py**: Versiones mínimas de la aplicación
- **app_min.py**: Versión mínima de la aplicación
- **app_prueba_sesion.py**: Prueba de sesiones
- **run.py**: Script de ejecución

#### 3. Scripts de Gestión de Sesiones (`/scripts/session_utils/`)
- **aplicar_configuracion_sesion.py**: Aplicación de configuración de sesiones
- **session_config.py**: Configuración de sesiones
- **session_fix.py**: Corrección de problemas de sesiones

#### 4. Scripts de Monitoreo (`/scripts/monitoring/`)
- **advanced_monitor.py**: Monitoreo avanzado
- **error_handling.py**: Manejo de errores

#### 5. Scripts de Catálogos (`/scripts/catalog_utils/`)
- **arreglar_catalogos.py**: Corrección de catálogos
- **tables_direct.py**: Acceso directo a tablas
- **direct_routes.py**: Rutas directas
- **convert_to_xlsx.py**: Conversión a formato XLSX

#### 6. Scripts de Imágenes (`/scripts/image_utils/`)
- **crear_imagen_perfil_default.py**: Creación de imagen de perfil por defecto

#### 7. Scripts de Contraseñas (`/scripts/password_utils/`)
- Scripts para gestión, reseteo y actualización de contraseñas

#### 8. Scripts de Base de Datos (`/scripts/db_utils/`)
- Scripts para operaciones con la base de datos

#### 9. Scripts de AWS (`/scripts/aws_utils/`)
- Scripts para interactuar con servicios AWS

#### 10. Scripts de Mantenimiento (`/scripts/maintenance/`)
- Scripts para tareas de mantenimiento del sistema

## Beneficios de la Reorganización

1. **Mejor organización**: Los scripts están ahora agrupados por funcionalidad
2. **Mayor claridad**: Es más fácil encontrar scripts específicos
3. **Directorio raíz más limpio**: Solo contiene archivos esenciales
4. **Mejor mantenibilidad**: Facilita el mantenimiento y actualización del código

## Recomendaciones

1. **Actualizar rutas en scripts**: Si algún script hace referencia a otros scripts por ruta relativa, es posible que sea necesario actualizar estas referencias.

2. **Actualizar documentación**: Actualizar cualquier documentación que haga referencia a la ubicación de estos scripts.

3. **Revisar permisos de ejecución**: Asegurarse de que los scripts que necesitan ser ejecutables mantengan sus permisos después de la reorganización.

4. **Pruebas**: Realizar pruebas para asegurar que la reorganización no ha afectado la funcionalidad del sistema.
