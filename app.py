"""
InventroBil Web - Flask Server-Side Application with User Authentication
Features: User Login, Role-Based Access Control (Owner, Manager, Cashier)
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from datetime import datetime, timedelta
from functools import wraps
import json
import os
import hashlib

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
Session(app)

# In-memory storage (replace with database in production)
products = [
    { 'id': 1, 'name': 'PVC Pipe 1/2 inch', 'category': 'Plumbing', 'stock': 50, 'price': 10.99, 'sku': 'PVC001' },
    { 'id': 2, 'name': 'Copper Wire 2.5mm', 'category': 'Electronics', 'stock': 5, 'price': 15.50, 'sku': 'COP001' },
    { 'id': 3, 'name': 'Switch Socket', 'category': 'Electronics', 'stock': 20, 'price': 5.50, 'sku': 'SWT001' },
    { 'id': 4, 'name': 'PVC Pipe 1 inch', 'category': 'Plumbing', 'stock': 35, 'price': 18.99, 'sku': 'PVC002' },
    { 'id': 5, 'name': 'Electrical Box', 'category': 'Electronics', 'stock': 8, 'price': 8.75, 'sku': 'ELB001' },
]

billing_history = []

# ============= USER MANAGEMENT =============

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from file"""
    users_file = 'users.json'
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            return json.load(f)
    
    # Default users (initialization)
    default_users = {
        'owner': {
            'username': 'owner',
            'password': hash_password('owner123'),
            'role': 'Owner',
            'email': 'owner@inventrobil.com'
        },
        'manager': {
            'username': 'manager',
            'password': hash_password('manager123'),
            'role': 'Manager',
            'email': 'manager@inventrobil.com'
        },
        'cashier': {
            'username': 'cashier',
            'password': hash_password('cashier123'),
            'role': 'Cashier',
            'email': 'cashier@inventrobil.com'
        }
    }
    save_users(default_users)
    return default_users

def save_users(users):
    """Save users to file"""
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

# Load users at startup
USERS = load_users()

# ============= DECORATORS =============

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    """Decorator to check if user is Owner"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        if session['user']['role'] != 'Owner':
            return jsonify({'error': 'Unauthorized - Owner access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Decorator to check if user is Manager or Owner"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        if session['user']['role'] not in ['Manager', 'Owner']:
            return jsonify({'error': 'Unauthorized - Manager access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def cashier_required(f):
    """Decorator to check if user is Cashier, Manager, or Owner"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        if session['user']['role'] not in ['Cashier', 'Manager', 'Owner']:
            return jsonify({'error': 'Unauthorized - Cashier access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ============= AUTH ROUTES =============

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username', '').lower()
        password = data.get('password', '')
        
        user = USERS.get(username)
        if user and user['password'] == hash_password(password):
            session.permanent = True
            session['user'] = {
                'username': user['username'],
                'role': user['role'],
                'email': user['email']
            }
            
            if request.is_json:
                return jsonify({'success': True, 'redirect': '/'}), 200
            return redirect('/')
        
        error = 'Invalid username or password'
        if request.is_json:
            return jsonify({'success': False, 'error': error}), 401
        return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/user-info')
@login_required
def user_info():
    """Get current user info"""
    return jsonify({
        'user': session['user'],
        'permissions': get_user_permissions(session['user']['role'])
    })

def get_user_permissions(role):
    """Get permissions based on role"""
    permissions = {
        'Owner': {
            'view_inventory': True,
            'edit_inventory': True,
            'manage_billing': True,
            'view_reports': True,
            'manage_users': True,
            'change_password': True,
            'access_settings': True
        },
        'Manager': {
            'view_inventory': True,
            'edit_inventory': True,
            'manage_billing': True,
            'view_reports': True,
            'manage_users': False,
            'change_password': False,
            'access_settings': False
        },
        'Cashier': {
            'view_inventory': True,
            'edit_inventory': False,
            'manage_billing': True,
            'view_reports': False,
            'manage_users': False,
            'change_password': False,
            'access_settings': False
        }
    }
    return permissions.get(role, {})

# ============= USER MANAGEMENT ROUTES (Owner Only) =============

@app.route('/api/users', methods=['GET'])
@owner_required
def get_users():
    """Get all users"""
    users_list = []
    for username, user in USERS.items():
        users_list.append({
            'username': user['username'],
            'role': user['role'],
            'email': user['email']
        })
    return jsonify(users_list)

@app.route('/api/user/change-password', methods=['POST'])
@login_required
def change_password():
    """Change password for current user"""
    data = request.json
    username = session['user']['username']
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    user = USERS.get(username)
    if not user or user['password'] != hash_password(old_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    user['password'] = hash_password(new_password)
    save_users(USERS)
    
    return jsonify({'success': True, 'message': 'Password changed successfully'})

@app.route('/api/user/<username>/reset-password', methods=['POST'])
@owner_required
def reset_password(username):
    """Reset password for a user (Owner only)"""
    data = request.json
    new_password = data.get('new_password', '')
    
    if username not in USERS:
        return jsonify({'error': 'User not found'}), 404
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    USERS[username]['password'] = hash_password(new_password)
    save_users(USERS)
    
    return jsonify({'success': True, 'message': f'Password reset for {username}'})

@app.route('/api/user', methods=['POST'])
@owner_required
def create_user():
    """Create a new user (Owner only)"""
    data = request.json
    username = data.get('username', '').lower()
    password = data.get('password', '')
    role = data.get('role', '')
    email = data.get('email', '')
    
    if not username or not password or not role:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if username in USERS:
        return jsonify({'error': 'User already exists'}), 400
    
    if role not in ['Owner', 'Manager', 'Cashier']:
        return jsonify({'error': 'Invalid role'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    USERS[username] = {
        'username': username,
        'password': hash_password(password),
        'role': role,
        'email': email
    }
    save_users(USERS)
    
    return jsonify({
        'success': True,
        'user': {
            'username': username,
            'role': role,
            'email': email
        }
    }), 201

@app.route('/api/user/<username>', methods=['DELETE'])
@owner_required
def delete_user(username):
    """Delete a user (Owner only)"""
    if username not in USERS:
        return jsonify({'error': 'User not found'}), 404
    
    if username == session['user']['username']:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    del USERS[username]
    save_users(USERS)
    
    return jsonify({'success': True, 'message': f'User {username} deleted'})

# ============= PAGE ROUTES =============

@app.route('/')
def index():
    """Redirect to login or home based on session"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('home'))

@app.route('/home')
@login_required
def home():
    """Render home page with dashboard stats"""
    permissions = get_user_permissions(session['user']['role'])
    total_products = len(products)
    low_stock_count = sum(1 for p in products if p['stock'] < 10)
    total_transactions = len(billing_history)
    total_revenue = sum(record['total'] for record in billing_history)
    
    return render_template('home.html',
        user=session['user'],
        permissions=permissions,
        total_products=total_products,
        low_stock_count=low_stock_count,
        total_transactions=total_transactions,
        total_revenue=total_revenue
    )

# ============= API ROUTES =============

@app.route('/inventory')
@cashier_required
def inventory():
    """Render inventory management page"""
    permissions = get_user_permissions(session['user']['role'])
    can_edit = permissions['edit_inventory']
    
    return render_template('inventory.html', 
        user=session['user'],
        permissions=permissions,
        products=products,
        can_edit=can_edit
    )

@app.route('/billing')
@cashier_required
def billing():
    """Render billing & POS page"""
    permissions = get_user_permissions(session['user']['role'])
    
    return render_template('billing.html', 
        user=session['user'],
        permissions=permissions,
        products=products,
        billing_history=billing_history
    )

@app.route('/settings')
@owner_required
def settings():
    """Render settings page (Owner only)"""
    permissions = get_user_permissions(session['user']['role'])
    users_list = []
    for username, user in USERS.items():
        users_list.append({
            'username': user['username'],
            'role': user['role'],
            'email': user['email']
        })
    
    return render_template('settings.html',
        user=session['user'],
        permissions=permissions,
        users=users_list
    )

# ============= API ROUTES =============

@app.route('/api/products', methods=['GET'])
@cashier_required
def get_products():
    """Get all products"""
    return jsonify(products)

@app.route('/api/product', methods=['POST'])
@manager_required
def add_product():
    """Add a new product"""
    global products
    data = request.json
    
    new_product = {
        'id': max([p['id'] for p in products], default=0) + 1,
        'name': data['name'],
        'category': data['category'],
        'stock': int(data['stock']),
        'price': float(data['price']),
        'sku': data['sku']
    }
    
    products.append(new_product)
    return jsonify(new_product), 201

@app.route('/api/product/<int:product_id>', methods=['PUT'])
@manager_required
def update_product(product_id):
    """Update an existing product"""
    global products
    data = request.json
    
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    product.update({
        'name': data.get('name', product['name']),
        'category': data.get('category', product['category']),
        'stock': int(data.get('stock', product['stock'])),
        'price': float(data.get('price', product['price'])),
        'sku': data.get('sku', product['sku'])
    })
    
    return jsonify(product)

@app.route('/api/product/<int:product_id>', methods=['DELETE'])
@manager_required
def delete_product(product_id):
    """Delete a product"""
    global products
    products = [p for p in products if p['id'] != product_id]
    return jsonify({'success': True})

@app.route('/api/billing', methods=['POST'])
@cashier_required
def add_billing_record():
    """Add a billing record"""
    global products, billing_history
    data = request.json
    
    # Update stock for each item
    for item in data['items']:
        product = next((p for p in products if p['id'] == item['id']), None)
        if product:
            product['stock'] -= item['quantity']
    
    # Create billing record
    record = {
        'id': int(datetime.now().timestamp() * 1000),
        'timestamp': datetime.now().isoformat(),
        'items': data['items'],
        'subtotal': data['subtotal'],
        'discountPercent': data['discountPercent'],
        'discountAmount': data['discountAmount'],
        'gstRate': data['gstRate'],
        'gstAmount': data['gstAmount'],
        'total': data['total'],
        'created_by': session['user']['username']
    }
    
    billing_history.insert(0, record)
    return jsonify(record), 201

@app.route('/api/billing', methods=['GET'])
@cashier_required
def get_billing_history():
    """Get billing history"""
    return jsonify(billing_history)

@app.route('/api/export', methods=['GET'])
@owner_required
def export_inventory():
    """Export inventory as JSON"""
    return jsonify({
        'exportDate': datetime.now().isoformat(),
        'totalProducts': len(products),
        'products': products
    })

@app.route('/api/import', methods=['POST'])
@owner_required
def import_inventory():
    """Import inventory from JSON"""
    global products
    data = request.json
    
    if not data.get('products') or not isinstance(data['products'], list):
        return jsonify({'error': 'Invalid inventory data format'}), 400
    
    products = data['products']
    return jsonify({'success': True, 'imported': len(products)})

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    if 'user' in session:
        permissions = get_user_permissions(session['user']['role'])
        return render_template('home.html', 
            user=session['user'],
            permissions=permissions,
            total_products=len(products),
            low_stock_count=sum(1 for p in products if p['stock'] < 10),
            total_transactions=len(billing_history),
            total_revenue=sum(record['total'] for record in billing_history)
        ), 404
    return redirect(url_for('login'))

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
