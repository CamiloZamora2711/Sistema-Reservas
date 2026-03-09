from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """Modelo de usuario con roles"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='docente')  # admin, coordinador, docente
    curso = db.Column(db.String(10))  # 1B-A, 1B-B, 2B-A, ..., 4M-A, 4M-B
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones - lazy='select' permite eager loading
    reservas = db.relationship('Reserva', backref='usuario', lazy='select', foreign_keys='Reserva.user_id')
    
    def set_password(self, password):
        """Hashear contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verificar si es administrador"""
        return self.rol == 'admin'
    
    def is_coordinador(self):
        """Verificar si es coordinador o admin"""
        return self.rol in ['admin', 'coordinador']
    
    def __repr__(self):
        return f'<User {self.email}>'

class Sala(db.Model):
    """Modelo de sala"""
    __tablename__ = 'salas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # basica, media
    descripcion = db.Column(db.Text)
    activa = db.Column(db.Boolean, default=True)
    color = db.Column(db.String(7), default='#0d6efd')  # Color para el calendario
    
    # Relaciones
    reservas = db.relationship('Reserva', backref='sala', lazy='select')
    
    def __repr__(self):
        return f'<Sala {self.nombre}>'

class Reserva(db.Model):
    """Modelo de Reserva"""
    __tablename__ = 'reserva'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # Índice agregado
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'), nullable=False, index=True)  # Índice agregado
    fecha = db.Column(db.Date, nullable=False, index=True)  # Índice agregado
    bloque = db.Column(db.String(50), nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    curso_asistente = db.Column(db.String(20))
    estado = db.Column(db.String(20), default='pendiente', index=True)  # Índice agregado
    notas = db.Column(db.Text)
    
    # Campos de recurrencia
    es_recurrente = db.Column(db.Boolean, default=False)
    recurrencia_tipo = db.Column(db.String(20))  # 'semanal', 'quincenal'
    recurrencia_cantidad = db.Column(db.Integer, default=1)
    reserva_padre_id = db.Column(db.Integer, db.ForeignKey('reserva.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones (sin backref duplicado)
    reserva_padre = db.relationship('Reserva', remote_side=[id], backref='reservas_hijas')
    
    # Índice compuesto para búsquedas frecuentes
    __table_args__ = (
        db.Index('idx_reserva_fecha_estado', 'fecha', 'estado'),
        db.Index('idx_reserva_user_fecha', 'user_id', 'fecha'),
    )
    
    def __repr__(self):
        return f'<Reserva {self.id}>'
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'sala': self.sala.nombre,
            'sala_id': self.sala_id,
            'usuario': self.usuario.nombre,
            'fecha': self.fecha.isoformat(),
            'bloque': self.bloque,
            'estado': self.estado,
            'motivo': self.motivo,
            'notas': self.notas,
            'color': self.sala.color
        }

class Recurso(db.Model):
    """Modelo de recursos adicionales (proyectores, laptops, etc.)"""
    __tablename__ = 'recursos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # proyector, laptop, microfono, etc.
    cantidad_disponible = db.Column(db.Integer, default=1)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Recurso {self.nombre}>'

class AuditLog(db.Model):
    """Modelo de logs de auditoría"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    accion = db.Column(db.String(100), nullable=False)
    entidad = db.Column(db.String(50))  # reserva, usuario, sala, etc.
    entidad_id = db.Column(db.Integer)
    detalles = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    usuario = db.relationship('User', backref='logs')
    
    def __repr__(self):
        return f'<AuditLog {self.accion} by {self.usuario.email if self.usuario else "System"}>'

def get_bloques_por_tipo(tipo_sala):
    """Retorna los bloques horarios según el tipo de sala"""
    bloques = {
        'basica': [
            '08:15-09:00',
            '09:00-09:45',
            '10:00-10:45',
            '10:45-11:30',
            '11:45-12:30',
            '12:30-13:15',
            '13:15-14:00',
            '14:45-15:25',
            '15:25-16:10',
            '16:10-17:05'
        ],
        'media': [
            '08:15-09:00',
            '09:00-09:45',
            '10:00-10:45',
            '10:45-11:30',
            '11:45-12:30',
            '12:30-13:15',
            '13:15-14:00',
            '14:45-15:25',
            '15:25-16:10',
            '16:10-17:05'
        ],
        'normal': [  # Salas normales usan el mismo horario que básica
            '08:15-09:00',
            '09:00-09:45',
            '10:00-10:45',
            '10:45-11:30',
            '11:45-12:30',
            '12:30-13:15',
            '13:15-14:00',
            '14:45-15:25',
            '15:25-16:10',
            '16:10-17:05'
        ]
    }
    
    return bloques.get(tipo_sala, bloques['basica'])  # Por defecto, usar bloques de básica
