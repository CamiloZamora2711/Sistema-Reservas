"""
Script de diagnóstico para verificar salas
"""
from app import create_app, db
from app.models import Sala, User

app = create_app()

with app.app_context():
    print("=" * 60)
    print("DIAGNÓSTICO DEL SISTEMA DE SALAS")
    print("=" * 60)
    
    # Verificar salas
    print("\n📍 SALAS EN LA BASE DE DATOS:")
    salas = Sala.query.all()
    print(f"Total de salas: {len(salas)}")
    
    for sala in salas:
        print(f"\n  ID: {sala.id}")
        print(f"  Nombre: {sala.nombre}")
        print(f"  Tipo: {sala.tipo}")
        print(f"  Capacidad: {sala.capacidad}")
        print(f"  Activa: {'✅ Sí' if sala.activa else '❌ No'}")
        print(f"  Color: {sala.color}")
    
    # Verificar salas activas
    print("\n" + "=" * 60)
    print("📍 SALAS ACTIVAS (las que aparecen en formularios):")
    salas_activas = Sala.query.filter_by(activa=True).all()
    print(f"Total de salas activas: {len(salas_activas)}")
    
    for sala in salas_activas:
        print(f"  - {sala.nombre} (ID: {sala.id})")
    
    # Verificar usuarios admin/coordinador
    print("\n" + "=" * 60)
    print("📍 USUARIOS CON ACCESO A GESTIÓN DE SALAS:")
    admins = User.query.filter(User.rol.in_(['admin', 'coordinador'])).all()
    
    for user in admins:
        print(f"  - {user.email} ({user.rol})")
    
    print("\n" + "=" * 60)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("=" * 60)
