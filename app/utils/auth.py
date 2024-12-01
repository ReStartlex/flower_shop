from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.models import Client, RoleEnum

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Получаем идентификатор клиента из JWT
        client_id = get_jwt_identity()
        # Ищем клиента по его ID
        client = Client.query.get(client_id)
        
        # Если клиент не найден или его роль не "admin"
        if not client or client.role != RoleEnum.ADMIN:
            return jsonify({"error": "Admin access required"}), 403
        
        # Если проверка прошла, передаем управление дальше
        return f(*args, **kwargs)
    
    return decorated_function
