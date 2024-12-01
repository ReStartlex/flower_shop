import pytest
from app import create_app
from config import Config

# Тестирование конфигурации приложения
def test_config():
    app = create_app()

    # Проверка, что конфигурация для базы данных установлена правильно
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://postgres:rootroot@localhost/flower_shop_test'

    # Проверка, что конфигурация для Redis установлена правильно
    assert app.config['REDIS_URL'] == 'redis://localhost:6379/0'

    # Проверка, что секретный ключ присутствует
    assert app.config['SECRET_KEY'] == 'default_secret_key'

    # Проверка, что ключ JWT секретен
    assert app.config['JWT_SECRET_KEY'] == 'default_jwt_secret_key'


# Тестирование конфигурации тестового окружения
def test_test_config():
    app = create_app()
    app.config.from_object('config.TestConfig')

    # Проверка, что конфигурация для базы данных для тестов установлена правильно
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://postgres:rootroot@localhost/flower_shop_test'

    # Проверка, что тестовый режим включен
    assert app.config['TESTING'] is True

    # Проверка, что для отслеживания изменений в базе данных отключено
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
