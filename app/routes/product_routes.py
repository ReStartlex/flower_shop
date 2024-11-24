from flask import Blueprint, request, jsonify
from app import db
from app.models import Product

bp = Blueprint('product_routes', __name__, url_prefix='/products')

@bp.route('/', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id, 
        'name': p.name, 
        'description': p.description, 
        'price': p.price, 
        'stock': p.stock
    } for p in products])

@bp.route('/', methods=['POST'])
def create_product():
    data = request.get_json()
    product = Product(
        name=data['name'], 
        description=data.get('description'), 
        price=data['price'], 
        stock=data.get('stock', 0)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully', 'id': product.id}), 201

@bp.route('/<int:product_id>/', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

@bp.route('/<int:product_id>/', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})
