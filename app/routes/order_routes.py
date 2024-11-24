from flask import Blueprint, request, jsonify
from app import db
from app.models import Order, Client, Product

bp = Blueprint('order_routes', __name__, url_prefix='/orders')

@bp.route('/', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([{
        'id': o.id, 
        'client_id': o.client_id, 
        'product_id': o.product_id, 
        'quantity': o.quantity, 
        'total_price': o.total_price
    } for o in orders])

@bp.route('/', methods=['POST'])
def create_order():
    data = request.get_json()
    client = Client.query.get(data['client_id'])
    product = Product.query.get(data['product_id'])

    if not client or not product:
        return jsonify({'error': 'Invalid client or product ID'}), 400

    if product.stock < data['quantity']:
        return jsonify({'error': 'Not enough stock available'}), 400

    total_price = product.price * data['quantity']
    order = Order(
        client_id=data['client_id'], 
        product_id=data['product_id'], 
        quantity=data['quantity'], 
        total_price=total_price
    )
    product.stock -= data['quantity']
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order created successfully', 'id': order.id}), 201

@bp.route('/<int:order_id>/', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    product = Product.query.get(order.product_id)

    if product:
        product.stock += order.quantity

    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'})
