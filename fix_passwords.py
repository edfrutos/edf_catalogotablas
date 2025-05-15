from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi
from pymongo.server_api import ServerApi
import bcrypt

def fix_password_formats():
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Conectar a MongoDB Atlas
        client = MongoClient(
            os.getenv('MONGO_URI'),
            tls=True,
            tlsCAFile=certifi.where(),
            server_api=ServerApi('1')
        )
        
        # Seleccionar la base de datos
        db = client['app_catalogojoyero']
        users = db['users']
        
        # Buscar usuarios con contraseñas en formato string
        string_password_users = users.find({
            "password": {"$type": "string"}
        })
        
        count = 0
        for user in string_password_users:
            print(f"\nProcesando usuario: {user.get('email')}")
            old_password = user.get('password')
            
            # Generar nuevo hash
            temp_password = "CambiarPassword123"  # Contraseña temporal segura
            new_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())
            
            # Actualizar usuario
            result = users.update_one(
                {'_id': user['_id']},
                {'$set': {
                    'password': new_hash,
                    'must_change_password': True  # Flag para forzar cambio de contraseña
                }}
            )
            
            if result.modified_count > 0:
                print(f"✅ Contraseña actualizada para {user.get('email')}")
                count += 1
            else:
                print(f"❌ Error al actualizar {user.get('email')}")
        
        print(f"\nProceso completado. {count} usuarios actualizados.")
        
    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == '__main__':
    fix_password_formats()
