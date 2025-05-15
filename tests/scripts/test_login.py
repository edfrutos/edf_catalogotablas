from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt

# Cargar variables de entorno
load_dotenv()

# Conectar a MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client['app_catalogojoyero']
users_collection = db['users_unified']

try:
    # Buscar el usuario
    user = users_collection.find_one({'email': 'edfrutos@gmail.com'})
    
    if user:
        print(f"Usuario encontrado: {user['email']}")
        
        # Probar contraseña
        password = '34Maf15si$'
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            print("Contraseña correcta")
        else:
            print("Contraseña incorrecta")
    else:
        print("Usuario no encontrado")
        
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    client.close()
