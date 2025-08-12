# Guía de Reconocimiento Automático de Scripts

## ✅ **RESPUESTA DIRECTA A TU PREGUNTA**

**SÍ, los nuevos scripts son reconocidos automáticamente** cuando los colocas en cualquiera de los directorios configurados. **NO necesitas ejecutar ninguna funcionalidad adicional**.

## 🔄 **Cómo Funciona el Reconocimiento Automático**

### 1. **Escaneo Dinámico**
El sistema escanea automáticamente los directorios configurados cada vez que:
- Se accede a la página del Gestor de Scripts
- Se solicita la lista de scripts disponibles
- Se ejecuta la API `/admin/tools/api/scripts_metadata`

### 2. **Directorios Reconocidos**
El sistema reconoce scripts en estos directorios organizados por categorías:

#### 📊 **Categorías y Directorios:**

| Categoría | Directorios |
|-----------|-------------|
| **Database Utils** | `tools/local/db_utils`, `tools/production/db_utils`, `scripts/local/maintenance`, `scripts/production/maintenance` |
| **System Maintenance** | `scripts/local/maintenance`, `scripts/production/maintenance`, `tools/local/maintenance`, `tools/production/maintenance`, `tools/local/system`, `tools/production/system` |
| **User Management** | `tools/local/admin_utils`, `tools/production/admin_utils`, `tools/local/user_utils`, `tools/production/user_utils` |
| **File Management** | `tools/local/utils`, `tools/production/utils`, `tools/local/catalog_utils`, `tools/production/catalog_utils` |
| **Monitoring** | `tools/local/monitoring`, `tools/production/monitoring`, `tools/local/diagnostico`, `tools/production/diagnostico` |
| **Testing** | `tests/local/unit`, `tests/local/integration`, `tests/local/functional`, `tests/local/performance`, `tests/local/security`, `tests/production/*`, `tools/testing` |
| **Diagnostic Tools** | `tools/diagnostic`, `tools/local/diagnostico`, `tools/production/diagnostico` |
| **Migration Tools** | `tools/migration`, `tools/local/aws_utils`, `tools/production/aws_utils` |
| **Configuration Tools** | `tools/configuration`, `tools/production/configuration` |
| **Development Tools** | `tools/local/app`, `tools/production/app`, `tools/local/src`, `tools/production/src` |
| **Infrastructure** | `tools/local/aws_utils`, `tools/production/aws_utils`, `tools/local/session_utils`, `tools/production/session_utils` |
| **Root Tools** | `tools/local/utils`, `tools/production/utils` |

## 📝 **Pasos para Agregar un Nuevo Script**

### 1. **Crear el Script**
```bash
# Ejemplo: crear un script de base de datos
nano tools/production/db_utils/mi_nuevo_script.py
```

### 2. **Agregar Descripción (Opcional pero Recomendado)**
```python
#!/usr/bin/env python3
# Descripción: Mi nuevo script para gestionar la base de datos
# Autor: Tu nombre
# Fecha: 2025-08-11

import os
import sys
from datetime import datetime

def main():
    print("=== MI NUEVO SCRIPT ===")
    print(f"Fecha: {datetime.now()}")
    # Tu código aquí
    
if __name__ == "__main__":
    main()
```

### 3. **Establecer Permisos de Ejecución**
```bash
chmod 755 tools/production/db_utils/mi_nuevo_script.py
```

### 4. **¡Listo!**
El script será reconocido automáticamente. Solo recarga la página del Gestor de Scripts.

## 🔍 **Verificación del Reconocimiento**

### Usar el Script de Gestión:
```bash
# Escanear todos los scripts
python3 gestionar_nuevos_scripts.py scan

# Verificar scripts nuevos
python3 gestionar_nuevos_scripts.py check

# Obtener guía completa
python3 gestionar_nuevos_scripts.py add
```

### Verificar Manualmente:
```bash
# Contar scripts en un directorio específico
ls -la tools/production/db_utils/*.py | wc -l

# Verificar permisos
ls -la tools/production/db_utils/*.py
```

## ⚡ **Ejemplo Práctico**

### Antes de agregar el script:
```
📊 RESUMEN:
  Total de scripts encontrados: 220
  Scripts reconocidos: 220
  Scripts no reconocidos: 0
```

### Después de agregar `ejemplo_nuevo_script.py`:
```
📊 RESUMEN:
  Total de scripts encontrados: 221
  Scripts reconocidos: 221
  Scripts no reconocidos: 0
```

El nuevo script aparece automáticamente en la categoría "Database Utils" porque está en `tools/production/db_utils/`.

## 🛠️ **Herramientas Disponibles**

### 1. **Script de Gestión** (`gestionar_nuevos_scripts.py`)
- **`scan`**: Escanea y muestra todos los scripts reconocidos
- **`add`**: Muestra guía para agregar nuevos scripts
- **`template`**: Crea una plantilla de script
- **`check`**: Verifica scripts nuevos y permisos

### 2. **Script de Diagnóstico** (`fix_script_execution.py`)
- Verifica el estado del sistema de scripts
- Corrige permisos automáticamente
- Diagnostica problemas de ejecución

### 3. **Script de Prueba Web** (`test_web_script_execution.py`)
- Prueba la ejecución desde la interfaz web
- Verifica conectividad con el servidor

## 📋 **Requisitos para el Reconocimiento**

### ✅ **Scripts Reconocidos Automáticamente:**
- Archivos `.py` (Python) y `.sh` (Bash)
- Ubicados en directorios configurados
- Con permisos de ejecución (755)
- Con descripción opcional en comentarios

### ❌ **Scripts NO Reconocidos:**
- Archivos sin extensión `.py` o `.sh`
- Ubicados fuera de directorios configurados
- Sin permisos de ejecución
- Directorios (solo archivos)

## 🔧 **Solución de Problemas**

### Si un script no aparece:

1. **Verificar ubicación:**
   ```bash
   python3 gestionar_nuevos_scripts.py scan
   ```

2. **Verificar permisos:**
   ```bash
   ls -la tu_script.py
   chmod 755 tu_script.py
   ```

3. **Verificar directorio:**
   ```bash
   # Asegúrate de que esté en un directorio reconocido
   python3 gestionar_nuevos_scripts.py add
   ```

4. **Recargar la página web:**
   - Limpia la caché del navegador
   - Recarga la página del Gestor de Scripts

## 🎯 **Conclusión**

**El sistema de reconocimiento de scripts es completamente automático.** Solo necesitas:

1. ✅ Colocar el script en el directorio correcto
2. ✅ Darle permisos de ejecución (`chmod 755`)
3. ✅ Recargar la página web

**No hay comandos adicionales, no hay configuraciones manuales, no hay reinicios necesarios.**

El sistema está diseñado para ser **plug-and-play**: agrega scripts y aparecen automáticamente en la interfaz web.
