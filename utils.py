from functools import wraps
from flask import session, redirect, url_for, jsonify
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

# We will upgrade to PBKDF2 (Werkzeug default) for new system
# but if we needed strict compat with old SHA256 hashes we could keep it.
# Given it's a "production upgrade", we should use secure hashing.

def hash_password(password):
    """Hash password using Werkzeug (PBKDF2)"""
    return generate_password_hash(password)

def verify_password(stored_password, provided_password):
    """Verify password"""
    if stored_password.startswith('scrypt:') or stored_password.startswith('pbkdf2:'):
         return check_password_hash(stored_password, provided_password)
    
    # Fallback/Legacy support for the old SHA256 if we imported old data directly (Optional, but safe)
    if len(stored_password) == 64: 
        return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()
        
    return check_password_hash(stored_password, provided_password)

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            # Check if this is an API call
            # The original code did a redirect. We Keep exact internal behavior.
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        if session['user']['role'] != 'Owner':
            return jsonify({'error': 'Unauthorized - Owner access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        if session['user']['role'] not in ['Manager', 'Owner']:
            return jsonify({'error': 'Unauthorized - Manager access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def cashier_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        if session['user']['role'] not in ['Cashier', 'Manager', 'Owner']:
            return jsonify({'error': 'Unauthorized - Cashier access required'}), 403
        return f(*args, **kwargs)
    return decorated_function
