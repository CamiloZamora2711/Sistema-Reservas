import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Configuración de la aplicación"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///reservas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de email (Microsoft 365)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.office365.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'admin_valpo@ssr.cl')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'Rafael2026')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'admin_valpo@ssr.cl')
    MAIL_ADMIN = os.environ.get('MAIL_ADMIN', 'juan.llanca@ssr.cl')
    
    # Application Settings
    RESERVAS_MAX_DIAS_ANTICIPACION = int(os.environ.get('RESERVAS_MAX_DIAS_ANTICIPACION') or 30)
    RESERVAS_REQUIEREN_APROBACION = os.environ.get('RESERVAS_REQUIEREN_APROBACION', 'True').lower() in ['true', '1', 't']
    
    # Admin Credentials (por defecto para inicialización)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@ssr.cl')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin2026!')
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Session
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora en segundos

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
