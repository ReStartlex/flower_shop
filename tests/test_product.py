import pytest
from app import create_app, db
from app.models import Product, Client
from flask_jwt_extended import create_access_token
from app.utils.auth import RoleEnum


@pytest.fixture
def admin_user():
    """Создаем пользователя с ролью администратора."""
    admin = Client(
        name="Admin User",
        email="admin@gmail.com",
        password="admin123",
        role=RoleEnum.ADMIN,
    )
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def auth_headers(admin_user):
    """Создаем заголовки с токеном для авторизации администратора."""
    token = create_access_token(identity=admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def product():
    """Создаем тестовый продукт в базе данных."""
    product = Product(
        name="Test Product",
        description="Test Description",
        price=20.0,
        stock=100
    )
    db.session.add(product)
    db.session.commit()
    return product


def test_get_all_products(client, auth_headers):
    """Тестируем получение всех продуктов."""
    response = client.get('/products/', headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)  # Проверяем, что ответ — это список продуктов


def test_create_product(client, auth_headers):
    """Тестируем создание нового продукта."""
    new_product = {
        "name": "New Product",
        "description": "A bouquet of fresh roses",
        "price": 25.50,
        "stock": 50
    }
    response = client.post('/products/', json=new_product, headers=auth_headers)
    assert response.status_code == 201
    assert 'id' in response.json  # Продукт должен содержать ID
    assert response.json['message'] == 'Product created successfully'


def test_get_product_by_id(client, auth_headers, product):
    """Тестируем получение продукта по ID."""
    response = client.get(f'/products/{product.id}/', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['name'] == product.name  # Проверяем, что название продукта соответствует ожидаемому


def test_update_product(client, auth_headers, product):
    """Тестируем обновление продукта."""
    updated_data = {
        "name": "Updated Product",
        "description": "Updated Description",
        "price": 30.00,
        "stock": 200
    }
    response = client.put(f'/products/{product.id}/', json=updated_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Product updated successfully'

    # Проверяем, что данные продукта обновились в базе
    updated_product = Product.query.get(product.id)
    assert updated_product.name == updated_data["name"]
    assert updated_product.price == updated_data["price"]


def test_delete_product(client, auth_headers, product):
    """Тестируем удаление продукта."""
    response = client.delete(f'/products/{product.id}/', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Product deleted successfully'

    # Проверяем, что продукт был удален из базы
    deleted_product = Product.query.get(product.id)
    assert deleted_product is None
