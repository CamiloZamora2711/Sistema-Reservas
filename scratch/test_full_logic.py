import sqlite3
from datetime import date, timedelta, datetime
import json

DB_PATH = 'reservas.db'
salas_disponibles = {
    "Sala Computación Media": {"capacidad": 35, "tipo": "media", "color": "#6610f2"},
    "Sala Computación Básica": {"capacidad": 30, "tipo": "basica", "color": "#fd7e14"},
    "Sala Audiovisuales": {"capacidad": 30, "tipo": "media", "color": "#0d6efd"},
    "Laboratorio Biología/Química": {"capacidad": 8, "tipo": "media", "color": "#20c997"},
    "Sala de Teatro Básica": {"capacidad": 30, "tipo": "basica", "color": "#d63384"},
}

bloques = {
    "basica": [
        "08:15-09:00", "09:00-09:45", "10:00-10:45", "10:45-11:30",
        "11:45-12:30", "12:30-13:15", "14:00-14:40", "14:40-15:20", "15:35-16:15"
    ],
    "media": [
        "08:15-09:00", "09:00-09:45", "10:00-10:45", "10:45-11:30",
        "11:45-12:30", "12:30-13:15", "13:15-14:00", "14:45-15:25", "15:25-16:10", "16:20-17:05"
    ]
}

bloque_a_hora = {}
for tipo, lista in bloques.items():
    for b in lista:
        parts = b.split('-')
        if len(parts) == 2:
            inicio, fin = parts
            bloque_a_hora[b] = (inicio + ":00", fin + ":00")

def test_full_index_logic():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        print("Cargando reservas...")
        c.execute("SELECT * FROM reservas")
        reservas_db = c.fetchall()
        
        eventos = []
        for r in reservas_db:
            # Replicating index() logic
            sala_nombre = r[1]
            tipo = salas_disponibles.get(sala_nombre, {}).get("tipo", "otro")
            color = salas_disponibles.get(sala_nombre, {}).get("color", "#6c757d")
            
            estado_reserva = r[6] if len(r) > 6 else 'aprobada'
            if estado_reserva == 'pendiente':
                color = '#adb5bd'

            bloque = r[3]
            fecha = r[2]
            inicio, fin = bloque_a_hora.get(bloque, ("08:00:00", "08:45:00"))
            start_datetime = f"{fecha}T{inicio}"
            end_datetime = f"{fecha}T{fin}"

            curso_tipo_reserva = r[5] if len(r) > 5 else ''
            curso_asistente = r[7] if len(r) > 7 else ''
            
            titulo_evento = f"{sala_nombre} - {bloque}"
            if curso_asistente:
                titulo_evento += f" ({curso_asistente})"

            eventos.append({
                'title': titulo_evento,
                'start': start_datetime,
                'end': end_datetime,
                'color': color,
                'extendedProps': {
                    'nombre': r[4],
                    'estado': estado_reserva,
                    'curso_tipo': curso_tipo_reserva,
                    'curso_asistente': curso_asistente
                }
            })
        
        print(f"Total eventos generados: {len(eventos)}")
        print("Probando serialización JSON...")
        json_output = json.dumps(eventos)
        print("Serialización OK.")
        
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_index_logic()
