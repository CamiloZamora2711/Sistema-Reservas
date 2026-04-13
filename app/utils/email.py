"""
Utilidades para envío de emails
"""
from flask import render_template, current_app
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    """Enviar email de forma asíncrona"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error al enviar email: {e}")

def send_email(subject, recipients, text_body, html_body):
    """Enviar email"""
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # Enviar de forma asíncrona
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_bienvenida(usuario):
    """Enviar email de bienvenida a nuevo usuario"""
    subject = '🎉 Bienvenido al Sistema de Reservas SSR 2026'
    
    # Texto plano
    text_body = f"""
¡Bienvenido al Sistema de Reservas SSR 2026!

Hola {usuario.nombre},

Tu cuenta ha sido creada exitosamente. Ya puedes comenzar a reservar salas para tus clases.

Tus datos de acceso:
- Email: {usuario.email}
- Rol: {usuario.rol}

Para acceder al sistema:
1. Ve a: http://localhost:5040
2. Inicia sesión con tu email y contraseña

Funcionalidades disponibles:
- Reservar salas de clases
- Ver tus reservas
- Cancelar reservas
- Ver disponibilidad de salas

Si tienes alguna duda, contacta al administrador.

¡Bienvenido!
Sistema de Reservas SSR 2026
"""
    
    # HTML estilizado
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .welcome-box {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .info-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .info-row {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-row:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: bold;
            color: #495057;
            min-width: 80px;
        }}
        .info-value {{
            color: #212529;
        }}
        .features {{
            background-color: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .feature-item {{
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .feature-item:last-child {{
            border-bottom: none;
        }}
        .feature-item i {{
            color: #667eea;
            margin-right: 10px;
        }}
        .button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 ¡Bienvenido!</h1>
            <p>Sistema de Reservas SSR 2026</p>
        </div>
        
        <div class="content">
            <div class="welcome-box">
                <h2 style="margin-top: 0; color: #667eea;">Hola {usuario.nombre},</h2>
                <p style="margin-bottom: 0;">Tu cuenta ha sido creada exitosamente. Ya puedes comenzar a reservar salas para tus clases.</p>
            </div>
            
            <div class="info-box">
                <h3 style="margin-top: 0; color: #667eea;">👤 Tus Datos de Acceso</h3>
                
                <div class="info-row">
                    <div class="info-label">📧 Email:</div>
                    <div class="info-value">{usuario.email}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">🎭 Rol:</div>
                    <div class="info-value">{usuario.rol.capitalize()}</div>
                </div>
            </div>
            
            <div style="text-align: center;">
                <a href="http://localhost:5040" class="button">
                    🚀 Acceder al Sistema
                </a>
            </div>
            
            <div class="features">
                <h3 style="margin-top: 0; color: #667eea;">✨ Funcionalidades Disponibles</h3>
                
                <div class="feature-item">
                    <i>📅</i> <strong>Reservar Salas:</strong> Reserva salas para tus clases con hasta 30 días de anticipación
                </div>
                
                <div class="feature-item">
                    <i>👁️</i> <strong>Ver Disponibilidad:</strong> Consulta qué salas están disponibles en tiempo real
                </div>
                
                <div class="feature-item">
                    <i>📋</i> <strong>Mis Reservas:</strong> Revisa todas tus reservas activas y su estado
                </div>
                
                <div class="feature-item">
                    <i>❌</i> <strong>Cancelar Reservas:</strong> Cancela reservas si ya no las necesitas
                </div>
                
                <div class="feature-item">
                    <i>📊</i> <strong>Calendario:</strong> Visualiza todas las reservas en un calendario interactivo
                </div>
            </div>
            
            <p style="margin-top: 30px;">Si tienes alguna duda o necesitas ayuda, no dudes en contactar al administrador.</p>
            
            <p><strong>¡Que tengas un excelente día!</strong></p>
        </div>
        
        <div class="footer">
            <p>Sistema de Reservas SSR 2026</p>
            <p>Este es un email automático, por favor no responder.</p>
        </div>
    </div>
</body>
</html>
"""
    
    send_email(subject, [usuario.email], text_body, html_body)

def send_reserva_confirmacion(reserva):
    """Enviar email de confirmación de reserva al usuario"""
    subject = f'Reserva Creada - {reserva.sala.nombre}'
    
    # Texto plano
    text_body = f"""
Hola {reserva.usuario.nombre},

Tu reserva ha sido creada exitosamente.

Detalles de la reserva:
- Sala: {reserva.sala.nombre}
- Fecha: {reserva.fecha.strftime('%d/%m/%Y')}
- Bloque: {reserva.bloque}
- Curso: {reserva.curso_asistente or 'No especificado'}
- Motivo: {reserva.motivo}
- Estado: {reserva.estado.upper()}

{'Esta reserva requiere aprobación del coordinador.' if reserva.estado == 'pendiente' else 'Tu reserva ha sido aprobada automáticamente.'}

Saludos,
Sistema de Reservas SSR 2026
"""
    
    # HTML estilizado
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
        }}
        .info-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .info-row {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-row:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: bold;
            color: #495057;
            min-width: 120px;
        }}
        .info-value {{
            color: #212529;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }}
        .status-pendiente {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .status-aprobada {{
            background-color: #d1ecf1;
            color: #0c5460;
        }}
        .alert {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Reserva Creada Exitosamente</h1>
        </div>
        
        <div class="content">
            <p>Hola <strong>{reserva.usuario.nombre}</strong>,</p>
            <p>Tu reserva ha sido creada exitosamente en el sistema.</p>
            
            <div class="info-box">
                <h3 style="margin-top: 0; color: #667eea;">📋 Detalles de la Reserva</h3>
                
                <div class="info-row">
                    <div class="info-label">🏢 Sala:</div>
                    <div class="info-value">{reserva.sala.nombre}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">📅 Fecha:</div>
                    <div class="info-value">{reserva.fecha.strftime('%d/%m/%Y')}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">🕐 Bloque:</div>
                    <div class="info-value">{reserva.bloque}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">👥 Curso:</div>
                    <div class="info-value">{reserva.curso_asistente or 'No especificado'}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">📝 Motivo:</div>
                    <div class="info-value">{reserva.motivo}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">📊 Estado:</div>
                    <div class="info-value">
                        <span class="status-badge status-{reserva.estado}">
                            {reserva.estado.upper()}
                        </span>
                    </div>
                </div>
            </div>
            
            {'<div class="alert">⏳ <strong>Nota:</strong> Esta reserva requiere aprobación del coordinador. Recibirás un email cuando sea aprobada o rechazada.</div>' if reserva.estado == 'pendiente' else '<div class="alert" style="background-color: #d1ecf1; border-left-color: #0c5460;">✅ <strong>¡Aprobada!</strong> Tu reserva ha sido aprobada automáticamente.</div>'}
            
            <p style="margin-top: 30px;">Si tienes alguna pregunta, contacta al coordinador.</p>
        </div>
        
        <div class="footer">
            <p>Sistema de Reservas SSR 2026</p>
            <p>Este es un email automático, por favor no responder.</p>
        </div>
    </div>
</body>
</html>
"""
    
    send_email(subject, [reserva.usuario.email], text_body, html_body)

def send_reserva_aprobada(reserva):
    """Enviar email cuando una reserva es aprobada"""
    subject = f'✅ Reserva Aprobada - {reserva.sala.nombre}'
    
    # Texto plano
    text_body = f"""
Hola {reserva.usuario.nombre},

¡Buenas noticias! Tu reserva ha sido APROBADA.

Detalles de la reserva:
- Sala: {reserva.sala.nombre}
- Fecha: {reserva.fecha.strftime('%d/%m/%Y')}
- Bloque: {reserva.bloque}
- Curso: {reserva.curso_asistente or 'No especificado'}
- Motivo: {reserva.motivo}

Tu reserva está confirmada. Por favor, asiste puntualmente.

Saludos,
Sistema de Reservas SSR 2026
"""
    
    # HTML estilizado
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
        }}
        .info-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .info-row {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-row:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: bold;
            color: #495057;
            min-width: 120px;
        }}
        .info-value {{
            color: #212529;
        }}
        .success-box {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            color: #155724;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Reserva Aprobada</h1>
        </div>
        
        <div class="content">
            <p>Hola <strong>{reserva.usuario.nombre}</strong>,</p>
            
            <div class="success-box">
                <h3 style="margin-top: 0;">🎉 ¡Buenas Noticias!</h3>
                <p style="margin-bottom: 0;">Tu reserva ha sido <strong>APROBADA</strong> por el coordinador.</p>
            </div>
            
            <div class="info-box">
                <h3 style="margin-top: 0; color: #28a745;">📋 Detalles de la Reserva</h3>
                
                <div class="info-row">
                    <div class="info-label">🏢 Sala:</div>
                    <div class="info-value">{reserva.sala.nombre}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">📅 Fecha:</div>
                    <div class="info-value">{reserva.fecha.strftime('%d/%m/%Y')}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">🕐 Bloque:</div>
                    <div class="info-value">{reserva.bloque}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">👥 Curso:</div>
                    <div class="info-value">{reserva.curso_asistente or 'No especificado'}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">📝 Motivo:</div>
                    <div class="info-value">{reserva.motivo}</div>
                </div>
            </div>
            
            <p style="margin-top: 30px;"><strong>Importante:</strong> Por favor, asiste puntualmente a tu reserva.</p>
        </div>
        
        <div class="footer">
            <p>Sistema de Reservas SSR 2026</p>
            <p>Este es un email automático, por favor no responder.</p>
        </div>
    </div>
</body>
</html>
"""
    
    send_email(subject, [reserva.usuario.email], text_body, html_body)

def send_reserva_rechazada(reserva):
    """Enviar email cuando una reserva es rechazada"""
    subject = f'❌ Reserva Rechazada - {reserva.sala.nombre}'
    
    # Texto plano
    text_body = f"""
Hola {reserva.usuario.nombre},

Lamentablemente, tu reserva ha sido RECHAZADA.

Detalles de la reserva:
- Sala: {reserva.sala.nombre}
- Fecha: {reserva.fecha.strftime('%d/%m/%Y')}
- Bloque: {reserva.bloque}
- Curso: {reserva.curso_asistente or 'No especificado'}
- Motivo: {reserva.motivo}

Si tienes dudas, contacta al coordinador.

Saludos,
Sistema de Reservas SSR 2026
"""
    
    # HTML estilizado
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
        }}
        .info-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .info-row {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-row:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: bold;
            color: #495057;
            min-width: 120px;
        }}
        .info-value {{
            color: #212529;
        }}
        .warning-box {{
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            color: #721c24;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>❌ Reserva Rechazada</h1>
        </div>
        
        <div class="content">
            <p>Hola <strong>{reserva.usuario.nombre}</strong>,</p>
            
            <div class="warning-box">
                <h3 style="margin-top: 0;">Reserva No Aprobada</h3>
                <p style="margin-bottom: 0;">Lamentablemente, tu reserva ha sido <strong>RECHAZADA</strong> por el coordinador.</p>
            </div>
            
            <div class="info-box">
                <h3 style="margin-top: 0; color: #dc3545;">📋 Detalles de la Reserva</h3>
                
                <div class="info-row">
                    <div class="info-label">🏢 Sala:</div>
                    <div class="info-value">{reserva.sala.nombre}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">📅 Fecha:</div>
                    <div class="info-value">{reserva.fecha.strftime('%d/%m/%Y')}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">🕐 Bloque:</div>
                    <div class="info-value">{reserva.bloque}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">👥 Curso:</div>
                    <div class="info-value">{reserva.curso_asistente or 'No especificado'}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">📝 Motivo:</div>
                    <div class="info-value">{reserva.motivo}</div>
                </div>
            </div>
            
            <p style="margin-top: 30px;">Si tienes dudas sobre el rechazo, por favor contacta al coordinador.</p>
        </div>
        
        <div class="footer">
            <p>Sistema de Reservas SSR 2026</p>
            <p>Este es un email automático, por favor no responder.</p>
        </div>
    </div>
</body>
</html>
"""
    
    send_email(subject, [reserva.usuario.email], text_body, html_body)

def send_reserva_notificacion_admin(reserva):
    """Enviar notificación al administrador sobre nueva reserva"""
    subject = f'Nueva Reserva - {reserva.usuario.nombre}'
    
    # Texto plano
    text_body = f"""
Nueva reserva creada en el sistema.

Usuario: {reserva.usuario.nombre} ({reserva.usuario.email})
Sala: {reserva.sala.nombre}
Fecha: {reserva.fecha.strftime('%d/%m/%Y')}
Bloque: {reserva.bloque}
Curso: {reserva.curso_asistente or 'No especificado'}
Motivo: {reserva.motivo}
Estado: {reserva.estado.upper()}

Accede al panel de administración para gestionar esta reserva.
"""
    
    # HTML estilizado
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
        }}
        .info-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .info-row {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-row:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: bold;
            color: #495057;
            min-width: 120px;
        }}
        .info-value {{
            color: #212529;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 Nueva Reserva Creada</h1>
        </div>
        
        <div class="content">
            <p>Se ha creado una nueva reserva en el sistema.</p>
            
            <div class="info-box">
                <h3 style="margin-top: 0; color: #667eea;">👤 Usuario</h3>
                <div class="info-row">
                    <div class="info-label">Nombre:</div>
                    <div class="info-value">{reserva.usuario.nombre}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Email:</div>
                    <div class="info-value">{reserva.usuario.email}</div>
                </div>
            </div>
            
            <div class="info-box">
                <h3 style="margin-top: 0; color: #667eea;">📋 Detalles de la Reserva</h3>
                
                <div class="info-row">
                    <div class="info-label">🏢 Sala:</div>
                    <div class="info-value">{reserva.sala.nombre}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">📅 Fecha:</div>
                    <div class="info-value">{reserva.fecha.strftime('%d/%m/%Y')}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">🕐 Bloque:</div>
                    <div class="info-value">{reserva.bloque}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">👥 Curso:</div>
                    <div class="info-value">{reserva.curso_asistente or 'No especificado'}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">📝 Motivo:</div>
                    <div class="info-value">{reserva.motivo}</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">📊 Estado:</div>
                    <div class="info-value"><strong>{reserva.estado.upper()}</strong></div>
                </div>
            </div>
            
            <p style="margin-top: 30px; text-align: center;">
                <a href="http://localhost:5040/admin/aprobaciones" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; 
                          padding: 12px 30px; 
                          text-decoration: none; 
                          border-radius: 5px; 
                          display: inline-block;">
                    Ver en Panel Admin
                </a>
            </p>
        </div>
        
        <div class="footer">
            <p>Sistema de Reservas SSR 2026</p>
            <p>Este es un email automático, por favor no responder.</p>
        </div>
    </div>
</body>
</html>
"""
    
    send_email(subject, [current_app.config['MAIL_ADMIN']], text_body, html_body)
