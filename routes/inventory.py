from flask import Blueprint, render_template, request, jsonify, session
from extensions import db
from models import Product
from utils import cashier_required, manager_required, owner_required, get_user_permissions
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory')
@cashier_required
def inventory_page():
    """Render inventory management page"""
    permissions = get_user_permissions(session['user']['role'])
    can_edit = permissions['edit_inventory']
    products = Product.query.order_by(Product.id).all()
    
    return render_template('inventory.html', 
        user=session['user'],
        permissions=permissions,
        products=[p.to_dict() for p in products],
        can_edit=can_edit,
        show_add_form=False
    )

@inventory_bp.route('/api/products', methods=['GET'])
@cashier_required
def get_products():
    """Get all products"""
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@inventory_bp.route('/api/product', methods=['POST'])
@manager_required
def add_product():
    """Add a new product"""
    data = request.json
    
    try:
        new_product = Product(
            name=data['name'],
            category=data['category'],
            stock=int(data['stock']),
            price=float(data['price']),
            sku=data['sku']
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@inventory_bp.route('/api/product/<int:product_id>', methods=['PUT'])
@manager_required
def update_product(product_id):
    """Update an existing product"""
    data = request.json
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    product.name = data.get('name', product.name)
    product.category = data.get('category', product.category)
    product.stock = int(data.get('stock', product.stock))
    product.price = float(data.get('price', product.price))
    product.sku = data.get('sku', product.sku)
    
    db.session.commit()
    return jsonify(product.to_dict())

@inventory_bp.route('/api/product/<int:product_id>', methods=['DELETE'])
@manager_required
def delete_product(product_id):
    """Delete a product"""
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return jsonify({'success': True})

@inventory_bp.route('/api/export', methods=['GET'])
@owner_required
def export_inventory():
    """Export inventory as JSON"""
    products = Product.query.all()
    return jsonify({
        'exportDate': datetime.now().isoformat(),
        'totalProducts': len(products),
        'products': [p.to_dict() for p in products]
    })

@inventory_bp.route('/api/import', methods=['POST'])
@owner_required
def import_inventory():
    """Import inventory from JSON"""
    data = request.json
    
    if not data.get('products') or not isinstance(data['products'], list):
        return jsonify({'error': 'Invalid inventory data format'}), 400
    
    # Minimalist import: Clear all and replace or upsert? 
    # Original code: products = data['products'] -> Replaces *entire* list.
    # We will replicate this destructively for compatibility, but safer is a Transaction.
    
    try:
        # Clear existing
        Product.query.delete()
        
        count = 0
        for p_data in data['products']:
             p = Product(
                 # ID might be included, we can try to preserve it or let DB auto-increment
                 # For safety with PostgreSQL sequences, usually better to let DB handle ID unless restore.
                 # Original code preserved structure. Let's try to preserve ID if possible but auto-inc logic is cleaner.
                 # We will ignore ID for now and let DB assign, unless user relies on IDs strictly.
                 # If IDs are used in relationships, this is risky. But current backend was single-user single-session mostly.
                 name=p_data['name'],
                 category=p_data['category'],
                 stock=p_data['stock'],
                 price=p_data['price'],
                 sku=p_data['sku']
             )
             db.session.add(p)
             count += 1
        
        db.session.commit()
        return jsonify({'success': True, 'imported': count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
