from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Conectar a MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client['app_catalogojoyero']
users_collection = db['users']

try:
    # Generar nuevo hash de contraseña
    password = 'admin123'
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Actualizar contraseña
    result = users_collection.update_one(
        {'email': 'edfrutos@gmail.com'},
        {'$set': {'password': hashed}}
    )
    
    if result.modified_count > 0:
        print("Contraseña actualizada exitosamente")
        
        # Verificar la actualización
        user = users_collection.find_one({'email': 'edfrutos@gmail.com'})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            print("Verificación exitosa")
        else:
            print("Error en la verificación")
    else:
        print("No se pudo actualizar la contraseña")
        
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    client.close()
