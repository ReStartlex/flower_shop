from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from config import Config, TestConfig
from app.utils.logger import setup_logger
import redis  # Подключаем библиотеку Redis

db = SQLAlchemy()
migrate = Migrate()
logger = setup_logger()
jwt = JWTManager()

# Глобальный объект клиента Redis
redis_client = None

def create_app(test_config=False):
    app = Flask(__name__)

    # Если test_config == True, используем TestConfig
    if test_config:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    # Инициализация клиента Redis в create_app
    global redis_client
    redis_client = redis.StrictRedis.from_url(app.config['REDIS_URL'], decode_responses=True)

    # Инициализация других компонентов
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    Swagger(app)

    # Регистрация маршрутов
    from .routes import client_routes, product_routes, order_routes, auth_routes
    app.register_blueprint(client_routes.bp)
    app.register_blueprint(product_routes.bp)
    app.register_blueprint(order_routes.bp)
    app.register_blueprint(auth_routes.bp)

    # Добавление redis_client в приложение
    app.redis_client = redis_client

    return app
