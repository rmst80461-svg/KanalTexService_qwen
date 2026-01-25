import sqlite3
from datetime import datetime, timedelta
import os


class Database:
    def __init__(self, db_path='requests.db'):
        """Инициализация соединения с базой данных"""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Создание таблицы заявок если её нет"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создание таблицы запросов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                address TEXT NOT NULL,
                service_type TEXT NOT NULL,
                phone TEXT NOT NULL,
                status TEXT DEFAULT 'Новая',
                comment TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_request(self, user_id, full_name, address, service_type, phone):
        """Создание новой заявки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO requests (user_id, full_name, address, service_type, phone)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, full_name, address, service_type, phone))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return request_id
    
    def get_user_last_request_within_24h(self, user_id):
        """Проверка, была ли заявка от пользователя за последние 24 часа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        cursor.execute('''
            SELECT * FROM requests 
            WHERE user_id = ? AND created_at > ?
        ''', (user_id, twenty_four_hours_ago.strftime('%Y-%m-%d %H:%M:%S')))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def get_all_requests(self):
        """Получение всех заявок"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, full_name, address, service_type, phone, 
                   status, comment, created_at 
            FROM requests 
            ORDER BY created_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_request_by_id(self, request_id):
        """Получение заявки по ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, full_name, address, service_type, phone, 
                   status, comment, created_at 
            FROM requests 
            WHERE id = ?
        ''', (request_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result
    
    def update_status(self, request_id, status):
        """Обновление статуса заявки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE requests 
            SET status = ? 
            WHERE id = ?
        ''', (status, request_id))
        
        conn.commit()
        conn.close()
    
    def update_comment(self, request_id, comment):
        """Обновление комментария к заявке"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE requests 
            SET comment = ? 
            WHERE id = ?
        ''', (comment, request_id))
        
        conn.commit()
        conn.close()
    
    def get_requests_count(self):
        """Получение количества заявок"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM requests')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count