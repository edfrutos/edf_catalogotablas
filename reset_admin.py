from pymongo import MongoClient
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash
import datetime

load_dotenv()
uri = os.getenv('MONGO_URI')
client = MongoClient(uri, tls=True)
db = client['app_catalogojoyero']  # Cambiar a la base de datos correcta
users = db['users']

# Buscar el usuario admin
user = users.find_one({'email': 'edfrutos@gmail.com'})

if user:
    print(f"Usuario encontrado: {user['nombre']}")
    
    # Resetear la contraseña usando el hash existente (scrypt)
    # No necesitamos cambiar el método de hash, solo resetear la contraseña
    new_password = generate_password_hash('admin123', method='scrypt')
    
    # Actualizar el usuario
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
else:
    print("Usuario no encontrado")
