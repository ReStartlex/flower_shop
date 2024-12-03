import pytest
from app import create_app, db
from app.models import Client, RoleEnum
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token


@pytest.fixture
def new_user_data():
    """Данные для регистрации нового пользователя."""
    return {
        "name": "Alexey Savchishen",
        "email": "alexey@gmail.com",
        "password": "password123"
    }


@pytest.fixture
def existing_user_data():
    """Данные для уже существующего пользователя."""
    return {
        "name": "Existing User",
        "email": "existing@gmail.com",
        "password": "password123"
    }


@pytest.fixture
def existing_user(existing_user_data):
    """Создаем существующего пользователя для тестов."""
    existing_user = Client(
        name=existing_user_data['name'],
        email=existing_user_data['email'],
        password=generate_password_hash(existing_user_data['password'], method='pbkdf2:sha256'),
        role=RoleEnum.USER
    )
    db.session.add(existing_user)
    db.session.commit()
    return existing_user


def test_register_user(client, new_user_data):
    """Тестируем успешную регистрацию нового пользователя."""
    response = client.post('/auth/register', json=new_user_data)
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'


def test_register_user_with_existing_email(client, new_user_data, existing_user_data):
    """Тестируем регистрацию с уже существующим email."""
    client.post('/auth/register', json=existing_user_data)  # Создаем существующего пользователя
    response = client.post('/auth/register', json=new_user_data)
    assert response.status_code == 400
    assert response.json['error'] == 'Email already exists'


def test_login_user(client, existing_user_data):
    """Тестируем успешный вход пользователя."""
    client.post('/auth/register', json=existing_user_data)  # Регистрируем пользователя
    login_data = {
        "email": existing_user_data['email'],
        "password": existing_user_data['password']
    }
    response = client.post('/auth/login', json=login_data)
    assert response.status_code == 200
    assert 'access_token' in response.json  # Проверяем, что токен получен


def test_login_user_invalid_credentials(client, existing_user_data):
    """Тестируем ошибку при входе с неверным паролем."""
    client.post('/auth/register', json=existing_user_data)  # Регистрируем пользователя
    login_data = {
        "email": existing_user_data['email'],
        "password": "wrongpassword"  # Неверный пароль
    }
    response = client.post('/auth/login', json=login_data)
    assert response.status_code == 401
    assert response.json['error'] == 'Invalid credentials'


def test_login_user_non_existent(client):
    """Тестируем ошибку при входе с несуществующим пользователем."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = client.post('/auth/login', json=login_data)
    assert response.status_code == 401
    assert response.json['error'] == 'Invalid credentials'


def test_login_attempts_limit(client, existing_user_data):
    """Тестируем ограничение количества попыток входа."""
    client.post('/auth/register', json=existing_user_data)  # Регистрируем пользователя
    login_data = {
        "email": existing_user_data['email'],
        "password": "wrongpassword"
    }
    
    # Совершаем 5 неудачных попыток входа
    for _ in range(5):
        response = client.post('/auth/login', json=login_data)
        assert response.status_code == 401

    # После 5 неудачных попыток, проверяем, что запрос заблокирован
    response = client.post('/auth/login', json=login_data)
    assert response.status_code == 429
    assert response.json['error'] == 'Too many login attempts. Please try again later.'


def test_missing_fields_in_register(client):
    """Тестируем отсутствие обязательных полей при регистрации."""
    incomplete_data = {"name": "John Doe", "email": "john@example.com"}  # Без пароля
    response = client.post('/auth/register', json=incomplete_data)
    assert response.status_code == 400
    assert response.json['error'] == 'Name, email, and password are required'


def test_missing_fields_in_login(client, existing_user_data):
    """Тестируем отсутствие обязательных полей при входе."""
    client.post('/auth/register', json=existing_user_data)  # Регистрируем пользователя
    incomplete_data = {"email": "existing@example.com"}  # Без пароля
    response = client.post('/auth/login', json=incomplete_data)
    assert response.status_code == 400
    assert response.json['error'] == 'Email and password are required'
