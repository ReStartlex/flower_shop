import json
from flask_jwt_extended import create_access_token
from app import db
from app.models import Client

def test_get_clients(client, redis_client, auth_headers):
    # Добавляем клиентов в базу данных
    client_1 = Client(name="Client One", email="client1@example.com")
    client_2 = Client(name="Client Two", email="client2@example.com")
    db.session.add_all([client_1, client_2])
    db.session.commit()

    # Тестирование получения клиентов из базы данных
    response = client.get("/clients/", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["name"] == "Client One"
    assert data[1]["email"] == "client2@example.com"

    # Тестирование получения данных из кэша
    redis_client.set("clients", json.dumps(data))
    response = client.get("/clients/", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json() == data


def test_create_client(client, redis_client, auth_headers):
    # Успешное создание клиента
    payload = {"name": "Client New", "email": "client.new@example.com", "phone": "+123456789"}
    response = client.post("/clients/", headers=auth_headers, json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Client created successfully"
    assert "id" in data

    # Проверка, что клиент добавлен в базу данных
    client_in_db = Client.query.get(data["id"])
    assert client_in_db is not None
    assert client_in_db.name == "Client New"

    # Проверка, что кэш сброшен
    assert redis_client.get("clients") is None

    # Ошибка при отсутствии обязательных полей
    payload = {"name": "Missing Email"}
    response = client.post("/clients/", headers=auth_headers, json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Name and email are required"
