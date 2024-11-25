from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db, logger
from app.models import Product

bp = Blueprint('product_routes', __name__, url_prefix='/products')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    """
    Get all products
    ---
    tags:
      - Products
    responses:
      200:
        description: A list of products
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
                example: "Rose Bouquet"
              description:
                type: string
                example: "A bouquet of fresh roses"
              price:
                type: number
                example: 29.99
              stock:
                type: integer
                example: 100
    """
    logger.info("Fetching all products.")
    products = Product.query.all()
    logger.info(f"Found {len(products)} products.")
    return jsonify([{
        'id': p.id, 
        'name': p.name, 
        'description': p.description, 
        'price': p.price, 
        'stock': p.stock
    } for p in products]), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """
    Create a new product
    ---
    tags:
      - Products
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Rose Bouquet"
            description:
              type: string
              example: "A bouquet of fresh roses"
            price:
              type: number
              example: 29.99
            stock:
              type: integer
              example: 100
    responses:
      201:
        description: Product created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Product created successfully"
            id:
              type: integer
              example: 1
    """
    data = request.get_json()
    logger.info(f"Received product creation request: {data}")
    product = Product(
        name=data['name'], 
        description=data.get('description'), 
        price=data['price'], 
        stock=data.get('stock', 0)
    )
    db.session.add(product)
    db.session.commit()
    logger.info(f"Product created successfully with ID {product.id}")
    return jsonify({'message': 'Product created successfully', 'id': product.id}), 201

@bp.route('/<int:product_id>/', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """
    Update a product
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        required: true
        type: integer
        example: 1
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Rose Bouquet"
            description:
              type: string
              example: "A bouquet of fresh roses"
            price:
              type: number
              example: 29.99
            stock:
              type: integer
              example: 100
    responses:
      200:
        description: Product updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Product updated successfully"
    """
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    logger.info(f"Updating product with ID {product_id}: {data}")
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    db.session.commit()
    logger.info(f"Product with ID {product_id} updated successfully.")
    return jsonify({'message': 'Product updated successfully'}), 200

@bp.route('/<int:product_id>/', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """
    Delete a product
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        required: true
        type: integer
        example: 1
    responses:
      200:
        description: Product deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Product deleted successfully"
      404:
        description: Product not found
    """
    logger.info(f"Attempting to delete product with ID {product_id}")
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    logger.info(f"Product with ID {product_id} deleted successfully.")
    return jsonify({'message': 'Product deleted successfully'}), 200
