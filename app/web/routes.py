"""Flask routes for admin panel"""
from flask import Flask, render_template, jsonify
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.database import Database

def create_app(db: 'Database', bot=None) -> Flask:
    """Create Flask application"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-key'
    
    @app.route('/')
    def index():
        """Main page"""
        return jsonify({"status": "online", "message": "КаналТехСервис Bot Admin Panel"})
    
    @app.route('/health')
    def health():
        """Health check"""
        return jsonify({"status": "healthy"})
    
    return app
