import sqlite3

DB_PATH = 'reservas.db'

def update_user():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Marcamos a un usuario como administrativo para pruebas
    nombre_test = 'AGURTO PARADA MIGUEL ANTONIO'
    c.execute("UPDATE usuarios SET rol='administrativo' WHERE nombre=?", (nombre_test,))
    conn.commit()
    
    print(f"OK: Usuario '{nombre_test}' actualizado a rol 'administrativo'.")
    conn.close()

if __name__ == '__main__':
    update_user()
