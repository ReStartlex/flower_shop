from app import db
from datetime import datetime
from enum import Enum

# Определение Enum для ролей
class RoleEnum(Enum):
    ADMIN = 'admin'
    CLIENT = 'client'

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=True)  # Сделано уникальным
    password = db.Column(db.String(128), nullable=False)  # Поле для хранения пароля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.Enum(RoleEnum), default=RoleEnum.CLIENT)  # Роль пользователя через Enum

    def __repr__(self):
        return f'<Client {self.name}>'

    def set_role(self, role):
        """Метод для изменения роли пользователя"""
        if isinstance(role, RoleEnum):
            self.role = role
        else:
            raise ValueError(f"Invalid role: {role}")
        db.session.commit()

    def get_role(self):
        """Метод для получения роли пользователя"""
        return self.role

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship('Client', backref=db.backref('orders', lazy=True))
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f'<Order {self.id}>'
