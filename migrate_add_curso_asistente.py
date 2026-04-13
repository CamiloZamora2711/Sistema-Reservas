"""
Script para agregar la columna 'curso_asistente' a la tabla reservas
"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Agregar columna curso_asistente a la tabla reservas
    try:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE reservas ADD COLUMN curso_asistente VARCHAR(10)'))
            conn.commit()
        print("✅ Columna 'curso_asistente' agregada exitosamente a la tabla reservas")
    except Exception as e:
        if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
            print("ℹ️  La columna 'curso_asistente' ya existe en la tabla reservas")
        else:
            print(f"❌ Error al agregar columna: {e}")
