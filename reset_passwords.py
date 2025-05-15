import csv

INPUT_FILE = 'app_catalogojoyero.users.csv'
OUTPUT_FILE = 'app_catalogojoyero.users.migrated.csv'

with open(INPUT_FILE, newline='', encoding='utf-8') as infile, open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    # Excluimos el campo _id si existe
    fieldnames = [f for f in reader.fieldnames if f != '_id']
    if 'password' not in fieldnames:
        fieldnames.append('password')
    if 'must_change_password' not in fieldnames:
        fieldnames.append('must_change_password')
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        # Eliminamos el campo _id si existe en la fila
        if '_id' in row:
            del row['_id']
        row['password'] = 'RESET_REQUIRED'
        row['must_change_password'] = 'true'
        writer.writerow(row)

print(f"Archivo migrado generado: {OUTPUT_FILE}") 