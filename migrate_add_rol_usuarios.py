import sqlite3

DB_PATH = 'reservas.db'

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("Verificando tabla 'usuarios'...")
    try:
        # Intentar agregar la columna 'rol'
        c.execute("ALTER TABLE usuarios ADD COLUMN rol TEXT DEFAULT 'docente'")
        conn.commit()
        print("OK: Columna 'rol' agregada exitosamente a la tabla 'usuarios'.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("ℹ️  La columna 'rol' ya existe.")
        else:
            print(f"❌ Error al migrar: {e}")
    
    conn.close()

if __name__ == '__main__':
    migrate()
