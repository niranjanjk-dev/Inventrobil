from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from extensions import db
from models import User
from utils import hash_password, verify_password, owner_required, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username', '').lower()
        password = data.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user and verify_password(user.password, password):
            session.permanent = True
            session['user'] = user.to_dict()
            
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('main.home')}), 200
            return redirect(url_for('main.home'))
        
        error = 'Invalid username or password'
        if request.is_json:
            return jsonify({'success': False, 'error': error}), 401
        return render_template('login.html', error=error)
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/user-info')
@login_required
def user_info():
    """Get current user info"""
    from utils import get_user_permissions # Import here to avoid circulars if any
    return jsonify({
        'user': session['user'],
        'permissions': get_user_permissions(session['user']['role'])
    })

# ============= USER MANAGEMENT ROUTES (Owner Only) =============

@auth_bp.route('/api/users', methods=['GET'])
@owner_required
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@auth_bp.route('/api/user/change-password', methods=['POST'])
@login_required
def change_password():
    """Change password for current user"""
    data = request.json
    username = session['user']['username']
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not verify_password(user.password, old_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    user.password = hash_password(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Password changed successfully'})

@auth_bp.route('/api/user/<username>/reset-password', methods=['POST'])
@owner_required
def reset_password(username):
    """Reset password for a user (Owner only)"""
    data = request.json
    new_password = data.get('new_password', '')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    user.password = hash_password(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Password reset for {username}'})

@auth_bp.route('/api/user', methods=['POST'])
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
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400
    
    if role not in ['Owner', 'Manager', 'Cashier']:
        return jsonify({'error': 'Invalid role'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    new_user = User(
        username=username,
        password=hash_password(password),
        role=role,
        email=email
    )
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user': new_user.to_dict()
    }), 201

@auth_bp.route('/api/user/<username>', methods=['DELETE'])
@owner_required
def delete_user(username):
    """Delete a user (Owner only)"""
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if username == session['user']['username']:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'User {username} deleted'})
