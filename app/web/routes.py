"""Flask routes for admin panel"""
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
from typing import Optional, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from app.models.database import Database

def create_app(db: 'Database', bot=None) -> Flask:
    """Create Flask application"""
    app = Flask(__name__, template_folder='../../templates')
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('admin_logged_in'):
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def api_auth_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('admin_logged_in'):
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return decorated_function
    
    @app.after_request
    def add_header(response):
        """Add headers to prevent caching"""
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        error = None
        if request.method == 'POST':
            password = request.form.get('password', '')
            if password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                return redirect(url_for('index'))
            else:
                error = 'Неверный пароль'
        return render_template('login.html', error=error)
    
    @app.route('/logout')
    def logout():
        """Logout"""
        session.pop('admin_logged_in', None)
        return redirect(url_for('login'))
    
    @app.route('/')
    @login_required
    def index():
        """Admin panel main page"""
        return render_template('admin.html')
    
    @app.route('/health')
    def health():
        """Health check"""
        return jsonify({"status": "healthy"})
    
    @app.route('/api/orders')
    @api_auth_required
    def get_orders():
        """Get all orders with stats"""
        if db is None:
            return jsonify({"orders": [], "stats": {}})
        
        orders = db.get_all_orders()
        stats = db.get_stats()
        stats['users'] = db.get_users_count()
        
        return jsonify({
            "orders": orders,
            "stats": stats
        })
    
    @app.route('/api/orders/<int:order_id>/status', methods=['POST'])
    @api_auth_required
    def update_order_status(order_id):
        """Update order status"""
        if db is None:
            return jsonify({"error": "Database not available"}), 500
        
        order = db.get_order_by_id(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['new', 'in_progress', 'completed', 'cancelled']:
            return jsonify({"error": "Invalid status"}), 400
        
        db.update_order_status(order_id, new_status)
        return jsonify({"success": True})
    
    @app.route('/api/orders/<int:order_id>', methods=['DELETE'])
    @api_auth_required
    def delete_order(order_id):
        """Delete order"""
        if db is None:
            return jsonify({"error": "Database not available"}), 500
        
        order = db.get_order_by_id(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        db.delete_order(order_id)
        return jsonify({"success": True})
    
    return app
