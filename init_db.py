from app import create_app, db
from app.models import User, Sala, BLOQUES_BASICA, BLOQUES_MEDIA

def init_database():
    """Inicializar base de datos con datos de ejemplo"""
    app = create_app()
    
    with app.app_context():
        # Crear tablas
        print("Creando tablas...")
        db.create_all()
        
        # Verificar si ya existen datos
        if User.query.first():
            print("La base de datos ya contiene datos.")
            return
        
        # Crear usuario administrador
        print("Creando usuario administrador...")
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@ssr.cl')
        admin_password = app.config.get('ADMIN_PASSWORD', 'Admin2026!')
        
        admin = User(
            email=admin_email,
            nombre='Administrador',
            rol='admin',
            activo=True
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        
        # Crear usuarios de ejemplo
        print("Creando usuarios de ejemplo...")
        coordinador = User(
            email='coordinador@ssr.cl',
            nombre='María Coordinadora',
            rol='coordinador',
            activo=True
        )
        coordinador.set_password('Coord2026!')
        db.session.add(coordinador)
        
        docente1 = User(
            email='docente1@ssr.cl',
            nombre='Juan Docente',
            rol='docente',
            activo=True
        )
        docente1.set_password('Docente2026!')
        db.session.add(docente1)
        
        docente2 = User(
            email='docente2@ssr.cl',
            nombre='Ana Profesora',
            rol='docente',
            activo=True
        )
        docente2.set_password('Docente2026!')
        db.session.add(docente2)
        
        # Crear salas
        print("Creando salas...")
        salas_data = [
            {
                'nombre': 'Sala Computación Media',
                'capacidad': 35,
                'tipo': 'media',
                'descripcion': 'Sala de computación para educación media',
                'color': '#0d6efd'
            },
            {
                'nombre': 'Sala Computación Básica',
                'capacidad': 30,
                'tipo': 'basica',
                'descripcion': 'Sala de computación para educación básica',
                'color': '#6610f2'
            },
            {
                'nombre': 'Sala Audiovisuales',
                'capacidad': 30,
                'tipo': 'media',
                'descripcion': 'Sala equipada con proyector y sistema de audio',
                'color': '#20c997'
            },
            {
                'nombre': 'Laboratorio Biología/Química',
                'capacidad': 8,
                'tipo': 'media',
                'descripcion': 'Laboratorio de ciencias',
                'color': '#fd7e14'
            },
            {
                'nombre': 'Sala de Teatro Básica',
                'capacidad': 30,
                'tipo': 'basica',
                'descripcion': 'Sala para actividades artísticas',
                'color': '#d63384'
            }
        ]
        
        for sala_data in salas_data:
            sala = Sala(**sala_data)
            db.session.add(sala)
        
        # Commit de todos los cambios
        db.session.commit()
        
        print("\n" + "="*50)
        print("✅ Base de datos inicializada correctamente!")
        print("="*50)
        print("\nUsuarios creados:")
        print("-" * 50)
        print(f"Admin:       admin@ssr.cl / Admin2026!")
        print(f"Coordinador: coordinador@ssr.cl / Coord2026!")
        print(f"Docente 1:   docente1@ssr.cl / Docente2026!")
        print(f"Docente 2:   docente2@ssr.cl / Docente2026!")
        print("-" * 50)
        print(f"\nSalas creadas: {len(salas_data)}")
        print("="*50)

if __name__ == '__main__':
    init_database()
