from flask import Blueprint, request, jsonify
from app import db, logger
from app.models import Order, Client, Product

bp = Blueprint('order_routes', __name__, url_prefix='/orders')

@bp.route('/', methods=['GET'])
def get_orders():
    """
    Get all orders
    ---
    tags:
      - Orders
    responses:
      200:
        description: A list of orders
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              client_id:
                type: integer
                example: 1
              product_id:
                type: integer
                example: 2
              quantity:
                type: integer
                example: 3
              total_price:
                type: number
                example: 150.75
    """
    logger.info("Fetching all orders.")
    orders = Order.query.all()
    logger.info(f"Found {len(orders)} orders.")
    return jsonify([{
        'id': o.id, 
        'client_id': o.client_id, 
        'product_id': o.product_id, 
        'quantity': o.quantity, 
        'total_price': o.total_price
    } for o in orders]), 200

@bp.route('/', methods=['POST'])
def create_order():
    """
    Create a new order
    ---
    tags:
      - Orders
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            client_id:
              type: integer
              example: 1
            product_id:
              type: integer
              example: 2
            quantity:
              type: integer
              example: 3
    responses:
      201:
        description: Order created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Order created successfully"
            id:
              type: integer
              example: 1
      400:
        description: Invalid client or product ID or insufficient stock
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid client or product ID"
    """
    data = request.get_json()
    logger.info(f"Received order creation request: {data}")

    client = Client.query.get(data['client_id'])
    product = Product.query.get(data['product_id'])

    if not client or not product:
        logger.error("Invalid client or product ID.")
        return jsonify({'error': 'Invalid client or product ID'}), 400

    if product.stock < data['quantity']:
        logger.error("Not enough stock available.")
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
    logger.info(f"Order created successfully with ID {order.id}")
    return jsonify({'message': 'Order created successfully', 'id': order.id}), 201

@bp.route('/<int:order_id>/', methods=['DELETE'])
def delete_order(order_id):
    """
    Delete an order
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        required: true
        type: integer
        example: 1
    responses:
      200:
        description: Order deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Order deleted successfully"
      404:
        description: Order not found
    """
    logger.info(f"Attempting to delete order with ID {order_id}")
    order = Order.query.get_or_404(order_id)
    product = Product.query.get(order.product_id)

    if product:
        product.stock += order.quantity

    db.session.delete(order)
    db.session.commit()
    logger.info(f"Order with ID {order_id} deleted successfully.")
    return jsonify({'message': 'Order deleted successfully'}), 200
