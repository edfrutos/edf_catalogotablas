from pymongo import MongoClient
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash
import bcrypt

load_dotenv()
uri = os.getenv('MONGO_URI')
client = MongoClient(uri, tls=True)
db = client['edefrutos']
users = db['users']

# Función para verificar si es un hash scrypt
def is_scrypt_hash(hash_str):
    return hash_str.startswith('scrypt:')

# Actualizar todas las contraseñas
for user in users.find({}, {'password': 1, 'email': 1, 'nombre': 1}):
    password = user['password']
    
    if is_scrypt_hash(password):
        print(f"Actualizando contraseña para usuario: {user.get('email') or user.get('nombre')}")
        # Convertir el hash scrypt a bcrypt
        # Primero extraemos el hash sin el prefijo
        hash_parts = password.split('$')
        scrypt_hash = '$'.join(hash_parts[1:])
        
        # Generamos un nuevo hash bcrypt
        bcrypt_hash = generate_password_hash(scrypt_hash, method='bcrypt')
        
        # Actualizamos en la base de datos
        users.update_one(
            {'_id': user['_id']},
            {'$set': {'password': bcrypt_hash}}
        )
        print(f"Contraseña actualizada exitosamente para usuario: {user.get('email') or user.get('nombre')}")

print("Proceso de actualización completado")
