from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app import db, logger
from app.models import Client
from app.utils.auth import admin_required  # Импортируем декоратор
import json

bp = Blueprint('client_routes', __name__, url_prefix='/clients')

@bp.route('/', methods=['GET'])
@jwt_required()
@admin_required  # Добавлен декоратор для проверки админских прав
def get_clients():
    """
    Get all clients
    --- 
    tags:
      - Clients
    responses:
      200:
        description: A list of clients
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "Savchishen Alexey"
              email:
                type: string
                example: "dlyauchebitpgy@gmail.com"
    """
    redis_client = current_app.redis_client

    cached_clients = redis_client.get('clients')

    if cached_clients:
        # Если данные есть в кэше, возвращаем их
        logger.info("Returning clients from cache.")
        clients = json.loads(cached_clients)  # Десериализуем JSON из кэша
    else:
        # Если данных нет в кэше, получаем из БД и сохраняем в кэш
        logger.info("Fetching clients from database.")
        clients = [{
            'id': c.id,
            'name': c.name,
            'email': c.email
        } for c in Client.query.all()]

        # Сохраняем в кэш с TTL 60 секунд (сериализация в JSON)
        redis_client.set('clients', json.dumps(clients), ex=60)
        logger.info("Clients data cached.")

    return jsonify(clients), 200

@bp.route('/', methods=['POST'])
@jwt_required()
@admin_required  # Только администратор может создавать клиентов
def create_client():
    """
    Create a new client
    --- 
    tags:
      - Clients
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Savchishen Alexey"
            email:
              type: string
              example: "dlyauchebitpgy@gmail.com"
            phone:
              type: string
              example: "+79539688575"
    responses:
      201:
        description: Client created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Client created successfully"
            id:
              type: integer
              example: 1
    """
    data = request.get_json()
    logger.info(f"Received client creation request: {data}")

    # Валидация входных данных
    if not data.get('name') or not data.get('email'):
        logger.error("Missing required fields: name or email.")
        return jsonify({'error': 'Name and email are required'}), 400

    try:
        # Создание нового клиента
        client = Client(name=data['name'], email=data['email'], phone=data.get('phone'))
        db.session.add(client)
        db.session.commit()
        logger.info(f"Client created with ID {client.id}")

        
        redis_client = current_app.redis_client
        # Сбрасываем кэш, так как данные изменены
        redis_client.delete('clients')
        logger.info("Cleared clients cache.")

        return jsonify({'message': 'Client created successfully', 'id': client.id}), 201

    except Exception as e:
        logger.error(f"Error while creating client: {e}")
        return jsonify({'error': 'Client creation failed'}), 500
