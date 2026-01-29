"""Flask routes for admin panel"""
from flask import Flask, render_template, jsonify, make_response
from typing import Optional, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from app.models.database import Database

def create_app(db: 'Database', bot=None) -> Flask:
    """Create Flask application"""
    app = Flask(__name__, template_folder='../../templates')
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    
    @app.after_request
    def add_header(response):
        """Add headers to prevent caching"""
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    @app.route('/')
    def index():
        """Main page"""
        return jsonify({"status": "online", "message": "КаналТехСервис Bot Admin Panel"})
    
    @app.route('/health')
    def health():
        """Health check"""
        return jsonify({"status": "healthy"})
    
    return app
