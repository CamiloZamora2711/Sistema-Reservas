"""
Script de prueba para verificar la configuración de email
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración
MAIL_SERVER = 'smtp.office365.com'
MAIL_PORT = 587
MAIL_USERNAME = 'admin_valpo@ssr.cl'
MAIL_PASSWORD = 'Rafael2026'
MAIL_TO = 'juan.llanca@ssr.cl'

print("🔍 Probando conexión SMTP con Microsoft 365...")
print(f"Servidor: {MAIL_SERVER}:{MAIL_PORT}")
print(f"Usuario: {MAIL_USERNAME}")
print(f"Destinatario: {MAIL_TO}")
print("-" * 50)

try:
    # Crear mensaje
    msg = MIMEMultipart()
    msg['From'] = MAIL_USERNAME
    msg['To'] = MAIL_TO
    msg['Subject'] = 'Prueba de Email - Sistema de Reservas SSR'
    
    body = """
    Hola,
    
    Este es un email de prueba del Sistema de Reservas SSR 2026.
    
    Si recibes este mensaje, la configuración de email está funcionando correctamente.
    
    Saludos,
    Sistema de Reservas
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Conectar al servidor
    print("📡 Conectando al servidor SMTP...")
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
    server.set_debuglevel(1)  # Mostrar debug info
    
    print("🔐 Iniciando TLS...")
    server.starttls()
    
    print("🔑 Autenticando...")
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    
    print("📧 Enviando email...")
    server.send_message(msg)
    
    print("✅ Email enviado exitosamente!")
    server.quit()
    
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ Error de autenticación: {e}")
    print("Verifica que el usuario y contraseña sean correctos.")
    
except smtplib.SMTPException as e:
    print(f"❌ Error SMTP: {e}")
    
except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()
