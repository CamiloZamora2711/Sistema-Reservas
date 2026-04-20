"""
Script para crear la tabla 'usuarios' e importar los nombres desde usuarios.xlsx
"""
import sqlite3
import openpyxl
import unicodedata

def clean_name(s):
    if not s: return ""
    s = ''.join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn')
    return s.lower()

def calcular_correo(nombre_completo):
    partes = str(nombre_completo).split()
    if len(partes) >= 3:
        return f"{clean_name(partes[2])}.{clean_name(partes[0])}@ssr.cl"
    elif len(partes) == 2:
        return f"{clean_name(partes[1])}.{clean_name(partes[0])}@ssr.cl"
    elif len(partes) == 1:
        return f"{clean_name(partes[0])}@ssr.cl"
    return ""

DB_PATH = 'reservas.db'
EXCEL_PATH = 'usuarios.xlsx'

def importar_usuarios():
    # Leer Excel
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb.active

    nombres = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        nombre = row[0]
        if nombre and str(nombre).strip():
            nombres.append(str(nombre).strip())

    print(f"✅ Se encontraron {len(nombres)} usuarios en el archivo Excel.")

    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Crear tabla usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        correo TEXT,
        rol TEXT DEFAULT 'docente'
    )''')
    conn.commit()
    
    # Intento de agregar las columnas si la tabla es antigua
    for col, default in [('correo', 'NULL'), ('rol', "'docente'")]:
        try:
            c.execute(f"ALTER TABLE usuarios ADD COLUMN {col} {default if col == 'correo' else 'TEXT DEFAULT ' + default}")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # La columna ya existe

    print("✅ Tabla 'usuarios' lista.")

    # Insertar nombres (sin duplicados)
    insertados = 0
    omitidos = 0
        try:
            c.execute("INSERT INTO usuarios (nombre, correo, rol) VALUES (?, ?, ?)", (nombre, correo, 'docente'))
            insertados += 1
        except sqlite3.IntegrityError:
            omitidos += 1  # Nombre ya existe

    conn.commit()
    conn.close()

    print(f"✅ Usuarios importados: {insertados}")
    if omitidos:
        print(f"⚠️  Omitidos por duplicado: {omitidos}")
    print("\n📋 Primeros 5 usuarios importados:")
    for n in nombres[:5]:
        print(f"   - {n}")

if __name__ == '__main__':
    importar_usuarios()
