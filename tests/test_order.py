import pytest
from app import create_app, db
from app.models import Order, Client, Product
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
def client_user():
    """Создаем обычного пользователя для заказов."""
    client = Client(
        name="Client User",
        email="client@gmail.com",
        password="client123",
        role=RoleEnum.CLIENT,
    )
    db.session.add(client)
    db.session.commit()
    return client


@pytest.fixture
def product():
    """Создаем продукт для тестов."""
    product = Product(
        name="Test Product",
        description="Test Description",
        price=20.0,
        stock=100
    )
    db.session.add(product)
    db.session.commit()
    return product


@pytest.fixture
def auth_headers(admin_user):
    """Создаем заголовки с токеном для авторизации администратора."""
    token = create_access_token(identity=admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_auth_headers(client_user):
    """Создаем заголовки с токеном для обычного пользователя."""
    token = create_access_token(identity=client_user.id)
    return {"Authorization": f"Bearer {token}"}


def test_get_orders(client, auth_headers):
    """Тестируем получение всех заказов администратором."""
    response = client.get('/orders/', headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)  # Проверяем, что ответ — это список заказов


def test_create_order(client, auth_headers, client_user, product):
    """Тестируем создание нового заказа администратором."""
    order_data = {
        "client_id": client_user.id,
        "product_id": product.id,
        "quantity": 3
    }
    response = client.post('/orders/', json=order_data, headers=auth_headers)
    assert response.status_code == 201
    assert 'id' in response.json  # Заказ должен содержать ID
    assert response.json['message'] == 'Order created successfully'


def test_create_order_invalid_product(client, auth_headers, client_user):
    """Тестируем создание заказа с некорректным продуктом (отсутствие в базе)."""
    order_data = {
        "client_id": client_user.id,
        "product_id": 9999,  # Несуществующий продукт
        "quantity": 3
    }
    response = client.post('/orders/', json=order_data, headers=auth_headers)
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid client or product ID'


def test_create_order_not_enough_stock(client, auth_headers, client_user, product):
    """Тестируем создание заказа, когда недостаточно товара на складе."""
    product.stock = 2  # Устанавливаем количество товара меньше, чем заказано
    db.session.commit()
    
    order_data = {
        "client_id": client_user.id,
        "product_id": product.id,
        "quantity": 3  # Пытаемся заказать больше, чем есть в наличии
    }
    response = client.post('/orders/', json=order_data, headers=auth_headers)
    assert response.status_code == 400
    assert response.json['error'] == 'Not enough stock available'


def test_delete_order(client, auth_headers, client_user, product):
    """Тестируем удаление заказа администратором."""
    # Сначала создаем заказ
    order_data = {
        "client_id": client_user.id,
        "product_id": product.id,
        "quantity": 2
    }
    response = client.post('/orders/', json=order_data, headers=auth_headers)
    order_id = response.json['id']
    
    # Теперь удаляем его
    response = client.delete(f'/orders/{order_id}/', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Order deleted successfully'
    
    # Проверяем, что заказ был удален из базы данных
    deleted_order = Order.query.get(order_id)
    assert deleted_order is None


def test_delete_order_not_found(client, auth_headers):
    """Тестируем удаление заказа, которого нет в базе данных."""
    response = client.delete('/orders/99999/', headers=auth_headers)
    assert response.status_code == 404
    assert response.json['error'] == 'Order not found'
