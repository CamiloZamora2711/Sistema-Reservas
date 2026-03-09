from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, DateField, SelectMultipleField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    """Formulario de login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')

class RegistroForm(FlaskForm):
    """Formulario de registro"""
    nombre = StringField('Nombre completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    rol = SelectField('Rol', choices=[
        ('docente', 'Docente'),
        ('administrativo', 'Administrativo'),
        ('coordinador', 'Coordinador'),
        ('admin', 'Administrador')
    ], default='docente', validators=[DataRequired()])
    curso = SelectField('Curso que atiende', choices=[
        ('', 'Seleccione un curso'),
        ('1B-A', '1° Básico A'), ('1B-B', '1° Básico B'),
        ('2B-A', '2° Básico A'), ('2B-B', '2° Básico B'),
        ('3B-A', '3° Básico A'), ('3B-B', '3° Básico B'),
        ('4B-A', '4° Básico A'), ('4B-B', '4° Básico B'),
        ('5B-A', '5° Básico A'), ('5B-B', '5° Básico B'),
        ('6B-A', '6° Básico A'), ('6B-B', '6° Básico B'),
        ('7B-A', '7° Básico A'), ('7B-B', '7° Básico B'),
        ('8B-A', '8° Básico A'), ('8B-B', '8° Básico B'),
        ('1M-A', '1° Medio A'), ('1M-B', '1° Medio B'),
        ('2M-A', '2° Medio A'), ('2M-B', '2° Medio B'),
        ('3M-A', '3° Medio A'), ('3M-B', '3° Medio B'),
        ('4M-A', '4° Medio A'), ('4M-B', '4° Medio B'),
    ], validators=[Optional()])
    activo = BooleanField('Usuario Activo', default=True)
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado.')

class ReservaForm(FlaskForm):
    """Formulario de reserva"""
    sala_id = SelectField('Sala', coerce=int, validators=[DataRequired()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    bloques = StringField('Bloques', validators=[DataRequired()])
    motivo = StringField('Motivo', validators=[DataRequired(), Length(min=3, max=200)])
    curso_asistente = SelectField('Curso que asistirá', choices=[
        ('', 'Seleccione un curso'),
        ('1B-A', '1° Básico A'), ('1B-B', '1° Básico B'),
        ('2B-A', '2° Básico A'), ('2B-B', '2° Básico B'),
        ('3B-A', '3° Básico A'), ('3B-B', '3° Básico B'),
        ('4B-A', '4° Básico A'), ('4B-B', '4° Básico B'),
        ('5B-A', '5° Básico A'), ('5B-B', '5° Básico B'),
        ('6B-A', '6° Básico A'), ('6B-B', '6° Básico B'),
        ('7B-A', '7° Básico A'), ('7B-B', '7° Básico B'),
        ('8B-A', '8° Básico A'), ('8B-B', '8° Básico B'),
        ('1M-A', '1° Medio A'), ('1M-B', '1° Medio B'),
        ('2M-A', '2° Medio A'), ('2M-B', '2° Medio B'),
        ('3M-A', '3° Medio A'), ('3M-B', '3° Medio B'),
        ('4M-A', '4° Medio A'), ('4M-B', '4° Medio B'),
    ], validators=[Optional()]) # Cambiado a Optional para administrativos
    notas = TextAreaField('Notas adicionales', validators=[Optional(), Length(max=500)])
    es_recurrente = BooleanField('Reserva Recurrente')
    recurrencia_tipo = SelectField('Tipo de Recurrencia', choices=[
        ('', 'Seleccione'),
        ('diaria', 'Diaria'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual')
    ], validators=[Optional()])
    recurrencia_cantidad = IntegerField('Cantidad de Repeticiones', validators=[Optional(), NumberRange(min=1, max=10)])
    fecha_fin_recurrencia = DateField('Fecha Fin Recurrencia', validators=[Optional()])
    submit = SubmitField('Crear Reserva')


class EditarUsuarioForm(FlaskForm):
    """Formulario para editar usuario"""
    nombre = StringField('Nombre Completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    rol = SelectField('Rol', choices=[
        ('docente', 'Docente'), 
        ('administrativo', 'Administrativo'),
        ('coordinador', 'Coordinador'), 
        ('admin', 'Administrador')
    ])
    curso = SelectField('Curso que atiende', choices=[
        ('', 'Sin curso asignado'),
        ('1B-A', '1° Básico A'), ('1B-B', '1° Básico B'),
        ('2B-A', '2° Básico A'), ('2B-B', '2° Básico B'),
        ('3B-A', '3° Básico A'), ('3B-B', '3° Básico B'),
        ('4B-A', '4° Básico A'), ('4B-B', '4° Básico B'),
        ('5B-A', '5° Básico A'), ('5B-B', '5° Básico B'),
        ('6B-A', '6° Básico A'), ('6B-B', '6° Básico B'),
        ('7B-A', '7° Básico A'), ('7B-B', '7° Básico B'),
        ('8B-A', '8° Básico A'), ('8B-B', '8° Básico B'),
        ('1M-A', '1° Medio A'), ('1M-B', '1° Medio B'),
        ('2M-A', '2° Medio A'), ('2M-B', '2° Medio B'),
        ('3M-A', '3° Medio A'), ('3M-B', '3° Medio B'),
        ('4M-A', '4° Medio A'), ('4M-B', '4° Medio B'),
    ], validators=[Optional()])
    activo = BooleanField('Usuario Activo')


class SalaForm(FlaskForm):
    """Formulario de sala"""
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=100)])
    capacidad = IntegerField('Capacidad', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[
        ('basica', 'Computación Básica'),
        ('media', 'Computación Media'),
        ('normal', 'Normal')
    ], validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    color = StringField('Color', validators=[Optional(), Length(max=7)], default='#0d6efd')
    activa = BooleanField('Activa', default=True)

class AprobarReservaForm(FlaskForm):
    """Formulario para aprobar/rechazar reserva"""
    accion = SelectField('Acción', choices=[('aprobar', 'Aprobar'), ('rechazar', 'Rechazar')], validators=[DataRequired()])
    notas = TextAreaField('Notas', validators=[Optional()])
