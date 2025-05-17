import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://admin:miclave@cluster0.abcde.mongodb.net/edefrutos?retryWrites=true&w=majority")
DB_NAME = os.getenv("MONGO_DB_NAME", "edefrutos")
SPREADSHEETS = "spreadsheets"
CATALOG = "catalog"

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    spreadsheets = db[SPREADSHEETS]
    catalog = db[CATALOG]

    # 1. Eliminar tablas duplicadas (por filename y owner)
    print("Buscando tablas duplicadas...")
    seen = set()
    to_delete = []
    for t in spreadsheets.find():
        key = (t.get('filename'), t.get('owner'))
        if key in seen:
            to_delete.append(t['_id'])
        else:
            seen.add(key)
    if to_delete:
        print(f"Eliminando {len(to_delete)} tablas duplicadas...")
        spreadsheets.delete_many({'_id': {'$in': to_delete}})
    else:
        print("No se encontraron tablas duplicadas.")

    # 2. Eliminar tablas huérfanas (sin registros en catalog)
    print("Buscando tablas huérfanas...")
    orphan_tables = []
    for t in spreadsheets.find():
        count = catalog.count_documents({'table': t['filename']})
        if count == 0:
            orphan_tables.append(t['_id'])
    if orphan_tables:
        print(f"Eliminando {len(orphan_tables)} tablas huérfanas...")
        spreadsheets.delete_many({'_id': {'$in': orphan_tables}})
    else:
        print("No se encontraron tablas huérfanas.")

    # 3. Eliminar registros huérfanos (sin tabla asociada)
    print("Buscando registros huérfanos...")
    valid_filenames = set([t['filename'] for t in spreadsheets.find()])
    orphan_rows = []
    for row in catalog.find():
        if row.get('table') not in valid_filenames:
            orphan_rows.append(row['_id'])
    if orphan_rows:
        print(f"Eliminando {len(orphan_rows)} registros huérfanos...")
        catalog.delete_many({'_id': {'$in': orphan_rows}})
    else:
        print("No se encontraron registros huérfanos.")

    print("Limpieza completada.")

if __name__ == "__main__":
    main() 