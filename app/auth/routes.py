from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.auth import auth_bp
from app import db
from app.models import User, AuditLog
from app.forms import LoginForm, RegistroForm

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Email o contraseña incorrectos.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.activo:
            flash('Tu cuenta está desactivada. Contacta al administrador.', 'warning')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        # Log de auditoría
        log = AuditLog(
            user_id=user.id,
            accion='login',
            entidad='user',
            entidad_id=user.id,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'¡Bienvenido {user.nombre}!', 'success')
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.dashboard')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    if current_user.is_authenticated:
        # Log de auditoría
        log = AuditLog(
            user_id=current_user.id,
            accion='logout',
            entidad='user',
            entidad_id=current_user.id,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de nuevos usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistroForm()
    if form.validate_on_submit():
        # Verificar si el email ya existe
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('El email ya está registrado.', 'danger')
            return redirect(url_for('auth.registro'))
        
        # Crear nuevo usuario
        user = User(
            nombre=form.nombre.data,
            email=form.email.data.lower(),
            rol=form.rol.data,  # Usar el rol seleccionado del formulario
            curso=form.curso.data if form.curso.data else None
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Log de auditoría
        log = AuditLog(
            user_id=user.id,
            accion='registro',
            entidad='user',
            entidad_id=user.id,
            detalles=f'Nuevo usuario registrado: {user.email}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        # Enviar email de bienvenida
        from app.utils.email import send_bienvenida
        try:
            send_bienvenida(user)
        except Exception as e:
            print(f"Error al enviar email de bienvenida: {e}")
        
        flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/registro.html', form=form)
