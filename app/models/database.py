"""Расширенная модель базы данных для Telegram бота швейной мастерской."""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных SQLite."""

    def __init__(self, db_path: str = "bot_database.db"):
        """Инициализация подключения к БД."""
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Получить соединение с БД."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Создание таблиц в базе данных."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Таблица пользователей (расширенная)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    email TEXT,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_blocked INTEGER DEFAULT 0,
                    total_orders INTEGER DEFAULT 0,
                    notes TEXT
                )
            """)

            # Таблица заказов (расширенная)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    service_type TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    price REAL,
                    status TEXT DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    deadline TIMESTAMP,
                    photo_path TEXT,
                    admin_notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Таблица отзывов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    order_id INTEGER,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_published INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (order_id) REFERENCES orders(order_id)
                )
            """)

            # Таблица FAQ
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS faq (
                    faq_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category TEXT,
                    order_num INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1
                )
            """)

            # Таблица прайс-листа
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_list (
                    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    base_price REAL NOT NULL,
                    description TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)

            # Таблица рассылок
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS broadcasts (
                    broadcast_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'draft'
                )
            """)

            conn.commit()
            logger.info("База данных инициализирована")

    # === USERS ===
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавить нового пользователя."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                """, (user_id, username, first_name, last_name))
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Ошибка при добавлении пользователя: {e}")
                return False

    def update_user_activity(self, user_id: int):
        """Обновить время последней активности пользователя."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?
            """, (user_id,))
            conn.commit()

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить информацию о пользователе."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Получить список всех пользователей с пагинацией."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users ORDER BY registration_date DESC LIMIT ? OFFSET ?
            """, (limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    def get_users_count(self) -> int:
        """Получить общее количество пользователей."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users")
            return cursor.fetchone()['count']

    # === ORDERS ===
    def create_order(self, user_id: int, service_type: str, category: str = None, 
                    description: str = None, price: float = None, photo_path: str = None) -> int:
        """Создать новый заказ."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (user_id, service_type, category, description, price, photo_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, service_type, category, description, price, photo_path))
            
            # Увеличить счетчик заказов пользователя
            cursor.execute("""
                UPDATE users SET total_orders = total_orders + 1 WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
            return cursor.lastrowid

    def update_order_status(self, order_id: int, status: str, admin_notes: str = None):
        """Обновить статус заказа."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            update_query = "UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP"
            params = [status]
            
            if status == 'completed':
                update_query += ", completed_at = CURRENT_TIMESTAMP"
            
            if admin_notes:
                update_query += ", admin_notes = ?"
                params.append(admin_notes)
            
            update_query += " WHERE order_id = ?"
            params.append(order_id)
            
            cursor.execute(update_query, params)
            conn.commit()

    def get_order(self, order_id: int) -> Optional[Dict]:
        """Получить информацию о заказе."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_orders(self, user_id: int) -> List[Dict]:
        """Получить все заказы пользователя."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_orders_by_status(self, status: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Получить заказы по статусу с пагинацией."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.*, u.username, u.first_name, u.phone 
                FROM orders o
                JOIN users u ON o.user_id = u.user_id
                WHERE o.status = ?
                ORDER BY o.created_at DESC
                LIMIT ? OFFSET ?
            """, (status, limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    def get_pending_orders(self, hours: int = 48) -> List[Dict]:
        """Получить зависшие заказы (старше N часов в статусе 'in_progress')."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM orders 
                WHERE status = 'in_progress' 
                AND datetime(updated_at) < datetime('now', '-' || ? || ' hours')
                ORDER BY updated_at ASC
            """, (hours,))
            return [dict(row) for row in cursor.fetchall()]

    # === REVIEWS ===
    def add_review(self, user_id: int, rating: int, comment: str = None, order_id: int = None) -> int:
        """Добавить отзыв."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reviews (user_id, order_id, rating, comment)
                VALUES (?, ?, ?, ?)
            """, (user_id, order_id, rating, comment))
            conn.commit()
            return cursor.lastrowid

    def get_reviews(self, published_only: bool = True, limit: int = 10) -> List[Dict]:
        """Получить отзывы."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT r.*, u.first_name, u.username
                FROM reviews r
                JOIN users u ON r.user_id = u.user_id
            """
            if published_only:
                query += " WHERE r.is_published = 1"
            query += " ORDER BY r.created_at DESC LIMIT ?"
            
            cursor.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # === FAQ ===
    def get_faq_items(self, category: str = None) -> List[Dict]:
        """Получить FAQ записи."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("""
                    SELECT * FROM faq WHERE category = ? AND is_active = 1 ORDER BY order_num
                """, (category,))
            else:
                cursor.execute("""
                    SELECT * FROM faq WHERE is_active = 1 ORDER BY category, order_num
                """)
            return [dict(row) for row in cursor.fetchall()]

    # === PRICE LIST ===
    def get_prices_by_category(self, category: str) -> List[Dict]:
        """Получить цены по категории."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM price_list WHERE category = ? AND is_active = 1
            """, (category,))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_categories(self) -> List[str]:
        """Получить список всех категорий услуг."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT category FROM price_list WHERE is_active = 1 ORDER BY category
            """)
            return [row['category'] for row in cursor.fetchall()]

    # === STATISTICS ===
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику бота."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Всего пользователей
            cursor.execute("SELECT COUNT(*) as count FROM users")
            stats['total_users'] = cursor.fetchone()['count']
            
            # Новых за 7 дней
            cursor.execute("""
                SELECT COUNT(*) as count FROM users 
                WHERE datetime(registration_date) > datetime('now', '-7 days')
            """)
            stats['new_users_week'] = cursor.fetchone()['count']
            
            # Всего заказов
            cursor.execute("SELECT COUNT(*) as count FROM orders")
            stats['total_orders'] = cursor.fetchone()['count']
            
            # Заказы по статусам
            cursor.execute("""
                SELECT status, COUNT(*) as count FROM orders GROUP BY status
            """)
            stats['orders_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Средний рейтинг
            cursor.execute("SELECT AVG(rating) as avg_rating FROM reviews")
            avg_rating = cursor.fetchone()['avg_rating']
            stats['avg_rating'] = round(avg_rating, 2) if avg_rating else 0
            
            # Всего отзывов
            cursor.execute("SELECT COUNT(*) as count FROM reviews")
            stats['total_reviews'] = cursor.fetchone()['count']
            
            return stats

    # === BROADCASTS ===
    def create_broadcast(self, message: str) -> int:
        """Создать рассылку."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO broadcasts (message) VALUES (?)
            """, (message,))
            conn.commit()
            return cursor.lastrowid

    def update_broadcast_stats(self, broadcast_id: int, sent: int = 0, failed: int = 0):
        """Обновить статистику рассылки."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE broadcasts 
                SET sent_count = sent_count + ?, failed_count = failed_count + ?, status = 'sent'
                WHERE broadcast_id = ?
            """, (sent, failed, broadcast_id))
            conn.commit()
