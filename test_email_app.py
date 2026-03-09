"""
Script de prueba mejorado para verificar configuración de email
"""
from app import create_app

app = create_app()

with app.app_context():
    print("🔍 Verificando configuración de email...")
    print("-" * 50)
    print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
    print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"MAIL_PASSWORD: {'*' * len(app.config['MAIL_PASSWORD'])}")
    print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
    print(f"MAIL_ADMIN: {app.config['MAIL_ADMIN']}")
    print("-" * 50)
    
    # Probar envío de email
    from app.utils.email import send_email
    
    print("\n📧 Enviando email de prueba...")
    try:
        send_email(
            subject='Prueba - Sistema de Reservas SSR',
            recipients=[app.config['MAIL_ADMIN']],
            text_body='Este es un email de prueba.',
            html_body='<h1>Email de Prueba</h1><p>Este es un email de prueba del sistema.</p>'
        )
        print("✅ Email enviado (verificando en segundo plano)")
        print(f"Revisa la bandeja de {app.config['MAIL_ADMIN']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
