from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app.main import main_bp
from app import db
from app.models import Reserva, Sala, User, AuditLog, get_bloques_por_tipo
from app.forms import ReservaForm
from config import Config
import uuid

@main_bp.route('/')
def index():
    """Página de inicio - redirige según autenticación"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    from datetime import datetime, timedelta
    from sqlalchemy import func, desc
    
    # Estadísticas del usuario
    mis_reservas_count = Reserva.query.filter_by(user_id=current_user.id).count()
    salas_count = Sala.query.filter_by(activa=True).count()
    reservas_pendientes_usuario = Reserva.query.filter_by(
        user_id=current_user.id,
        estado='pendiente'
    ).count()
    
    # ✅ OPTIMIZADO: Próximas reservas con eager loading y límite
    hoy = datetime.now().date()
    mis_reservas = Reserva.query.options(
        db.joinedload(Reserva.sala)
    ).filter(
        Reserva.user_id == current_user.id,
        Reserva.fecha >= hoy
    ).order_by(Reserva.fecha, Reserva.bloque).limit(10).all()  # Límite de 10
    
    # Total de reservas del usuario
    total_mis_reservas = Reserva.query.filter_by(user_id=current_user.id).count()
    
    # Reservas pendientes de aprobación (si es admin/coordinador)
    reservas_pendientes_admin = 0
    if current_user.is_coordinador():
        reservas_pendientes_admin = Reserva.query.filter_by(estado='pendiente').count()
    
    # ✅ OPTIMIZADO: Salas más usadas con límite
    from sqlalchemy import func
    salas_populares = db.session.query(
        Sala.nombre, func.count(Reserva.id).label('total')
    ).join(Reserva).group_by(Sala.id).order_by(
        func.count(Reserva.id).desc()
    ).limit(5).all()  # Límite de 5 salas
    
    return render_template('main/dashboard.html',
                         mis_reservas=mis_reservas,
                         total_mis_reservas=total_mis_reservas,
                         reservas_pendientes=reservas_pendientes_admin,
                         salas_populares=salas_populares,
                         mis_reservas_count=mis_reservas_count,
                         salas_count=salas_count)

@main_bp.route('/calendario')
@login_required
def calendario():
    """Vista de calendario con todas las reservas"""
    salas = Sala.query.filter_by(activa=True).all()
    
    # Obtener todas las reservas aprobadas
    reservas = Reserva.query.filter_by(estado='aprobada').all()
    
    # Convertir a formato FullCalendar
    eventos = []
    for r in reservas:
        # Parsear bloque para obtener hora inicio y fin
        inicio, fin = r.bloque.split('-')
        
        eventos.append({
            'id': r.id,
            'title': f"{r.sala.nombre} - {r.usuario.nombre}",
            'start': f"{r.fecha.isoformat()}T{inicio}:00",
            'end': f"{r.fecha.isoformat()}T{fin}:00",
            'backgroundColor': r.sala.color,
            'borderColor': r.sala.color,
            'extendedProps': {
                'sala': r.sala.nombre,
                'usuario': r.usuario.nombre,
                'motivo': r.motivo,
                'notas': r.notas or ''
            }
        })
    
    return render_template('main/calendario.html', salas=salas, eventos=eventos)

@main_bp.route('/nueva-reserva', methods=['GET', 'POST'])
@login_required
def nueva_reserva():
    """Crear nueva reserva"""
    form = ReservaForm()
    
    # Cargar salas activas
    salas = Sala.query.filter_by(activa=True).all()
    form.sala_id.choices = [(s.id, f"{s.nombre} (Cap: {s.capacidad})") for s in salas]
    
    if form.validate_on_submit():
        sala = Sala.query.get(form.sala_id.data)
        fecha_reserva = form.fecha.data
        
        # NUEVA VALIDACIÓN: Límite de 30 días
        hoy = datetime.now().date()
        fecha_maxima = hoy + timedelta(days=30)
        
        if fecha_reserva < hoy:
            flash('No puedes reservar en fechas pasadas.', 'danger')
            return redirect(url_for('main.nueva_reserva'))
        
        if fecha_reserva > fecha_maxima:
            flash(f'No puedes reservar con más de 30 días de anticipación. Fecha máxima: {fecha_maxima.strftime("%d/%m/%Y")}', 'danger')
            return redirect(url_for('main.nueva_reserva'))
        
        # Procesar bloques seleccionados
        bloques_str = form.bloques.data
        if not bloques_str:
            flash('Debes seleccionar al menos un bloque.', 'danger')
            return redirect(url_for('main.nueva_reserva'))
        
        # Original max_dias validation, now using the 'hoy' defined above
        max_dias = Config.RESERVAS_MAX_DIAS_ANTICIPACION
        if fecha_reserva > hoy + timedelta(days=max_dias):
            flash(f'No puedes reservar con más de {max_dias} días de anticipación.', 'danger')
            return redirect(url_for('main.nueva_reserva'))
        
        # Crear reservas
        # Parsear bloques desde string separado por comas
        bloques_str = form.bloques.data
        bloques_seleccionados = [b.strip() for b in bloques_str.split(',') if b.strip()]
        recurrencia_id = str(uuid.uuid4()) if form.es_recurrente.data else None
        
        # Determinar fechas según recurrencia
        fechas = [fecha_reserva]
        if form.es_recurrente.data and form.recurrencia_tipo.data:
            cantidad = form.recurrencia_cantidad.data or 1
            delta_dias = 7 if form.recurrencia_tipo.data == 'semanal' else 14
            
            for i in range(1, cantidad):
                nueva_fecha = fecha_reserva + timedelta(days=delta_dias * i)
                if nueva_fecha <= hoy + timedelta(days=max_dias):
                    fechas.append(nueva_fecha)
        
        # Verificar conflictos
        for fecha in fechas:
            for bloque in bloques_seleccionados:
                conflicto = Reserva.query.filter_by(
                    sala_id=sala.id,
                    fecha=fecha,
                    bloque=bloque
                ).filter(Reserva.estado.in_(['pendiente', 'aprobada'])).first()
                
                if conflicto:
                    flash(f'El bloque {bloque} del {fecha} ya está reservado.', 'danger')
                    return redirect(url_for('main.nueva_reserva'))
        
        # Determinar estado inicial basado en configuración
        estado_inicial_config = 'pendiente' if Config.RESERVAS_REQUIEREN_APROBACION else 'aprobada'
        alguna_pendiente_por_prioridad = False
        
        # Crear reservas
        for fecha in fechas:
            for bloque in bloques_seleccionados:
                # Por defecto, estado según configuración
                estado_reserva_actual = estado_inicial_config
                
                if current_user.rol == 'administrativo':
                    estado_reserva_actual = 'aprobada'
                # Salas tipo 'normal' siempre se aprueban automáticamente (sin restricción de horas)
                elif sala.tipo == 'normal':
                    estado_reserva_actual = 'aprobada'
                # SOLO para salas de computación (tipo='basica' o 'media'): verificar prioridad
                elif sala.tipo in ['basica', 'media']:
                    # Es una sala de computación, aplicar lógica de prioridad
                    curso_asistente = form.curso_asistente.data
                    
                    if curso_asistente:
                        # Extraer el nivel del curso (ej: "1B" de "1B-A")
                        nivel_curso = curso_asistente.split('-')[0] if '-' in curso_asistente else curso_asistente
                        
                        # Determinar si es básica o media
                        es_curso_basica = nivel_curso.endswith('B')  # Termina en B (ej: 1B, 2B, etc.)
                        es_curso_media = nivel_curso.endswith('M')   # Termina en M (ej: 1M, 2M, etc.)
                        
                        # Verificar si hay mismatch (curso no coincide con tipo de sala)
                        hay_mismatch = (es_curso_basica and sala.tipo == 'media') or (es_curso_media and sala.tipo == 'basica')
                        
                        if hay_mismatch:
                            # Curso NO coincide → Verificar anticipación de 24 horas
                            ahora = datetime.now()
                            fecha_hora_reserva = datetime.combine(fecha, datetime.min.time())
                            diferencia_horas = (fecha_hora_reserva - ahora).total_seconds() / 3600
                            
                            if diferencia_horas < 24:
                                # Menos de 24 horas → Pendiente
                                estado_reserva_actual = 'pendiente'
                                alguna_pendiente_por_prioridad = True
                            else:
                                # 24+ horas → Pendiente (para aprobación manual)
                                estado_reserva_actual = 'pendiente'
                                alguna_pendiente_por_prioridad = True
                        else:
                            # Curso SÍ coincide → Aprobada automáticamente (sin restricción de horas)
                            estado_reserva_actual = 'aprobada'
                
                # Crear la reserva
                reserva = Reserva(
                    sala_id=sala.id,
                    user_id=current_user.id,
                    fecha=fecha,
                    bloque=bloque,
                    motivo=form.motivo.data,
                    curso_asistente=form.curso_asistente.data if form.curso_asistente.data else None,
                    notas=form.notas.data,
                    estado=estado_reserva_actual,
                    es_recurrente=form.es_recurrente.data,
                    recurrencia_tipo=form.recurrencia_tipo.data if form.es_recurrente.data else None
                )
                db.session.add(reserva)
        
        # Log de auditoría
        log = AuditLog(
            user_id=current_user.id,
            accion='crear_reserva',
            entidad='reserva',
            detalles=f'Reserva de {sala.nombre} para {len(fechas)} fecha(s), {len(bloques_seleccionados)} bloque(s)',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        # Enviar emails de notificación
        from app.utils.email import send_reserva_confirmacion, send_reserva_notificacion_admin
        try:
            # Email al usuario (se envía para la última reserva creada)
            send_reserva_confirmacion(reserva)
            # Email al administrador
            send_reserva_notificacion_admin(reserva)
        except Exception as e:
            print(f"Error al enviar emails: {e}")
        
        # Mensaje personalizado según el resultado
        if alguna_pendiente_por_prioridad:
            # Usar modal en lugar de flash para mensajes de pendiente
            session['mostrar_modal_pendiente'] = True
        elif estado_reserva_actual == 'aprobada':
            # Usar modal para reservas aprobadas automáticamente
            session['mostrar_modal_aprobada'] = True
        else:
            flash('Reserva creada exitosamente. Tu reserva está pendiente de aprobación.', 'info')
        
        return redirect(url_for('main.nueva_reserva'))
    
    return render_template('main/nueva_reserva.html', 
                         form=form, 
                         now=datetime.now(),
                         timedelta=timedelta)


@main_bp.route('/mis-reservas')
@login_required
def mis_reservas():
    """Ver mis reservas"""
    page = request.args.get('page', 1, type=int)
    
    reservas = Reserva.query.filter_by(user_id=current_user.id).order_by(
        Reserva.fecha.desc(), Reserva.bloque
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('main/mis_reservas.html', reservas=reservas)

@main_bp.route('/cancelar-reserva/<int:id>', methods=['POST'])
@login_required
def cancelar_reserva(id):
    """Cancelar una reserva"""
    reserva = Reserva.query.get_or_404(id)
    
    # Verificar permisos
    if reserva.user_id != current_user.id and not current_user.is_coordinador():
        flash('No tienes permiso para cancelar esta reserva.', 'danger')
        return redirect(url_for('main.mis_reservas'))
    
    # No permitir cancelar reservas pasadas
    if reserva.fecha < date.today():
        flash('No puedes cancelar reservas pasadas.', 'warning')
        return redirect(url_for('main.mis_reservas'))
    
    reserva.estado = 'cancelada'
    
    # Log de auditoría
    log = AuditLog(
        user_id=current_user.id,
        accion='cancelar_reserva',
        entidad='reserva',
        entidad_id=reserva.id,
        detalles=f'Reserva cancelada: {reserva.sala.nombre} - {reserva.fecha}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Reserva cancelada exitosamente.', 'success')
    return redirect(url_for('main.mis_reservas'))
