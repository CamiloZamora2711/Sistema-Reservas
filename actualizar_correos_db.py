import sqlite3
import unicodedata

def clean_name(s):
    # remove accents (e.g. GÉNESIS -> GENESIS)
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s.lower()

def calcular_correo(nombre_completo):
    partes = nombre_completo.split()
    if len(partes) >= 3:
        paterno = clean_name(partes[0])
        nombre_pila = clean_name(partes[2])
        return f"{nombre_pila}.{paterno}@ssr.cl"
    elif len(partes) == 2:
        paterno = clean_name(partes[0])
        nombre_pila = clean_name(partes[1])
        return f"{nombre_pila}.{paterno}@ssr.cl"
    elif len(partes) == 1:
        return f"{clean_name(partes[0])}@ssr.cl"
    else:
        return ""

def main():
    conn = sqlite3.connect('reservas.db')
    c = conn.cursor()

    # Agregar columna si no existe
    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN correo TEXT")
        print("Columna 'correo' agregada exitosamente.")
    except sqlite3.OperationalError:
        print("La columna 'correo' ya existía.")

    # Obtener usuarios
    c.execute("SELECT id, nombre FROM usuarios")
    rows = c.fetchall()

    updated = 0
    for row in rows:
        uid = row[0]
        nombre_completo = row[1]
        correo = calcular_correo(nombre_completo)
        
        c.execute("UPDATE usuarios SET correo = ? WHERE id = ?", (correo, uid))
        updated += 1
        
    conn.commit()
    conn.close()
    print(f"Correos generados o actualizados para {updated} usuarios.")

if __name__ == '__main__':
    main()
