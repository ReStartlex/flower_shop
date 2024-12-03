import pytest
import json
from app import create_app, db
from app.models import Client, Product, Order, RoleEnum
from flask_jwt_extended import create_access_token


@pytest.fixture
def app():
    """Создаём приложение Flask для тестов."""
    app = create_app('testing')  
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def redis_client(app):
    """Получаем доступ к Redis-клиенту для тестов."""
    return app.redis_client


@pytest.fixture
def new_user_data():
    """Данные для регистрации нового пользователя."""
    return {
        "name": "Alexey Savchishen",
        "email": "alexey@gmail.com",
        "password": "password123"
    }


@pytest.fixture
def new_product():
    """Создаём новый продукт для теста заказов."""
    product = Product(name="Rose", price=10.0, stock=100)
    db.session.add(product)
    db.session.commit()
    return product


@pytest.fixture
def new_order(new_user_data, new_product):
    """Создаём новый заказ для теста."""
    client = Client(name=new_user_data['name'], email=new_user_data['email'], role=RoleEnum.USER)
    db.session.add(client)
    db.session.commit()

    order = Order(client_id=client.id, product_id=new_product.id, quantity=2, total_price=20.0)
    db.session.add(order)
    db.session.commit()
    return order


def test_cache_orders(redis_client, app, new_order):
    """Тестируем кэширование данных заказов в Redis."""
    with app.test_client() as client:
        # Проверяем, что данные еще не кэшированы
        cached_orders = redis_client.get('orders')
        assert cached_orders is None

        # Запрашиваем список заказов
        response = client.get('/orders/')
        assert response.status_code == 200

        # Проверяем, что данные заказов закэшированы
        cached_orders = redis_client.get('orders')
        assert cached_orders is not None

        # Проверяем, что данные в кэше корректны
        orders = json.loads(cached_orders)
        assert len(orders) > 0
        assert orders[0]['client_id'] == new_order.client_id


def test_cache_orders_expiration(redis_client, app, new_order):
    """Тестируем срок действия кэша для заказов в Redis (TTL)."""
    with app.test_client() as client:
        # Запрашиваем список заказов
        response = client.get('/orders/')
        assert response.status_code == 200

        # Данные кэшируются
        cached_orders = redis_client.get('orders')
        assert cached_orders is not None

        # Проверяем, что кэш истечет через заданное время (60 секунд)
        redis_client.expire('orders', 60)

        # Проверяем истечение времени через 61 секунду
        import time
        time.sleep(61)

        cached_orders_after_expiration = redis_client.get('orders')
        assert cached_orders_after_expiration is None


def test_login_attempts_limit(redis_client, app, new_user_data):
    """Тестируем ограничение количества попыток входа с использованием Redis."""
    with app.test_client() as client:
        # Совершаем 5 неудачных попыток входа
        login_data = {
            "email": new_user_data['email'],
            "password": "wrongpassword"
        }
        for _ in range(5):
            response = client.post('/auth/login', json=login_data)
            assert response.status_code == 401

        # После 5 неудачных попыток, проверяем, что запрос заблокирован
        response = client.post('/auth/login', json=login_data)
        assert response.status_code == 429
        assert response.json['error'] == 'Too many login attempts. Please try again later.'

        # Проверяем, что количество попыток в Redis увеличено
        attempts_key = f"login_attempts:{new_user_data['email']}"
        attempts = redis_client.get(attempts_key)
        assert int(attempts) == 5
