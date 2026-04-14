from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import date, timedelta, datetime
from collections import Counter
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-reservas')
DB_PATH = 'reservas.db'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# Configuración de Correo
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.office365.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'juan.llanca@ssr.cl')

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
        inicio, fin = b.split('-')
        bloque_a_hora[b] = (inicio + ":00", fin + ":00")

def format_d_mm_aaaa(fecha_iso):
    """Convierte YYYY-MM-DD a D-MM-AAAA"""
    try:
        y, m, d = fecha_iso.split('-')
        return f"{int(d)}-{m}-{y}"
    except:
        return fecha_iso

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sala TEXT,
        fecha TEXT,
        bloque TEXT,
        nombre TEXT,
        curso_tipo TEXT DEFAULT 'media',
        estado TEXT DEFAULT 'aprobada'
    )''')
    conn.commit()
    # Migracion automatica: agregar columnas si no existen
    for col, default in [('curso_tipo', 'media'), ('estado', 'aprobada'), ('curso_asistente', '')]:
        try:
            c.execute(f"ALTER TABLE reservas ADD COLUMN {col} TEXT DEFAULT '{default}'")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # La columna ya existe
    conn.close()

def enviar_correo_admin(sala, fecha, bloques, nombre, curso_tipo, curso_asistente):
    """Envía un correo de notificación al administrador cuando hay una reserva pendiente con diseño HTML."""
    fecha = format_d_mm_aaaa(fecha)
    if not MAIL_USERNAME or MAIL_USERNAME == '':
        print("Advertencia: No se envió correo porque no se han configurado las credenciales.")
        return

    msg = EmailMessage()
    msg['Subject'] = f'Reserva Pendiente de Confirmación: {sala}'
    msg['From'] = MAIL_USERNAME
    msg['To'] = ADMIN_EMAIL
    
    logo_cid = make_msgid()

    cuerpo_texto = f"""Estimado Administrador,
Se ha ingresado una nueva reserva que requiere su confirmación.
Sala: {sala}
Fecha: {fecha}
Bloques: {', '.join(bloques)}
Profesor/Usuario: {nombre}
Tipo de Curso: {curso_tipo}
Curso Asistente: {curso_asistente}
Por favor, revise el panel de administración para aprobar o rechazar esta solicitud.
Atte, Sistema de Reservas Automático"""
    msg.set_content(cuerpo_texto)

    cuerpo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            .header {{ background-color: #2b3a4a; padding: 20px; text-align: center; border-bottom: 4px solid #dc3545; }}
            .header img {{ max-width: 120px; height: auto; }}
            .content {{ padding: 30px; color: #333333; line-height: 1.6; font-size: 15px; }}
            .h2 {{ color: #2b3a4a; margin-top: 0; font-size: 22px; }}
            .badge {{ display: inline-block; padding: 6px 12px; border-radius: 4px; color: white; background-color: #dc3545; font-weight: bold; font-size: 14px; margin-bottom: 20px; }}
            .details-box {{ background-color: #f8f9fa; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0; }}
            .details-box ul {{ list-style-type: none; padding: 0; margin: 0; }}
            .details-box li {{ margin-bottom: 8px; }}
            .details-box strong {{ display: inline-block; width: 130px; color: #555555; }}
            .footer {{ background-color: #eeeeee; padding: 15px; text-align: center; font-size: 12px; color: #777777; border-top: 1px solid #dddddd; }}
            .action-text {{ font-size: 14px; margin-top: 25px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="cid:{logo_cid[1:-1]}" alt="Seminario San Rafael">
            </div>
            <div class="content">
                <h2 class="h2">Alerta de Aprobación</h2>
                <div class="badge">Requiere Revisión</div>
                <p>Estimado <strong>Administrador</strong>,</p>
                <p>Se ha registrado una nueva reserva conflictiva que requiere su confirmación manual en el panel de administración.</p>
                
                <div class="details-box">
                    <ul>
                        <li><strong>Profesor:</strong> {nombre}</li>
                        <li><strong>Tipo de Curso:</strong> {curso_tipo}</li>
                        <li><strong>Curso Asistente:</strong> {curso_asistente}</li>
                        <hr style="border: 0; border-top: 1px solid #ddd; margin: 10px 0;">
                        <li><strong>Sala:</strong> {sala}</li>
                        <li><strong>Fecha:</strong> {fecha}</li>
                        <li><strong>Bloques:</strong> {', '.join(bloques)}</li>
                    </ul>
                </div>
                
                <div class="action-text" style="text-align: center; margin-top: 35px; background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                    <p style="margin-top: 0;">Recuerde ingresar al panel de administración del sistema para aprobar o denegar esta solicitud.</p>
                    <a href="{url_for('admin', _external=True)}" style="display: inline-block; background-color: #dc3545; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 10px;">Ir al Panel de Administración</a>
                </div>
                
                <p style="margin-top: 30px;">Atentamente,<br><strong>Equipo Informatico SSR</strong></p>
            </div>
            <div class="footer">
                Este mensaje fue enviado automáticamente como alerta administrativa. No compartir con usuarios regulares.
            </div>
        </div>
    </body>
    </html>
    """
    msg.add_alternative(cuerpo_html, subtype='html')

    try:
        logo_path = os.path.join(app.root_path, 'static', 'descarga.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as img:
                img_data = img.read()
            msg.get_payload()[1].add_related(img_data, 'image', 'png', cid=logo_cid)
            
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
            print("Correo notificado al administrador con éxito.")
    except Exception as e:
        print(f"Error al enviar el correo al administrador: {e}")

def enviar_correo_usuario(correo_destino, nombre, sala, fecha, bloques, estado):
    """Envía un correo de confirmación al usuario que hizo la reserva con diseño HTML."""
    fecha = format_d_mm_aaaa(fecha)
    if not correo_destino or not MAIL_USERNAME or MAIL_USERNAME == '':
        return

    msg = EmailMessage()
    msg['Subject'] = 'Confirmación de Reserva - Seminario San Rafael'
    msg['From'] = MAIL_USERNAME
    msg['To'] = correo_destino

    logo_cid = make_msgid()
    estado_txt = "pendientes de aprobación por el administrador" if estado == "pendiente" else "aprobadas"
    color_estado = "#ffc107" if estado == "pendiente" else "#198754"
    badge_estado = "Pendiente de Aprobación" if estado == "pendiente" else "Reserva Aprobada"

    # Versión de texto simple para clientes que no soportan HTML
    cuerpo_texto = f"""Estimado/a {nombre},
Sus reservas han sido ingresadas correctamente en el sistema y se encuentran {estado_txt}.
Detalles: {sala} - Fecha: {fecha} - Bloques: {', '.join(bloques)}
Para cancelar contacte a: {ADMIN_EMAIL}
Atte, Sistema de Reservas SSR"""
    msg.set_content(cuerpo_texto)

    # Versión HTML bonita
    cuerpo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            .header {{ background-color: #2b3a4a; padding: 20px; text-align: center; border-bottom: 4px solid #0d6efd; }}
            .header img {{ max-width: 120px; height: auto; }}
            .content {{ padding: 30px; color: #333333; line-height: 1.6; font-size: 15px; }}
            .h2 {{ color: #2b3a4a; margin-top: 0; font-size: 22px; }}
            .badge {{ display: inline-block; padding: 6px 12px; border-radius: 4px; color: white; background-color: {color_estado}; font-weight: bold; font-size: 14px; margin-bottom: 20px; }}
            .details-box {{ background-color: #f8f9fa; border-left: 4px solid #0d6efd; padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0; }}
            .details-box ul {{ list-style-type: none; padding: 0; margin: 0; }}
            .details-box li {{ margin-bottom: 8px; }}
            .details-box strong {{ color: #555555; display: inline-block; width: 80px; }}
            .footer {{ background-color: #eeeeee; padding: 15px; text-align: center; font-size: 12px; color: #777777; border-top: 1px solid #dddddd; }}
            .cancel-text {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; color: #856404; font-size: 14px; margin-top: 25px; border-left: 3px solid #ffeeba; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="cid:{logo_cid[1:-1]}" alt="Seminario San Rafael">
            </div>
            <div class="content">
                <h2 class="h2">Comprobante de Reserva</h2>
                <div class="badge">{badge_estado}</div>
                <p>Estimado/a <strong>{nombre}</strong>,</p>
                <p>Le informamos que su solicitud ha sido ingresada de forma exitosa en el <strong>Sistema de Reservas SSR 2026</strong>.</p>
                
                <div class="details-box">
                    <ul>
                        <li><strong>Sala:</strong> {sala}</li>
                        <li><strong>Fecha:</strong> {fecha}</li>
                        <li><strong>Bloques:</strong> {', '.join(bloques)}</li>
                    </ul>
                </div>
                
                <div class="cancel-text">
                    <strong>¿Necesita cancelar?</strong><br>
                    Si por algún motivo desea anular esta reserva, por favor comuníquese directamente con el administrador a través del correo: <a href="mailto:{ADMIN_EMAIL}">{ADMIN_EMAIL}</a>
                </div>
                
                <p style="margin-top: 30px;">Atentamente,<br><strong>Equipo Informatico SSR</strong></p>
            </div>
            <div class="footer">
                Este correo fue generado y enviado de manera automática. Por favor no responder directamente a esta dirección.
            </div>
        </div>
    </body>
    </html>
    """
    msg.add_alternative(cuerpo_html, subtype='html')

    try:
        # Adjuntar la imagen inline para que se vea sin necesidad de descargar
        logo_path = os.path.join(app.root_path, 'static', 'descarga.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as img:
                img_data = img.read()
            msg.get_payload()[1].add_related(img_data, 'image', 'png', cid=logo_cid)
        else:
            print(f"Advertencia: El logo en {logo_path} no se encuentra.")

        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
            print(f"Correo de confirmación enviado a {correo_destino}.")
    except Exception as e:
        print(f"Error al enviar confirmación al usuario {correo_destino}: {e}")

def enviar_correo_resolucion(correo_destino, nombre, sala, fecha, bloque, resolucion, motivo=""):
    """Envía un correo cuando el administrador aprueba o rechaza una reserva específica."""
    fecha = format_d_mm_aaaa(fecha)
    if not correo_destino or not MAIL_USERNAME or MAIL_USERNAME == '':
        return

    msg = EmailMessage()
    msg['Subject'] = f'Resolución de Reserva: {resolucion.capitalize()}'
    msg['From'] = MAIL_USERNAME
    msg['To'] = correo_destino
    
    logo_cid = make_msgid()
    color_estado = "#198754" if resolucion == "aprobada" else "#dc3545"
    badge_estado = "Reserva Aprobada" if resolucion == "aprobada" else "Reserva Rechazada/Cancelada"
    mensaje_accion = "ha sido <strong>APROBADA</strong>" if resolucion == "aprobada" else "ha sido <strong>RECHAZADA o CANCELADA</strong>"

    cuerpo_texto = f"Su solicitud de reserva en {sala} el {fecha} ({bloque}) ha sido {resolucion.upper()}."
    if motivo:
        cuerpo_texto += f"\nMotivo del rechazo: {motivo}"
    msg.set_content(cuerpo_texto)

    cuerpo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            .header {{ background-color: #2b3a4a; padding: 20px; text-align: center; border-bottom: 4px solid {color_estado}; }}
            .header img {{ max-width: 120px; height: auto; }}
            .content {{ padding: 30px; color: #333333; line-height: 1.6; font-size: 15px; }}
            .h2 {{ color: #2b3a4a; margin-top: 0; font-size: 22px; }}
            .badge {{ display: inline-block; padding: 6px 12px; border-radius: 4px; color: white; background-color: {color_estado}; font-weight: bold; font-size: 14px; margin-bottom: 20px; }}
            .details-box {{ background-color: #f8f9fa; border-left: 4px solid {color_estado}; padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0; }}
            .details-box ul {{ list-style-type: none; padding: 0; margin: 0; }}
            .details-box li {{ margin-bottom: 8px; }}
            .details-box strong {{ color: #555555; display: inline-block; width: 80px; }}
            .footer {{ background-color: #eeeeee; padding: 15px; text-align: center; font-size: 12px; color: #777777; border-top: 1px solid #dddddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="cid:{logo_cid[1:-1]}" alt="Seminario San Rafael">
            </div>
            <div class="content">
                <h2 class="h2" style="color: {color_estado};">Resolución de Reserva</h2>
                <div class="badge" style="background-color: {color_estado};">{badge_estado}</div>
                <p>Estimado/a <strong>{nombre}</strong>,</p>
                <p>Le informamos que su solicitud para la siguiente reserva {mensaje_accion} por la administración.</p>
                
                <div class="details-box" style="border-left: 4px solid {color_estado};">
                    <ul>
                        <li><strong>Sala:</strong> {sala}</li>
                        <li><strong>Fecha:</strong> {fecha}</li>
                        <li><strong>Bloque:</strong> {bloque}</li>
                    </ul>
                </div>
                
                {f'<div class="cancel-text" style="background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; border-left: 4px solid #ffeeba; margin-top: 20px;"><strong>Comentario del Administrador:</strong><br>{motivo}</div>' if motivo else ''}
                
                {"<p style='margin-top: 20px;'>Si cree que esto es un error o necesita agendar en otro horario, por favor comuníquese con el administrador.</p>" if resolucion == "rechazada" else ""}
                
                <p style="margin-top: 30px;">Atentamente,<br><strong>Equipo Informatico SSR</strong></p>
            </div>
            <div class="footer">Este correo fue generado automáticamente. Por favor no responder a esta dirección.</div>
        </div>
    </body>
    </html>
    """
    msg.add_alternative(cuerpo_html, subtype='html')

    try:
        logo_path = os.path.join(app.root_path, 'static', 'descarga.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as img:
                msg.get_payload()[1].add_related(img.read(), 'image', 'png', cid=logo_cid)
                
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
            print(f"Correo de resolución enviado a {correo_destino}.")
    except Exception as e:
        print(f"Error al enviar correo de resolución a {correo_destino}: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    if request.method == 'POST':
        sala = request.form.get('sala')
        fecha = request.form.get('fecha')
        bloques_str = request.form.get('bloque')
        nombre = request.form.get('nombre')

        if not (sala and fecha and bloques_str and nombre):
            flash('Faltan campos por completar', 'danger')
            return redirect(url_for('index'))

        fecha_obj = date.fromisoformat(fecha)
        if fecha_obj > date.today() + timedelta(days=30):
            flash('No se puede reservar con más de 30 días de anticipación.', 'danger')
            return redirect(url_for('index'))

        curso_tipo = request.form.get('curso_tipo')
        curso_nivel = request.form.get('curso_nivel', '')
        curso_seccion = request.form.get('curso_seccion', '')
        curso_asistente = f"{curso_nivel} {curso_seccion}".strip()
        
        if not curso_tipo:
            flash('Debes indicar el nivel de curso.', 'danger')
            return redirect(url_for('index'))

        bloques_seleccionados = [b.strip() for b in bloques_str.split(',') if b.strip()]

        # Determinar estado segun compatibilidad sala/curso
        tipo_sala = salas_disponibles.get(sala, {}).get('tipo', '')
        estado = 'aprobada'

        if tipo_sala and curso_tipo != tipo_sala:
            # Calcular la diferencia de horas
            primer_bloque = bloques_seleccionados[0] if bloques_seleccionados else ''
            inicio = bloque_a_hora.get(primer_bloque, ("08:00:00", "08:45:00"))[0]
            
            try:
                reserva_dt_str = f"{fecha} {inicio}"
                reserva_dt = datetime.strptime(reserva_dt_str, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                
                if (reserva_dt - now) <= timedelta(hours=48):
                    estado = 'pendiente'
            except Exception:
                # Fallback por si hay error en el formato
                estado = 'pendiente'

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for bloque in bloques_seleccionados:
            c.execute("SELECT * FROM reservas WHERE sala=? AND fecha=? AND bloque=?", (sala, fecha, bloque))
            if c.fetchone():
                flash(f'Bloque {bloque} ya está reservado para esa sala.', 'danger')
                conn.close()
                return redirect(url_for('index'))

        for bloque in bloques_seleccionados:
            c.execute("INSERT INTO reservas (sala, fecha, bloque, nombre, curso_tipo, estado, curso_asistente) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (sala, fecha, bloque, nombre, curso_tipo, estado, curso_asistente))
        
        # Buscar el correo del profesor/usuario
        c.execute("SELECT correo FROM usuarios WHERE nombre=?", (nombre,))
        row_usuario = c.fetchone()
        correo_usuario = row_usuario[0] if row_usuario and row_usuario[0] else None

        conn.commit()
        conn.close()

        if estado == 'pendiente':
            enviar_correo_admin(sala, fecha, bloques_seleccionados, nombre, curso_tipo, curso_asistente)
            flash(f'Reserva enviada y pendiente de aprobación del administrador porque su reserva es con menos de 48 hrs de anticipación a sala que no corresponde a su tipo de curso(sala de {tipo_sala} con curso de {curso_tipo}).', 'warning')
        else:
            flash('Reserva realizada con éxito.', 'success')
            
        # Enviar siempre el correo al usuario confirmando que se ingresó
        if correo_usuario:
            enviar_correo_usuario(correo_usuario, nombre, sala, fecha, bloques_seleccionados, estado)

        return redirect(url_for('index'))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM reservas")
    reservas_db = c.fetchall()
    # Obtener lista de usuarios para el autocompletado
    try:
        c.execute("SELECT nombre FROM usuarios ORDER BY nombre")
        lista_usuarios = [row[0] for row in c.fetchall()]
    except Exception:
        lista_usuarios = []
    conn.close()

    eventos = []
    for r in reservas_db:
        sala_nombre = r[1]
        tipo = salas_disponibles.get(sala_nombre, {}).get("tipo", "otro")

        # Usar el mismo color definido en salas_disponibles (igual que "Nuestras Salas")
        color = salas_disponibles.get(sala_nombre, {}).get("color", "#6c757d")

        # Reservas pendientes se muestran en gris
        estado_reserva = r[6] if len(r) > 6 else 'aprobada'
        if estado_reserva == 'pendiente':
            color = '#adb5bd'  # gris claro para pendientes

        bloque = r[3]
        fecha = r[2]
        inicio, fin = bloque_a_hora.get(bloque, ("08:00:00", "08:45:00"))
        start_datetime = f"{fecha}T{inicio}"
        end_datetime = f"{fecha}T{fin}"

        curso_tipo_reserva = r[5] if len(r) > 5 else ''
        curso_asistente = r[7] if len(r) > 7 else ''
        
        docente = r[4]
        titulo_evento = f"{docente} - {sala_nombre} - {bloque}"
        if curso_asistente:
            titulo_evento += f" ({curso_asistente})"

        eventos.append({
            'title': titulo_evento,
            'start': start_datetime,
            'end': end_datetime,
            'color': color,
            'extendedProps': {
                'nombre': docente,
                'sala': sala_nombre,
                'bloque': bloque,
                'estado': estado_reserva,
                'curso_tipo': curso_tipo_reserva,
                'curso_asistente': curso_asistente
            }
        })

    # Calcular fechas para los límites del formulario
    hoy = date.today()
    fecha_min = hoy.isoformat()
    fecha_max = (hoy + timedelta(days=30)).isoformat()

    return render_template('index.html',
                           salas=salas_disponibles,
                           bloques=bloques,
                           eventos=eventos,
                           fecha_min=fecha_min,
                           fecha_max=fecha_max,
                           lista_usuarios=lista_usuarios)

@app.route('/api/bloques-ocupados')
def api_bloques_ocupados():
    sala = request.args.get('sala')
    fecha = request.args.get('fecha')
    
    if not sala or not fecha:
        return jsonify({'bloques_ocupados': []})
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT bloque FROM reservas WHERE sala=? AND fecha=?", (sala, fecha))
    bloques_ocupados = [row[0] for row in c.fetchall()]
    conn.close()
    
    return jsonify({'bloques_ocupados': bloques_ocupados})

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM reservas ORDER BY estado DESC, fecha, bloque")
    reservas = [
        dict(id=row[0], sala=row[1], fecha=format_d_mm_aaaa(row[2]), bloque=row[3], nombre=row[4],
             curso_tipo=row[5] if len(row) > 5 else 'media',
             estado=row[6] if len(row) > 6 else 'aprobada')
        for row in c.fetchall()
    ]
    conn.close()
    pendientes = [r for r in reservas if r['estado'] == 'pendiente']
    return render_template('admin.html', reservas=reservas, pendientes=pendientes)


@app.route('/aprobar/<int:id>')
def aprobar(id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Extraer información para el correo
    c.execute("SELECT sala, fecha, bloque, nombre FROM reservas WHERE id=?", (id,))
    reserva = c.fetchone()

    c.execute("UPDATE reservas SET estado='aprobada' WHERE id=?", (id,))
    
    if reserva:
        sala, fecha, bloque, nombre = reserva
        c.execute("SELECT correo FROM usuarios WHERE nombre=?", (nombre,))
        row_usuario = c.fetchone()
        if row_usuario and row_usuario[0]:
            enviar_correo_resolucion(row_usuario[0], nombre, sala, fecha, bloque, "aprobada")

    conn.commit()
    conn.close()
    flash('Reserva aprobada exitosamente.', 'success')
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Extraer información antes de borrar
    c.execute("SELECT sala, fecha, bloque, nombre FROM reservas WHERE id=?", (id,))
    reserva = c.fetchone()

    c.execute("DELETE FROM reservas WHERE id=?", (id,))

    if reserva:
        sala, fecha, bloque, nombre = reserva
        motivo = request.args.get('motivo', '').strip()
        c.execute("SELECT correo FROM usuarios WHERE nombre=?", (nombre,))
        row_usuario = c.fetchone()
        if row_usuario and row_usuario[0]:
            enviar_correo_resolucion(row_usuario[0], nombre, sala, fecha, bloque, "rechazada", motivo)

    conn.commit()
    conn.close()
    flash('Reserva eliminada con éxito.', 'success')
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        clave = request.form.get('clave')
        if clave == ADMIN_PASSWORD:
            session['admin'] = True
            flash('Acceso concedido.', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Clave incorrecta.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=31, debug=True)