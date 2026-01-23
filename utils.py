from functools import wraps
from flask import session, redirect, url_for, jsonify
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO

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

def generate_invoice_pdf(record, items):
    """Generate invoice PDF using ReportLab"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Header
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        alignment=1, # Center
        spaceAfter=20
    )
    elements.append(Paragraph("InventroBil Invoice", title_style))
    elements.append(Spacer(1, 12))

    # Invoice Details
    normal_style = styles['Normal']
    elements.append(Paragraph(f"<b>Invoice ID:</b> #{record.id}", normal_style))
    elements.append(Paragraph(f"<b>Date:</b> {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Paragraph(f"<b>Cashier:</b> {record.created_by}", normal_style))
    elements.append(Spacer(1, 20))

    # Table Data
    data = [['Item', 'Price', 'Qty', 'Total']]
    for item in items:
        # Check if item is dict (from frontend pass) or object (from DB)
        # items can be list of dicts or list of BillingItem objects
        if hasattr(item, 'product_name'):
            name = item.product_name
            price = item.price
            qty = f"{item.quantity} {item.unit}"
            total = item.price * item.quantity
        else:
            name = item.get('name', 'Unknown')
            price = item.get('price', 0)
            qty = f"{item.get('quantity', 0)} {item.get('unit', 'pc')}"
            total = price * item.get('quantity', 0)
            
        data.append([
            name,
            f"${price:.2f}",
            qty,
            f"${total:.2f}"
        ])

    # Table Style
    table = Table(data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'), # Left align items
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'), # Right align totals
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Totals
    # Using a smaller table for totals aligned to the right
    total_data = [
        ['Subtotal:', f"${record.subtotal:.2f}"],
        [f"Discount ({record.discount_percent}%):", f"-${record.discount_amount:.2f}"],
        [f"GST ({record.gst_rate}%):", f"${record.gst_amount:.2f}"],
        ['Total:', f"${record.total:.2f}"]
    ]
    
    t_totals = Table(total_data, colWidths=[5.5*inch, 1.5*inch])
    t_totals.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'), # Bold Total
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(t_totals)
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Thank you for your business!", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer
