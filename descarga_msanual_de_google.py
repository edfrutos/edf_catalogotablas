# Probar si se puede descargar el archivo específico
from app.utils.google_drive_wrapper import download_file
try:
    content = download_file('1qVqck1ie3XZwkPB9BJa8eosv4q220OZy')
    print(f"Descarga exitosa: {len(content)} bytes")
except Exception as e:
    print(f"Error: {e}")