"""
Database model for the application
"""
import sqlite3
import logging
from datetime import datetime
from typing import List, Tuple, Optional


class Database:
    def __init__(self, db_path: str = "requests.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database and create tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    full_name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    status TEXT DEFAULT 'Новая',
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    def create_request(self, user_id: int, full_name: str, address: str, service_type: str, phone: str) -> int:
        """Create a new request"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO requests (user_id, full_name, address, service_type, phone) VALUES (?, ?, ?, ?, ?)",
                (user_id, full_name, address, service_type, phone)
            )
            
            request_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logging.info(f"New request created with ID: {request_id}")
            return request_id
        except Exception as e:
            logging.error(f"Error creating request: {e}")
            raise

    def get_user_last_request_within_24h(self, user_id: int) -> bool:
        """Check if user has submitted a request within the last 24 hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate time threshold (24 hours ago)
            time_threshold = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "SELECT COUNT(*) FROM requests WHERE user_id = ? AND created_at >= datetime(?, '-1 day')",
                (user_id, time_threshold)
            )
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
        except Exception as e:
            logging.error(f"Error checking user's recent requests: {e}")
            raise

    def get_all_requests(self) -> List[Tuple]:
        """Get all requests"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, user_id, full_name, address, service_type, phone, status, comment, created_at FROM requests ORDER BY created_at DESC"
            )
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            logging.error(f"Error getting all requests: {e}")
            raise

    def get_request_by_id(self, request_id: int) -> Optional[Tuple]:
        """Get request by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, user_id, full_name, address, service_type, phone, status, comment, created_at FROM requests WHERE id = ?",
                (request_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result
        except Exception as e:
            logging.error(f"Error getting request by ID: {e}")
            raise

    def update_status(self, request_id: int, new_status: str):
        """Update request status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE requests SET status = ? WHERE id = ?",
                (new_status, request_id)
            )
            
            conn.commit()
            conn.close()
            logging.info(f"Status updated for request ID: {request_id}, new status: {new_status}")
        except Exception as e:
            logging.error(f"Error updating status: {e}")
            raise

    def update_comment(self, request_id: int, comment: str):
        """Update request comment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE requests SET comment = ? WHERE id = ?",
                (comment, request_id)
            )
            
            conn.commit()
            conn.close()
            logging.info(f"Comment updated for request ID: {request_id}")
        except Exception as e:
            logging.error(f"Error updating comment: {e}")
            raise