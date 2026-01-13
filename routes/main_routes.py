from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from extensions import db
from models import Product, BillingRecord, User
from utils import login_required, get_user_permissions, owner_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Redirect to login or home based on session"""
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.home'))

@main_bp.route('/home')
@login_required
def home():
    """Render home page with dashboard stats"""
    permissions = get_user_permissions(session['user']['role'])
    
    # Calculate stats
    products = Product.query.all()
    billing_history = BillingRecord.query.all()
    
    total_products = len(products)
    low_stock_count = sum(1 for p in products if p.stock < 10)
    total_transactions = len(billing_history)
    total_revenue = sum(record.total for record in billing_history)
    
    return render_template('home.html',
        user=session['user'],
        permissions=permissions,
        total_products=total_products,
        low_stock_count=low_stock_count,
        total_transactions=total_transactions,
        total_revenue=total_revenue
    )

@main_bp.route('/settings')
@owner_required
def settings():
    """Render settings page (Owner only)"""
    permissions = get_user_permissions(session['user']['role'])
    users = User.query.all()
    
    return render_template('settings.html',
        user=session['user'],
        permissions=permissions,
        users=[u.to_dict() for u in users]
    )
