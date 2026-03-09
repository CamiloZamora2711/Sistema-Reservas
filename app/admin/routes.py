from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.admin import admin_bp
from app import db
from app.models import User, Sala, Reserva, AuditLog
from app.forms import EditarUsuarioForm, SalaForm, AprobarReservaForm

def admin_required(f):
    """Decorador para requerir rol de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Necesitas permisos de administrador para acceder a esta página.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def coordinador_required(f):
    """Decorador para requerir rol de coordinador o admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_coordinador():
            flash('Necesitas permisos de coordinador para acceder a esta página.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/panel')
@login_required
@coordinador_required
def panel():
    """Panel de administración principal"""
    # Estadísticas
    total_usuarios = User.query.count()
    total_salas = Sala.query.filter_by(activa=True).count()
    total_reservas = Reserva.query.count()
    reservas_pendientes = Reserva.query.filter_by(estado='pendiente').count()
    
    # Últimas reservas
    ultimas_reservas = Reserva.query.order_by(Reserva.created_at.desc()).limit(10).all()
    
    # Últimos logs
    ultimos_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(15).all()
    
    return render_template('admin/panel.html',
                         total_usuarios=total_usuarios,
                         total_salas=total_salas,
                         total_reservas=total_reservas,
                         reservas_pendientes=reservas_pendientes,
                         ultimas_reservas=ultimas_reservas,
                         ultimos_logs=ultimos_logs)

@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_usuario():
    """Crear nuevo usuario (solo admin)"""
    from app.forms import RegistroForm
    form = RegistroForm()
    
    if form.validate_on_submit():
        # Verificar si el email ya existe
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Este email ya está registrado.', 'danger')
            return render_template('admin/nuevo_usuario.html', form=form)
        
        # Crear nuevo usuario
        usuario = User(
            email=form.email.data,
            nombre=form.nombre.data,
            rol=form.rol.data,
            curso=form.curso.data if form.curso.data else None,
            activo=form.activo.data if hasattr(form, 'activo') else True
        )
        usuario.set_password(form.password.data)
        
        db.session.add(usuario)
        
        # Log de auditoría
        log = AuditLog(
            user_id=current_user.id,
            accion='crear_usuario',
            entidad='user',
            detalles=f'Creó usuario: {usuario.nombre} ({usuario.email}) con rol {usuario.rol}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Usuario {usuario.nombre} creado exitosamente.', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/nuevo_usuario.html', form=form)

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    """Gestión de usuarios"""
    page = request.args.get('page', 1, type=int)
    
    # Consulta simple sin eager loading (evita problemas de compatibilidad)
    usuarios = User.query.order_by(User.created_at.desc()).paginate(
        page=page, 
        per_page=20,
        error_out=False
    )
    
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(id):
    """Editar usuario"""
    usuario = User.query.get_or_404(id)
    form = EditarUsuarioForm(obj=usuario)
    
    if form.validate_on_submit():
        usuario.nombre = form.nombre.data
        usuario.email = form.email.data.lower()
        usuario.rol = form.rol.data  # Actualizar el rol
        usuario.curso = form.curso.data if form.curso.data else None
        usuario.activo = form.activo.data
        
        # Log de auditoría
        log = AuditLog(
            user_id=current_user.id,
            accion='editar_usuario',
            entidad='user',
            entidad_id=usuario.id,
            detalles=f'Editó usuario: {usuario.nombre} (Rol: {usuario.rol})',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/editar_usuario.html', form=form, usuario=usuario)

@admin_bp.route('/usuarios/resetear-password/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def resetear_password(id):
    """Resetear contraseña de usuario"""
    usuario = User.query.get_or_404(id)
    
    if request.method == 'POST':
        nueva_password = request.form.get('nueva_password')
        confirmar_password = request.form.get('confirmar_password')
        
        # Validar que las contraseñas coincidan
        if not nueva_password or not confirmar_password:
            flash('Debes ingresar la nueva contraseña y confirmarla.', 'danger')
            return redirect(url_for('admin.resetear_password', id=id))
        
        if nueva_password != confirmar_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('admin.resetear_password', id=id))
        
        # Validar longitud mínima
        if len(nueva_password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            return redirect(url_for('admin.resetear_password', id=id))
        
        # Actualizar contraseña
        usuario.set_password(nueva_password)
        
        # Log de auditoría
        log = AuditLog(
            user_id=current_user.id,
            accion='resetear_password',
            entidad='user',
            entidad_id=usuario.id,
            detalles=f'Contraseña reseteada para usuario: {usuario.email}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Contraseña reseteada exitosamente. Nueva contraseña: ' + nueva_password, 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/resetear_password.html', usuario=usuario)

@admin_bp.route('/usuarios/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario(id):
    """Eliminar usuario"""
    usuario = User.query.get_or_404(id)
    
    # No permitir eliminar al usuario actual
    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('admin.usuarios'))
    
    # Verificar si el usuario tiene reservas
    reservas_count = Reserva.query.filter_by(user_id=usuario.id).count()
    
    if reservas_count > 0:
        flash(f'No se puede eliminar el usuario porque tiene {reservas_count} reserva(s) asociada(s). Primero elimina o reasigna sus reservas.', 'warning')
        return redirect(url_for('admin.usuarios'))
    
    nombre_usuario = usuario.nombre
    email_usuario = usuario.email
    
    # Log de auditoría
    log = AuditLog(
        user_id=current_user.id,
        accion='eliminar_usuario',
        entidad='user',
        entidad_id=usuario.id,
        detalles=f'Eliminó usuario: {nombre_usuario} ({email_usuario})',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    # Eliminar usuario
    db.session.delete(usuario)
    db.session.commit()
    
    flash(f'Usuario {nombre_usuario} eliminado exitosamente.', 'success')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/salas')
@login_required
@coordinador_required
def salas():
    """Gestión de salas"""
    salas = Sala.query.all()
    return render_template('admin/salas.html', salas=salas)

@admin_bp.route('/salas/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def nueva_sala():
    """Crear nueva sala"""
    form = SalaForm()
    
    if form.validate_on_submit():
        sala = Sala(
            nombre=form.nombre.data,
            capacidad=form.capacidad.data,
            tipo=form.tipo.data,
            descripcion=form.descripcion.data,
            color=form.color.data,
            activa=form.activa.data
        )
        
        db.session.add(sala)
        
        # Log de auditoría
        log = AuditLog(
            user_id=current_user.id,
            accion='crear_sala',
            entidad='sala',
            detalles=f'Nueva sala creada: {sala.nombre}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Sala creada exitosamente.', 'success')
        return redirect(url_for('admin.salas'))
    
    return render_template('admin/sala_form.html', form=form, titulo='Nueva Sala')

@admin_bp.route('/salas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_sala(id):
    """Editar sala"""
    sala = Sala.query.get_or_404(id)
    form = SalaForm(obj=sala)
    
    if form.validate_on_submit():
        sala.nombre = form.nombre.data
        sala.capacidad = form.capacidad.data
        sala.tipo = form.tipo.data
        sala.descripcion = form.descripcion.data
        sala.color = form.color.data
        sala.activa = form.activa.data
        
        # Log de auditoría
        log = AuditLog(
            user_id=current_user.id,
            accion='editar_sala',
            entidad='sala',
            entidad_id=sala.id,
            detalles=f'Sala editada: {sala.nombre}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Sala actualizada exitosamente.', 'success')
        return redirect(url_for('admin.salas'))
    
    return render_template('admin/sala_form.html', form=form, titulo='Editar Sala', sala=sala)

@admin_bp.route('/aprobaciones')
@login_required
@coordinador_required
def aprobaciones():
    """Gestión de aprobaciones de reservas"""
    page = request.args.get('page', 1, type=int)
    reservas_pendientes = Reserva.query.filter_by(estado='pendiente').order_by(
        Reserva.fecha, Reserva.bloque
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/aprobaciones.html', reservas=reservas_pendientes)

@admin_bp.route('/aprobar-reserva/<int:id>', methods=['POST'])
@login_required
@coordinador_required
def aprobar_reserva(id):
    """Aprobar o rechazar reserva"""
    reserva = Reserva.query.get_or_404(id)
    accion = request.form.get('accion')
    notas = request.form.get('notas', '')
    
    if accion == 'aprobar':
        reserva.estado = 'aprobada'
        reserva.aprobada_por_id = current_user.id
        mensaje = 'Reserva aprobada exitosamente.'
        accion_log = 'aprobar_reserva'
        detalles_log = f'Aprobó reserva de {reserva.usuario.nombre} para {reserva.sala.nombre}'
    elif accion == 'rechazar':
        reserva.estado = 'rechazada'
        mensaje = 'Reserva rechazada.'
        accion_log = 'rechazar_reserva'
        detalles_log = f'Rechazó reserva de {reserva.usuario.nombre} para {reserva.sala.nombre}'
    else:
        flash('Acción no válida.', 'danger')
        return redirect(url_for('admin.aprobaciones'))
    
    # Log de auditoría
    log = AuditLog(
        user_id=current_user.id,
        accion=accion_log,
        entidad='reserva',
        entidad_id=reserva.id,
        detalles=detalles_log,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    # Enviar email al usuario
    if accion == 'aprobar':
        from app.utils.email import send_reserva_aprobada
        try:
            send_reserva_aprobada(reserva)
        except Exception as e:
            print(f"Error al enviar email de aprobación: {e}")
    elif accion == 'rechazar':
        from app.utils.email import send_reserva_rechazada
        try:
            send_reserva_rechazada(reserva)
        except Exception as e:
            print(f"Error al enviar email de rechazo: {e}")
    
    flash(mensaje, 'success')
    return redirect(url_for('admin.aprobaciones'))

@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    """Ver logs de auditoría"""
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('admin/logs.html', logs=logs)

@admin_bp.route('/reservas')
@login_required
@coordinador_required
def reservas():
    """Ver todas las reservas del sistema"""
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', '')
    sala_id = request.args.get('sala_id', type=int)
    
    # Query base
    query = Reserva.query
    
    # Filtros
    if estado:
        query = query.filter_by(estado=estado)
    if sala_id:
        query = query.filter_by(sala_id=sala_id)
    
    # Ordenar y paginar
    reservas = query.order_by(Reserva.fecha.desc(), Reserva.bloque).paginate(
        page=page, per_page=30, error_out=False
    )
    
    # Obtener salas para el filtro
    salas = Sala.query.filter_by(activa=True).all()
    
    return render_template('admin/reservas.html', 
                         reservas=reservas, 
                         salas=salas,
                         estado_filtro=estado,
                         sala_filtro=sala_id)

@admin_bp.route('/eliminar-reserva/<int:id>', methods=['POST'])
@login_required
@coordinador_required
def eliminar_reserva(id):
    """Eliminar una reserva (solo admin/coordinador)"""
    reserva = Reserva.query.get_or_404(id)
    
    # Guardar información para el log antes de eliminar
    info_reserva = f'{reserva.sala.nombre} - {reserva.fecha} {reserva.bloque} - Usuario: {reserva.usuario.nombre}'
    
    # Log de auditoría
    log = AuditLog(
        user_id=current_user.id,
        accion='eliminar_reserva',
        entidad='reserva',
        entidad_id=reserva.id,
        detalles=f'Reserva eliminada: {info_reserva}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    # Eliminar reserva
    db.session.delete(reserva)
    db.session.commit()
    
    flash('Reserva eliminada exitosamente.', 'success')
    
    # Redirigir según de dónde vino
    referer = request.referrer
    if referer and 'aprobaciones' in referer:
        return redirect(url_for('admin.aprobaciones'))
    elif referer and 'panel' in referer:
        return redirect(url_for('admin.panel'))
    else:
        return redirect(url_for('admin.panel'))
