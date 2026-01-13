from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))

    def to_dict(self):
        return {
            'username': self.username,
            'role': self.role,
            'email': self.email
        }

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    sku = db.Column(db.String(50), unique=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'stock': self.stock,
            'price': self.price,
            'sku': self.sku
        }

class BillingRecord(db.Model):
    __tablename__ = 'billing_records'
    id = db.Column(db.Integer, primary_key=True)  # Using auto-increment or we can use the timestamp ID logic if strict compatibility is needed, but auto-increment is better for DB
    # Note: Frontend might expect 'id' to be the timestamp one. We will adapt in the route.
    timestamp_id = db.Column(db.BigInteger, unique=True) # To store the frontend-style ID
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal = db.Column(db.Float, default=0.0)
    discount_percent = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    gst_rate = db.Column(db.Float, default=0.0)
    gst_amount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    created_by = db.Column(db.String(80)) # username snapshot
    
    items = db.relationship('BillingItem', backref='billing_record', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.timestamp_id,
            'timestamp': self.timestamp.isoformat(),
            'subtotal': self.subtotal,
            'discountPercent': self.discount_percent,
            'discountAmount': self.discount_amount,
            'gstRate': self.gst_rate,
            'gstAmount': self.gst_amount,
            'total': self.total,
            'created_by': self.created_by,
            'items': [item.to_dict() for item in self.items]
        }

class BillingItem(db.Model):
    __tablename__ = 'billing_items'
    id = db.Column(db.Integer, primary_key=True)
    billing_id = db.Column(db.Integer, db.ForeignKey('billing_records.id'), nullable=False)
    product_id = db.Column(db.Integer) # Keep it even if product deleted
    product_name = db.Column(db.String(100)) # Snapshot
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float) # Snapshot price at time of sale
    
    def to_dict(self):
        return {
            'id': self.product_id, # Frontend expects 'id' to be product id in the items list usually, effectively reconstructing the payload
            'name': self.product_name,
            'quantity': self.quantity,
            'price': self.price
        }
