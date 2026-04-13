"""
Script para agregar la columna 'curso' a la tabla users
"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Agregar columna curso a la tabla users
    try:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE users ADD COLUMN curso VARCHAR(10)'))
            conn.commit()
        print("✅ Columna 'curso' agregada exitosamente a la tabla users")
    except Exception as e:
        if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
            print("ℹ️  La columna 'curso' ya existe en la tabla users")
        else:
            print(f"❌ Error al agregar columna: {e}")

