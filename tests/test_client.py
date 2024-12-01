import pytest
from app import create_app, db
from app.models import Client  # Импортируем модель Client для тестирования
from flask_jwt_extended import create_access_token
from flask import jsonify

@pytest.fixture(scope='module')
def new_client():
    """Фикстура для создания нового клиента в базе данных"""
    client = Client(name="John Doe", email="john@example.com", phone="1234567890")
    db.session.add(client)
    db.session.commit()
    return client

@pytest.fixture(scope='module')
def access_token():
    """Фикстура для создания JWT-токена для аутентификации"""
    # Создаём токен для теста
    user = Client(name="John Doe", email="john@example.com", phone="1234567890")
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id)  # Токен для клиента
    return token

@pytest.fixture(scope='module')
def app():
    """Фикстура для создания и настройки Flask-приложения с тестовой конфигурацией"""
    app = create_app('TestConfig')  # Используем тестовую конфигурацию
    with app.app_context():
        db.create_all()  # Создаём все таблицы
        yield app
        db.drop_all()  # Удаляем таблицы после тестов

@pytest.fixture(scope='module')
def client(app):
    """Фикстура для тестирования маршрутов"""
    return app.test_client()

def test_create_client(client, access_token):
    """Тест на создание клиента"""
    new_client_data = {
        "name": "Alice",
        "email": "alice@example.com",
        "phone": "9876543210"
    }

    # Отправляем запрос на создание клиента
    response = client.post(
        '/clients/',
        json=new_client_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Проверяем, что ответ успешный (статус 201)
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == new_client_data['name']
    assert data['email'] == new_client_data['email']
    assert data['phone'] == new_client_data['phone']

def test_get_clients(client, access_token, new_client):
    """Тест на получение списка клиентов"""
    response = client.get(
        '/clients/',
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)  # Проверяем, что данные — это список
    assert len(data) > 0  # Список клиентов не должен быть пустым

def test_update_client(client, access_token, new_client):
    """Тест на обновление информации о клиенте"""
    updated_data = {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "111222333"
    }

    response = client.put(
        f'/clients/{new_client.id}/',
        json=updated_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == updated_data['name']
    assert data['email'] == updated_data['email']
    assert data['phone'] == updated_data['phone']

def test_delete_client(client, access_token, new_client):
    """Тест на удаление клиента"""
    response = client.delete(
        f'/clients/{new_client.id}/',
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    # Проверяем, что клиент был удалён
    client = Client.query.get(new_client.id)
    assert client is None
