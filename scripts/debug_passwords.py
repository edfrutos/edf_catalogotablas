from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv
import os
import certifi
from pymongo.server_api import ServerApi

# Cargar variables de entorno
load_dotenv()

# Conectar a MongoDB Atlas
client = MongoClient(
    os.getenv('MONGO_URI'),
    tls=True,
    tlsCAFile=certifi.where(),
    server_api=ServerApi('1')
)

# Seleccionar la base de datos y colección
db = client['app_catalogojoyero']
users = db['users_unified']

def show_user_info(email_or_name):
    """Muestra la información del usuario incluyendo detalles del hash de la contraseña"""
    user = users.find_one({
        '$or': [
            {'email': email_or_name},
            {'username': email_or_name},
            {'nombre': email_or_name},
            {'name': email_or_name}
        ]
    })
    
    if user:
        print(f"\nInformación del usuario:")
        print(f"Email: {user.get('email', 'N/A')}")
        print(f"Nombre: {user.get('nombre', user.get('name', 'N/A'))}")
        print(f"Role: {user.get('role', 'N/A')}")
        
        stored_password = user.get('password')
        print(f"\nContraseña almacenada:")
        print(f"Tipo: {type(stored_password)}")
        print(f"Valor: {stored_password}")
        
        # Verificar si el hash está en formato bcrypt
        if isinstance(stored_password, str) and stored_password.startswith('$2b$'):
            print("El hash está en formato bcrypt correcto")
        else:
            print("ADVERTENCIA: El hash no está en formato bcrypt esperado")
    else:
        print(f"\nUsuario no encontrado")

# Buscar el usuario admin
show_user_info('edfrutos@gmail.com')
