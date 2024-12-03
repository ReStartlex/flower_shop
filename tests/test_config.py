import pytest
from app import create_app
from config import Config, TestConfig


@pytest.fixture
def app():
    """Фикстура для создания тестового приложения с конфигурацией TestConfig."""
    app = create_app()
    app.config.from_object(TestConfig)
    yield app


def test_config_values(app):
    """Тестирование значений конфигурации TestConfig."""
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://postgres:rootroot@localhost/flower_shop_test', \
        "Неправильный URI для тестовой базы данных"
    assert app.config['REDIS_URL'] == 'redis://localhost:6379/0', \
        "Неправильный URL для Redis"
    assert app.config['SECRET_KEY'] == 'a3d2b1e49c12356f8d0ab57ce25dc7e8', \
        "Неправильный SECRET_KEY"
    assert app.config['JWT_SECRET_KEY'] == 'b6f2e1c497a146d3c0af26d5da93ce6f', \
        "Неправильный JWT_SECRET_KEY"


def test_testing_mode(app):
    """Тестирование включения тестового режима."""
    assert app.config['TESTING'] is True, "Тестовый режим должен быть включен"


def test_sqlalchemy_tracking(app):
    """Тестирование отключения отслеживания изменений SQLAlchemy."""
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False, \
        "SQLALCHEMY_TRACK_MODIFICATIONS должно быть отключено"


def test_main_config():
    """Тестирование основной конфигурации приложения."""
    app = create_app()
    app.config.from_object(Config)

    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://postgres:rootroot@localhost/flower_shop', \
        "Неправильный URI для основной базы данных"
    assert app.config['REDIS_URL'] == 'redis://localhost:6379/0', \
        "Неправильный URL для Redis"
    assert app.config['SECRET_KEY'] == 'a3d2b1e49c12356f8d0ab57ce25dc7e8', \
        "Неправильный SECRET_KEY"
    assert app.config['JWT_SECRET_KEY'] == 'b6f2e1c497a146d3c0af26d5da93ce6f', \
        "Неправильный JWT_SECRET_KEY"
