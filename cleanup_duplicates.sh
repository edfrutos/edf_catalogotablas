#!/bin/bash
# Script para eliminar directorios duplicados
# Creado: 17/05/2025

echo "Eliminando directorios duplicados..."

# Crear un backup de los directorios antes de eliminarlos
echo "Creando backup de directorios duplicados..."
mkdir -p backup_duplicates
cp -r app/app_catalogo_completo_final backup_duplicates/ 2>/dev/null
cp -r app/routes/app_catalogo_completo_final backup_duplicates/ 2>/dev/null

# Eliminar directorios duplicados
echo "Eliminando app/app_catalogo_completo_final..."
rm -rf app/app_catalogo_completo_final 2>/dev/null

echo "Eliminando app/routes/app_catalogo_completo_final..."
rm -rf app/routes/app_catalogo_completo_final 2>/dev/null

echo "Eliminación de directorios duplicados completada."
echo "Se ha creado un backup en backup_duplicates/ por seguridad."
echo "Si todo funciona correctamente, puede eliminar este backup con: rm -rf backup_duplicates/"
