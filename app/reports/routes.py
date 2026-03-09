from flask import render_template, request, send_file
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app.reports import reports_bp
from app.models import Reserva, Sala, User
from app.utils.export import exportar_excel, exportar_pdf
from sqlalchemy import func
from app import db

@reports_bp.route('/estadisticas')
@login_required
def estadisticas():
    """Página de estadísticas avanzadas"""
    # Filtros
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Fechas por defecto: último mes
    if not fecha_inicio:
        fecha_inicio = (date.today() - timedelta(days=30)).isoformat()
    if not fecha_fin:
        fecha_fin = date.today().isoformat()
    
    # Convertir a objetos date
    fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    # Query base
    query = Reserva.query.filter(
        Reserva.fecha >= fecha_inicio_obj,
        Reserva.fecha <= fecha_fin_obj
    )
    
    # Total de reservas
    total_reservas = query.count()
    
    # Reservas por estado
    reservas_por_estado = db.session.query(
        Reserva.estado, func.count(Reserva.id)
    ).filter(
        Reserva.fecha >= fecha_inicio_obj,
        Reserva.fecha <= fecha_fin_obj
    ).group_by(Reserva.estado).all()
    
    # Reservas por sala
    reservas_por_sala = db.session.query(
        Sala.nombre, func.count(Reserva.id).label('total')
    ).join(Reserva).filter(
        Reserva.fecha >= fecha_inicio_obj,
        Reserva.fecha <= fecha_fin_obj
    ).group_by(Sala.id).all()
    
    # Reservas por día
    reservas_por_dia = db.session.query(
        Reserva.fecha, func.count(Reserva.id).label('total')
    ).filter(
        Reserva.fecha >= fecha_inicio_obj,
        Reserva.fecha <= fecha_fin_obj
    ).group_by(Reserva.fecha).order_by(Reserva.fecha).all()
    
    # Top usuarios (solo para admin/coordinador)
    top_usuarios = []
    if current_user.is_coordinador():
        top_usuarios = db.session.query(
            User.nombre, func.count(Reserva.id).label('total')
        ).join(Reserva, User.id == Reserva.user_id).filter(
            Reserva.fecha >= fecha_inicio_obj,
            Reserva.fecha <= fecha_fin_obj
        ).group_by(User.id).order_by(func.count(Reserva.id).desc()).limit(10).all()
    
    # Bloques más usados
    bloques_mas_usados = db.session.query(
        Reserva.bloque, func.count(Reserva.id).label('total')
    ).filter(
        Reserva.fecha >= fecha_inicio_obj,
        Reserva.fecha <= fecha_fin_obj
    ).group_by(Reserva.bloque).order_by(func.count(Reserva.id).desc()).all()
    
    return render_template('reports/estadisticas.html',
                         total_reservas=total_reservas,
                         reservas_por_estado=reservas_por_estado,
                         reservas_por_sala=reservas_por_sala,
                         reservas_por_dia=reservas_por_dia,
                         top_usuarios=top_usuarios,
                         bloques_mas_usados=bloques_mas_usados,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin)

@reports_bp.route('/exportar/excel')
@login_required
def exportar_reservas_excel():
    """Exportar reservas a Excel"""
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Fechas por defecto
    if not fecha_inicio:
        fecha_inicio = (date.today() - timedelta(days=30)).isoformat()
    if not fecha_fin:
        fecha_fin = date.today().isoformat()
    
    fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    # Obtener reservas
    query = Reserva.query.filter(
        Reserva.fecha >= fecha_inicio_obj,
        Reserva.fecha <= fecha_fin_obj
    )
    
    # Solo mostrar propias si no es admin/coordinador
    if not current_user.is_coordinador():
        query = query.filter_by(user_id=current_user.id)
    
    reservas = query.order_by(Reserva.fecha, Reserva.bloque).all()
    
    # Generar archivo
    archivo = exportar_excel(reservas, fecha_inicio, fecha_fin)
    
    return send_file(
        archivo,
        as_attachment=True,
        download_name=f'reservas_{fecha_inicio}_a_{fecha_fin}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@reports_bp.route('/exportar/pdf')
@login_required
def exportar_reservas_pdf():
    """Exportar reservas a PDF"""
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Fechas por defecto
    if not fecha_inicio:
        fecha_inicio = (date.today() - timedelta(days=30)).isoformat()
    if not fecha_fin:
        fecha_fin = date.today().isoformat()
    
    fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    # Obtener reservas
    query = Reserva.query.filter(
        Reserva.fecha >= fecha_inicio_obj,
        Reserva.fecha <= fecha_fin_obj
    )
    
    # Solo mostrar propias si no es admin/coordinador
    if not current_user.is_coordinador():
        query = query.filter_by(user_id=current_user.id)
    
    reservas = query.order_by(Reserva.fecha, Reserva.bloque).all()
    
    # Generar archivo
    archivo = exportar_pdf(reservas, fecha_inicio, fecha_fin)
    
    return send_file(
        archivo,
        as_attachment=True,
        download_name=f'reservas_{fecha_inicio}_a_{fecha_fin}.pdf',
        mimetype='application/pdf'
    )
