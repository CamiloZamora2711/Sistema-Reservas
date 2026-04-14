import sqlite3

def test_routes_logic():
    try:
        conn = sqlite3.connect('reservas.db')
        c = conn.cursor()
        
        print("Probando consulta de reservas...")
        c.execute("SELECT * FROM reservas")
        reservas = c.fetchall()
        print(f"Total reservas: {len(reservas)}")
        
        for r in reservas:
            # Simular logica de index()
            sala_nombre = r[1]
            bloque = r[3]
            fecha = r[2]
            estado = r[6] if len(r) > 6 else 'aprobada'
            print(f"Reserva: {sala_nombre}, {fecha}, {bloque}, {estado}")
            
        print("\nProbando consulta de usuarios...")
        c.execute("SELECT nombre FROM usuarios ORDER BY nombre")
        usuarios = c.fetchall()
        print(f"Total usuarios: {len(usuarios)}")
        
        conn.close()
        print("\nPrueba de lógica exitosa.")
    except Exception as e:
        print(f"\nERROR DETECTADO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_routes_logic()
