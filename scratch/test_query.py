import sqlite3

DB_PATH = 'reservas.db'

def test_query():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("SELECT rol FROM usuarios LIMIT 1")
        print("Successfully selected 'rol' from 'usuarios'.")
    except sqlite3.OperationalError as e:
        print(f"Error selecting 'rol': {e}")
    conn.close()

if __name__ == "__main__":
    test_query()
