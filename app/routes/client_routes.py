from flask import Blueprint, request, jsonify
from app import db, logger
from app.models import Client

bp = Blueprint('client_routes', __name__, url_prefix='/clients')

@bp.route('/', methods=['GET'])
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
    logger.info("Fetching all clients.")
    clients = Client.query.all()
    logger.info(f"Found {len(clients)} clients.")
    return jsonify([{'id': c.id, 'name': c.name, 'email': c.email} for c in clients]), 200

@bp.route('/', methods=['POST'])
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
    client = Client(name=data['name'], email=data['email'], phone=data.get('phone'))
    db.session.add(client)
    db.session.commit()
    logger.info(f"Client created with ID {client.id}")
    return jsonify({'message': 'Client created successfully', 'id': client.id}), 201
