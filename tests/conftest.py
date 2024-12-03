import pytest
from app import create_app, db
from app.models import Client
from fakeredis import FakeRedis
from flask_jwt_extended import create_access_token
from app.models import Client, RoleEnum


@pytest.fixture
def app():
    app = create_app()
    app.config.from_object("config.TestConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def redis_client(app):
    fake_redis = FakeRedis()
    app.redis_client = fake_redis
    return fake_redis

@pytest.fixture
def admin_user():
    admin = Client(
        name="Admin User",
        email="admin@gmail.com",
        password="admin123",  
        role=RoleEnum.ADMIN,  # Используем правильный Enum
    )
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def auth_headers(admin_user):
    token = create_access_token(identity=admin_user.id)
    return {"Authorization": f"Bearer {token}"}
