import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    """Базовая конфигурация для приложения."""
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY не задан. Укажите его в .env файле.")
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY не задан. Укажите его в .env файле.")
    
    # Основная база данных
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL не задан. Укажите его в .env файле.")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

class TestConfig(Config):
    """Конфигурация для тестирования."""
    # Тестовая база данных
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("TEST_DATABASE_URL не задан. Укажите его в .env файле.")
    
    TESTING = True
