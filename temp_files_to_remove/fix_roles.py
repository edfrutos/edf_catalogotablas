import os
from pymongo import MongoClient

# Configura tu URI de conexión aquí
MONGO_URI = "mongodb+srv://edfrutos:rYjwUC6pUNrLtbaI@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority"
DB_NAME = "app_catalogojoyero"
COLLECTIONS = ["users", "users_unified", "usuarios"]

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    total_actualizados = 0

    for collection_name in COLLECTIONS:
        if collection_name not in db.list_collection_names():
            continue
        collection = db[collection_name]
        print(f"Revisando colección: {collection_name}")

        # Buscar usuarios sin campo 'role' o con role vacío/nulo
        query = {"$or": [{"role": {"$exists": False}}, {"role": None}, {"role": ""}]}
        usuarios = list(collection.find(query))

        for user in usuarios:
            nuevo_role = "admin" if user.get("email") == "admin@example.com" else "user"
            result = collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"role": nuevo_role}}
            )
            print(f"Usuario {user.get('email', user.get('username', user['_id']))}: role → {nuevo_role}")
            total_actualizados += result.modified_count

    print(f"\nTotal de usuarios actualizados: {total_actualizados}")

if __name__ == "__main__":
    main() 