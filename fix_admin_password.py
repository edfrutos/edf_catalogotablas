#!/usr/bin/env python
"""
Script para corregir la contraseña de administrador.
Esto establecerá la contraseña 'admin123' para el usuario administrador.
"""

import sys
import os
from datetime import datetime
from app.models import get_users_collection, hash_password
from bson.objectid import ObjectId

def fix_admin_password(email, password):
    """
    Corregir la contraseña de un usuario.
    """
    print(f"Buscando usuario: {email}")
    users_col = get_users_collection()
    user = users_col.find_one({"email": email})
    
    if not user:
        print(f"No se encontró el usuario con email {email}")
        return False
    
    # Crear hash de contraseña usando scrypt (más seguro)
    hashed_password = hash_password(password, method='scrypt')
    
    # Actualizar usuario con nueva contraseña y desbloquear
    result = users_col.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "password": hashed_password,
            "password_type": "scrypt",
            "password_updated_at": datetime.utcnow().isoformat(),
            "failed_attempts": 0,
            "locked_until": None
        }}
    )
    
    if result.modified_count > 0:
        print(f"✅ Contraseña actualizada correctamente para {email}")
        return True
    else:
        print(f"❌ No se pudo actualizar la contraseña para {email}")
        return False

def main():
    # Primero el administrador principal
    fix_admin_password('admin@example.com', 'admin123')
    
    # Luego el usuario edfrutos si existe
    fix_admin_password('edfrutos@gmail.com', 'admin123')
    
if __name__ == "__main__":
    main()
