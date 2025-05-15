#!/usr/bin/env python
"""
Script definitivo para arreglar las contraseñas de los usuarios 
usando un método compatible con werkzeug.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.models import get_users_collection
from datetime import datetime
import sys
import os

def fix_user_password(email, new_password):
    """
    Corrige la contraseña de un usuario usando el método nativo de werkzeug.
    """
    print(f"\n=== ARREGLANDO CONTRASEÑA PARA: {email} ===")
    
    users_col = get_users_collection()
    user = users_col.find_one({"email": email})
    
    if not user:
        print(f"❌ Usuario no encontrado: {email}")
        return False
    
    print(f"✅ Usuario encontrado: {email}")
    print(f"   - ID: {user['_id']}")
    print(f"   - Rol: {user.get('role', 'user')}")
    
    # Generar nuevo hash de contraseña usando pbkdf2:sha256 (método por defecto de werkzeug)
    # Este método es ampliamente compatible
    hashed_password = generate_password_hash(new_password)
    
    # Actualizar usuario con nueva contraseña y desbloquear
    result = users_col.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "password": hashed_password,
            "password_type": "werkzeug",
            "password_updated_at": datetime.utcnow().isoformat(),
            "failed_attempts": 0,
            "locked_until": None
        }}
    )
    
    if result.modified_count > 0:
        print(f"✅ Contraseña actualizada correctamente para {email}")
        print(f"   - Nuevo hash: {hashed_password[:30]}...")
        
        # Verificar si funciona
        print("\n=== VERIFICANDO CONTRASEÑA ===")
        if check_password_hash(hashed_password, new_password):
            print(f"✅ Verificación exitosa para {email}")
            return True
        else:
            print(f"❌ La verificación falló para {email}")
            return False
    else:
        print(f"❌ No se pudo actualizar la contraseña para {email}")
        return False

if __name__ == "__main__":
    print("=== SCRIPT DEFINITIVO DE CORRECCIÓN DE CONTRASEÑAS ===")
    
    # Primero corregir admin principal
    fix_user_password('admin@example.com', 'admin123')
    
    # Luego corregir edfrutos
    fix_user_password('edfrutos@gmail.com', 'admin123')
    
    print("\n=== REPARACIÓN COMPLETA ===")
    print("Ahora puedes intentar iniciar sesión con estas credenciales:")
    print("- Email: admin@example.com o edfrutos@gmail.com")
    print("- Contraseña: admin123")
