from pymongo import MongoClient
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash
import datetime

load_dotenv()
uri = os.getenv('MONGO_URI')
client = MongoClient(uri, tls=True)
db = client['app_catalogojoyero']

# Buscar en ambas colecciones
users = db['users']
users_unified = db['users_unified']

# Intentar encontrar el usuario en la colección users
user = users.find_one({'email': 'edfrutos@gmail.com'})
if user:
    print(f"Usuario encontrado en users: {user['nombre']}")
    
    # Resetear la contraseña usando el hash existente (scrypt)
    new_password = generate_password_hash('admin123', method='scrypt')
    
    # Desbloquear el usuario
    users.update_one(
        {'_id': user['_id']},
        {
            '$set': {
                'password': new_password,
                'failed_attempts': 0,
                'locked_until': None,
                'last_login': datetime.datetime.utcnow()
            }
        }
    )
    print("Usuario desbloqueado y contraseña reseteada exitosamente")

# Intentar encontrar el usuario en la colección users_unified
user_unified = users_unified.find_one({'email': 'edfrutos@gmail.com'})
if user_unified:
    print(f"Usuario encontrado en users_unified: {user_unified['name']}")
    
    # Resetear la contraseña usando pbkdf2
    new_password = generate_password_hash('admin123', method='pbkdf2:sha256')
    
    # Desbloquear el usuario
    users_unified.update_one(
        {'_id': user_unified['_id']},
        {
            '$set': {
                'password': new_password,
                'password_updated_at': datetime.datetime.utcnow()
            }
        }
    )
    print("Usuario desbloqueado y contraseña reseteada exitosamente")

if not user and not user_unified:
    print("Usuario no encontrado en ninguna colección")
