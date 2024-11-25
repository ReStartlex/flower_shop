from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app import db, logger
from app.models import Client

bp = Blueprint('auth_routes', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Alexey Savchishen"
            email:
              type: string
              example: "dlyadchebitpgu.com"
            password:
              type: string
              example: "password123"
    responses:
      201:
        description: User registered successfully
      400:
        description: Email already exists
    """
    data = request.get_json()
    
    
    if not data.get('name') or not data.get('email') or not data.get('password'):
        logger.error("Missing required registration fields.")
        return jsonify({'error': 'Name, email, and password are required'}), 400

    
    if Client.query.filter_by(email=data['email']).first():
        logger.error(f"Registration failed: email {data['email']} already exists.")
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    try:
        new_client = Client(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
        )
        new_client.password = hashed_password
        db.session.add(new_client)
        db.session.commit()
        logger.info(f"User {data['email']} registered successfully.")
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        logger.error(f"Error during user registration: {e}")
        return jsonify({'error': 'Registration failed due to server error'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """
    User login
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: "dlyadchebitpgu.com"
            password:
              type: string
              example: "password123"
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()

    
    if not data.get('email') or not data.get('password'):
        logger.error("Missing email or password in login request.")
        return jsonify({'error': 'Email and password are required'}), 400

    client = Client.query.filter_by(email=data['email']).first()

    
    if not client or not check_password_hash(client.password, data['password']):
        logger.warning(f"Invalid login attempt for email {data['email']}.")
        return jsonify({'error': 'Invalid credentials'}), 401

   
    try:
        access_token = create_access_token(identity=client.id, additional_claims={
            'name': client.name,
            'email': client.email
        })
        logger.info(f"User {data['email']} logged in successfully.")
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        logger.error(f"Error during login for {data['email']}: {e}")
        return jsonify({'error': 'Login failed due to server error'}), 500
