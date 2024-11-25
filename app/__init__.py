from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from flask_jwt_extended import JWTManager  
from config import Config
from app.utils.logger import setup_logger


db = SQLAlchemy()
migrate = Migrate()
logger = setup_logger()
jwt = JWTManager()  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)  
    Swagger(app)

    
    from .routes import client_routes, product_routes, order_routes, auth_routes
    app.register_blueprint(client_routes.bp)
    app.register_blueprint(product_routes.bp)
    app.register_blueprint(order_routes.bp)
    app.register_blueprint(auth_routes.bp)  

    return app
