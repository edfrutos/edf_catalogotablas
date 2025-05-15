from dotenv import load_dotenv
import os
from pymongo import MongoClient

# Cargar variables de entorno
load_dotenv()

# Configuración de conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("Error: MONGO_URI no está definida")
    exit(1)

# Intentar conexión
try:
    client = MongoClient(MONGO_URI)
    # Probar conexión
    client.admin.command('ping')
    print("Conexión exitosa a MongoDB")
    
    # Listar bases de datos disponibles
    print("Bases de datos disponibles:")
    print(client.list_database_names())
    
except Exception as e:
    print(f"Error al conectar a MongoDB: {str(e)}")
