from flask import Blueprint, request, jsonify
from app import db
from app.models import Client

bp = Blueprint('client_routes', __name__, url_prefix='/clients')

@bp.route('/', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([{'id': c.id, 'name': c.name, 'email': c.email} for c in clients])

@bp.route('/', methods=['POST'])
def create_client():
    data = request.get_json()
    client = Client(name=data['name'], email=data['email'], phone=data.get('phone'))
    db.session.add(client)
    db.session.commit()
    return jsonify({'message': 'Client created successfully', 'id': client.id}), 201
