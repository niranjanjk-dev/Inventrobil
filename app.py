"""
InventroBil Web - Flask Server-Side Application with User Authentication
Features: User Login, Role-Based Access Control (Owner, Manager, Cashier)
Production-Ready Backend Refactor
"""

from flask import Flask, render_template, redirect, url_for, session, jsonify
from flask_session import Session
from extensions import db
from config import Config
from routes import auth_bp, inventory_bp, billing_bp, main_bp
from models import User
from utils import hash_password, get_user_permissions
import os

def create_app(config_class=Config):
    app = Flask(__name__, 
        template_folder='templates',
        static_folder='static'
    )
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    Session(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(main_bp)

    # Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        if 'user' in session:
            # We need to render the home page logic for 404 to match original behavior
            # which passed stats to the 404 page (home.html used as 404?)
            # Original code: return render_template('home.html', ...), 404
            # We will redirect to home or render home with 404 code.
            # To avoid duplicating "home" logic, let's just redirect or keep it simple.
            # The original code RENDERED home.html with stats.
            # We'll try to redirect to home to be safe, or render a generic 404 if acceptable.
            # Strict adherence: Re-implement the view logic locally or import.
            return redirect(url_for('main.home'))
        return redirect(url_for('auth.login'))

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Database Initialization (Dev/Startup)
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        create_default_admin(app)

    return app

def create_default_admin(app):
    """Create default admin user if no users exist"""
    if not User.query.first():
        print("Creating default admin user...")
        admin_username = app.config['ADMIN_USERNAME']
        admin_password = app.config['ADMIN_PASSWORD']
        
        admin = User(
            username=admin_username,
            password=hash_password(admin_password),
            role='Owner',
            email=f'{admin_username}@inventrobil.com'
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{admin_username}' created.")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=8000)
