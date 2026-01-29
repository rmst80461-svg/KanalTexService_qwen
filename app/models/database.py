"""Database models and operations for KanalTexService Bot"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database handler for KanalTexService Bot"""
    
    def __init__(self, db_path: str = "botdata.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                service_type TEXT,
                address TEXT,
                phone TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rating INTEGER,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Add or update user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
    
    def get_user_orders(self, user_id: int) -> List[Dict]:
        """Get user's orders"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return orders
    
    def create_order(self, user_id: int, service_type: str, address: str, phone: str) -> int:
        """Create new order"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (user_id, service_type, address, phone, status)
            VALUES (?, ?, ?, ?, 'new')
        ''', (user_id, service_type, address, phone))
        
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()
        return order_id
    
    def update_order_status(self, order_id: int, status: str):
        """Update order status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE order_id = ?
        ''', (status, order_id))
        
        conn.commit()
        conn.close()
