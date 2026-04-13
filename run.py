import os
from app import create_app, db

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5040, debug=True)
