from flask import Blueprint, render_template, request, jsonify, session
from extensions import db
from models import Product, BillingRecord, BillingItem
from utils import cashier_required, get_user_permissions
from datetime import datetime

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/billing')
@cashier_required
def billing_page():
    """Render billing & POS page"""
    permissions = get_user_permissions(session['user']['role'])
    products = Product.query.all()
    # History: newest first
    history = BillingRecord.query.order_by(BillingRecord.timestamp.desc()).all()
    
    return render_template('billing.html', 
        user=session['user'],
        permissions=permissions,
        products=[p.to_dict() for p in products],
        billing_history=[h.to_dict() for h in history]
    )

@billing_bp.route('/api/billing', methods=['POST'])
@cashier_required
def add_billing_record():
    """Add a billing record"""
    data = request.json
    
    try:
        # 1. Update stock
        for item in data['items']:
            product = Product.query.get(item['id'])
            if product:
                if product.stock < item['quantity']:
                     return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
                product.stock -= item['quantity']
        
        # 2. Create Billing Record
        timestamp_id = int(datetime.now().timestamp() * 1000)
        
        record = BillingRecord(
            timestamp_id=timestamp_id,
            timestamp=datetime.now(),
            subtotal=data['subtotal'],
            discount_percent=data['discountPercent'],
            discount_amount=data['discountAmount'],
            gst_rate=data['gstRate'],
            gst_amount=data['gstAmount'],
            total=data['total'],
            created_by=session['user']['username']
        )
        db.session.add(record)
        db.session.flush() # Get ID
        
        # 3. Create Items
        billing_items_list = []
        for item in data['items']:
            # We fetch again or use the one from loop above. 
            # Note: item['id'] is Product ID from frontend
            # We need to snapshot name/price in case product changes later?
            # Original code just stored what frontend sent or linked?
            # Original: 'items': data['items'] stored directly.
            # We should be robust.
            
            p = Product.query.get(item['id'])
            p_name = p.name if p else "Unknown Product"
            p_price = p.price if p else 0
            
            b_item = BillingItem(
                billing_id=record.id,
                product_id=item['id'],
                product_name=p_name,
                quantity=item['quantity'],
                price=p_price
            )
            db.session.add(b_item)
            # Reconstruct for response to match old format
            billing_items_list.append({
                'id': item['id'],
                'name': p_name,
                'category': p.category if p else '',
                'stock': p.stock if p else 0,
                'price': p_price,
                'sku': p.sku if p else '',
                'quantity': item['quantity']
            })

        db.session.commit()
        
        # Return format must match original exactly
        response_record = record.to_dict()
        # Override items with the full details frontend might expect if it renders them immediately
        # The to_dict() returns a simplified item list. 
        # Check original: it returned 'items': data['items'] (which has full product details usually)
        response_record['items'] = data['items'] # Echo back what was sent + ID updates if any
        response_record['id'] = timestamp_id
        
        return jsonify(response_record), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@billing_bp.route('/api/billing', methods=['GET'])
@cashier_required
def get_billing_history():
    """Get billing history"""
    history = BillingRecord.query.order_by(BillingRecord.timestamp.desc()).all()
    return jsonify([h.to_dict() for h in history])
