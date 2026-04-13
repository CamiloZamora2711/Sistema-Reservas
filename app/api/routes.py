from flask import jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, date
from app.api import api_bp
from app.models import Sala, Reserva, get_bloques_por_tipo
from app import db

@api_bp.route('/salas', methods=['GET'])
@login_required
def get_salas():
    """Obtener todas las salas activas"""
    salas = Sala.query.filter_by(activa=True).all()
    return jsonify([{
        'id': s.id,
        'nombre': s.nombre,
        'capacidad': s.capacidad,
        'tipo': s.tipo,
        'color': s.color
    } for s in salas])

@api_bp.route('/bloques/<int:sala_id>', methods=['GET'])
@login_required
def get_bloques(sala_id):
    """Obtener bloques disponibles para una sala"""
    sala = Sala.query.get_or_404(sala_id)
    bloques = get_bloques_por_tipo(sala.tipo)
    
    return jsonify({
        'bloques': bloques,
        'tipo': sala.tipo
    })

@api_bp.route('/disponibilidad', methods=['GET'])
@login_required
def get_disponibilidad():
    """Obtener disponibilidad de una sala en una fecha"""
    sala_id = request.args.get('sala_id', type=int)
    fecha_str = request.args.get('fecha')
    
    if not sala_id or not fecha_str:
        return jsonify({'error': 'Faltan parámetros'}), 400
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido'}), 400
    
    sala = Sala.query.get_or_404(sala_id)
    
    # Obtener todos los bloques para el tipo de sala
    todos_bloques = get_bloques_por_tipo(sala.tipo)
    
    # Obtener reservas existentes para esa sala y fecha
    reservas_existentes = Reserva.query.filter_by(
        sala_id=sala_id,
        fecha=fecha
    ).filter(Reserva.estado.in_(['pendiente', 'aprobada'])).all()
    
    # Crear diccionario de bloques ocupados con información
    bloques_ocupados_info = {}
    for reserva in reservas_existentes:
        # Ensure 'usuario' relationship is loaded or handle potential None
        usuario_nombre = reserva.usuario.nombre if reserva.usuario else 'Desconocido'
        bloques_ocupados_info[reserva.bloque] = {
            'usuario': usuario_nombre,
            'curso': reserva.curso_asistente,
            'motivo': reserva.motivo,
            'estado': reserva.estado
        }
    
    # Crear lista de bloques con su estado y detalles
    bloques_info = []
    for bloque in todos_bloques:
        if bloque in bloques_ocupados_info:
            bloques_info.append({
                'bloque': bloque,
                'disponible': False,
                'info': bloques_ocupados_info[bloque]
            })
        else:
            bloques_info.append({
                'bloque': bloque,
                'disponible': True,
                'info': None
            })
    
    return jsonify({
        'sala_nombre': sala.nombre,
        'fecha': fecha_str,
        'bloques': bloques_info,
        'total_bloques': len(todos_bloques)
    })

@api_bp.route('/reservas', methods=['GET'])
@login_required
def get_reservas():
    """Obtener reservas con filtros opcionales"""
    # Parámetros de filtro
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    sala_id = request.args.get('sala_id', type=int)
    estado = request.args.get('estado')
    
    query = Reserva.query
    
    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            query = query.filter(Reserva.fecha >= fecha_inicio_obj)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            query = query.filter(Reserva.fecha <= fecha_fin_obj)
        except ValueError:
            pass
    
    if sala_id:
        query = query.filter_by(sala_id=sala_id)
    
    if estado:
        query = query.filter_by(estado=estado)
    
    # Solo mostrar reservas propias si no es admin/coordinador
    if not current_user.is_coordinador():
        query = query.filter_by(user_id=current_user.id)
    
    reservas = query.order_by(Reserva.fecha, Reserva.bloque).all()
    
    return jsonify([r.to_dict() for r in reservas])

@api_bp.route('/estadisticas', methods=['GET'])
@login_required
def get_estadisticas():
    """Obtener estadísticas generales"""
    from sqlalchemy import func
    
    # Total de reservas
    total_reservas = Reserva.query.count()
    
    # Reservas por estado
    reservas_por_estado = db.session.query(
        Reserva.estado, func.count(Reserva.id)
    ).group_by(Reserva.estado).all()
    
    # Salas más usadas
    salas_mas_usadas = db.session.query(
        Sala.nombre, func.count(Reserva.id).label('total')
    ).join(Reserva).group_by(Sala.id).order_by(func.count(Reserva.id).desc()).limit(5).all()
    
    # Usuarios más activos (solo para admin/coordinador)
    usuarios_activos = []
    if current_user.is_coordinador():
        from app.models import User
        usuarios_activos = db.session.query(
            User.nombre, func.count(Reserva.id).label('total')
        ).join(Reserva).group_by(User.id).order_by(func.count(Reserva.id).desc()).limit(5).all()
    
    return jsonify({
        'total_reservas': total_reservas,
        'reservas_por_estado': dict(reservas_por_estado),
        'salas_mas_usadas': [{'sala': s[0], 'total': s[1]} for s in salas_mas_usadas],
        'usuarios_activos': [{'usuario': u[0], 'total': u[1]} for u in usuarios_activos]
    })
