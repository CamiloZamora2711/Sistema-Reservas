import sqlite3
import os

DB_PATH = 'reservas-pcdecamilo.db'

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} does not exist.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print(f"Tables: {tables}")
    
    if ('usuarios',) in tables:
        c.execute("PRAGMA table_info(usuarios)")
        columns = c.fetchall()
        print(f"Columns in 'usuarios': {columns}")
    else:
        print("Table 'usuarios' does not exist.")
        
    conn.close()

if __name__ == "__main__":
    check_db()
