# Sistema de Reservas SSR 2026

Sistema moderno de gestión de reservas de salas educativas con autenticación multi-usuario, estadísticas avanzadas y exportación de datos.

## 🚀 Características

- ✅ **Autenticación Multi-Usuario** con roles (Admin, Coordinador, Docente)
- ✅ **Reservas Recurrentes** (semanal/quincenal)
- ✅ **Sistema de Aprobación** de reservas
- ✅ **Calendario Interactivo** con FullCalendar.js
- ✅ **Exportación** a Excel y PDF
- ✅ **Estadísticas Avanzadas** con gráficos
- ✅ **API REST** para integraciones
- ✅ **Modo Oscuro** automático
- ✅ **Logs de Auditoría** completos
- ✅ **Diseño Responsive** con Bootstrap 5

## 📋 Requisitos

- Python 3.8+
- pip
- SQLite (incluido con Python)

## 🔧 Instalación

1. **Clonar o descargar el proyecto**

2. **Crear entorno virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Inicializar base de datos**
```bash
python init_db.py
```

6. **Ejecutar aplicación**
```bash
python run.py
```

7. **Abrir en navegador**
```
http://localhost:5000
```

## 👥 Usuarios de Prueba y Credenciales por Defecto

A continuación se presentan las credenciales configuradas al inicializar la base de datos (mediante `init_db.py`):

| Email       | Contraseña | Rol |
|-------------|-------------|------|
| admin@ssr.cl | Admin2026! | Administrador |
| coordinador@ssr.cl | Coord2026! | Coordinador |
| docente1@ssr.cl | Docente2026! | Docente |
| docente2@ssr.cl | Docente2026! | Docente |

## 📚 Estructura del Proyecto

```
RESERVASSSR2026/
├── app/
│   ├── __init__.py          # Factory de aplicación
│   ├── models.py            # Modelos de base de datos
│   ├── forms.py             # Formularios WTForms
│   ├── auth/                # Blueprint de autenticación
│   ├── main/                # Blueprint principal
│   ├── admin/               # Blueprint de administración
│   ├── api/                 # Blueprint de API REST
│   ├── reports/             # Blueprint de reportes
│   ├── utils/               # Utilidades (email, export, etc.)
│   ├── templates/           # Templates HTML
│   └── static/              # Archivos estáticos (CSS, JS)
├── config.py                # Configuración
├── init_db.py               # Script de inicialización
├── run.py                   # Punto de entrada
└── requirements.txt         # Dependencias
```

## 🎯 Uso

### Como Docente
1. Iniciar sesión
2. Ir a "Nueva Reserva"
3. Seleccionar sala, fecha y bloques
4. Esperar aprobación (si está configurado)

### Como Coordinador
- Todas las funciones de docente
- Aprobar/rechazar reservas
- Gestionar salas
- Ver estadísticas completas

### Como Administrador
- Todas las funciones de coordinador
- Gestionar usuarios
- Ver logs de auditoría
- Configurar sistema

## 📊 API REST

### Endpoints Disponibles

- `GET /api/salas` - Listar salas
- `GET /api/bloques/<sala_id>` - Bloques de una sala
- `GET /api/disponibilidad` - Verificar disponibilidad
- `GET /api/reservas` - Listar reservas (con filtros)
- `GET /api/estadisticas` - Estadísticas generales

### Ejemplo de Uso

```bash
curl -X GET http://localhost:5000/api/salas \
  -H "Cookie: session=..."
```

## 🔒 Seguridad

- Contraseñas hasheadas con bcrypt
- Protección CSRF en formularios
- Validación de sesiones
- Logs de auditoría
- Control de acceso basado en roles

## 📧 Configuración de Email (Opcional)

Para habilitar notificaciones por email, configura en `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicacion
```

**Nota:** Para Gmail, necesitas crear una "Contraseña de aplicación" en tu cuenta.

## 🎨 Personalización

### Cambiar Colores de Salas
Editar en `init_db.py` o desde el panel de administración.

### Modificar Bloques Horarios
Editar en `app/models.py`:
```python
BLOQUES_BASICA = [...]
BLOQUES_MEDIA = [...]
```

### Ajustar Límite de Días de Anticipación
En `.env`:
```env
RESERVAS_MAX_DIAS_ANTICIPACION=30
```

## 🐛 Solución de Problemas

### Error: "No module named 'app'"
```bash
# Asegúrate de estar en el directorio correcto
cd RESERVASSSR2026
```

### Error de base de datos
```bash
# Eliminar y recrear base de datos
rm reservas.db
python init_db.py
```

### Puerto 5000 en uso
Cambiar puerto en `run.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Para preguntas o problemas, por favor abre un issue en el repositorio.

---

**Desarrollado con ❤️ para SSR 2026**
