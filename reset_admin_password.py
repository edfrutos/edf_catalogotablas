#!/usr/bin/env python
"""
Script para resetear contraseñas de administrador.
"""

from werkzeug.security import generate_password_hash
from app.models import get_users_collection
from datetime import datetime
from bson.objectid import ObjectId
import sys

# Valores a establecer
NEW_PASSWORD = 'admin123'
ADMIN_EMAILS = ['admin@example.com', 'edfrutos@gmail.com']

def reset_admin_password():
    """Resetear la contraseña de los usuarios administradores."""
    users_collection = get_users_collection()
    
    for email in ADMIN_EMAILS:
        # Buscar el usuario
        print(f"Buscando usuario: {email}")
        user = users_collection.find_one({"email": email})
        
        if not user:
            print(f"  - No se encontró el usuario: {email}")
            continue
            
        # Generar nueva contraseña con método scrypt (más seguro)
        new_password_hash = generate_password_hash(NEW_PASSWORD, method='scrypt')
        
        # Actualizar el usuario
        result = users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "password": new_password_hash,
                "password_type": "scrypt",
                "failed_attempts": 0,
                "locked_until": None,
                "password_updated_at": datetime.utcnow().isoformat()
            }}
        )
        
        if result.modified_count > 0:
            print(f"  - ✅ Contraseña actualizada para {email}")
        else:
            print(f"  - ❌ No se pudo actualizar la contraseña para {email}")

if __name__ == "__main__":
    print("=== SCRIPT DE RESTABLECIMIENTO DE CONTRASEÑAS ===")
    reset_admin_password()
    print("=== COMPLETADO ===")
