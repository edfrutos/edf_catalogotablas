from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import bcrypt
from dotenv import load_dotenv
import certifi
import os

# Cargar variables de entorno
load_dotenv()

# Conectar a MongoDB Atlas
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    server_api=ServerApi('1')
)

# Seleccionar la base de datos y colección
db = client.get_database('app_catalogojoyero')
users = db['users_unified']

# Buscar el usuario
user = users.find_one({'email': 'edfrutos@gmail.com'})
if not user:
    print('Usuario no encontrado')
    exit(1)

# Generar nuevo hash con bcrypt y convertirlo a string
password = '34Maf15si$'
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Actualizar la contraseña
result = users.update_one(
    {'_id': user['_id']},
    {'$set': {
        'password': hashed_password,
        'password_updated_at': datetime.now()
    }}
)

if result.modified_count > 0:
    print('Contraseña actualizada exitosamente')
else:
    print('Error al actualizar la contraseña')
