import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('reservas.db')
        c = conn.cursor()
        
        # List tables
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        print(f"Tables: {tables}")
        
        for table in tables:
            table_name = table[0]
            print(f"\nSchema for {table_name}:")
            c.execute(f"PRAGMA table_info({table_name})")
            columns = c.fetchall()
            for col in columns:
                print(col)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
