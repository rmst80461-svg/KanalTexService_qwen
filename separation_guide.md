# Руководство по разделению приложения для развертывания на bothost.ru

## Проблема
Приложение "КаналТехСервис" одновременно запускает Telegram-бота и Flask-веб-сервер в одном процессе. На shared-хостинге bothost.ru такой подход не будет работать, так как постоянные процессы (для polling бота) блокируются.

## Решение
Разделить приложение на две части:
1. **Веб-админка** - развертывается на bothost.ru
2. **Telegram-бот** - развертывается на отдельном хостинге

## Шаг 1: Создание отдельного файла для веб-админки

Создайте новый файл `web_app.py`:

```python
"""
Веб-админка для bothost.ru (без запуска Telegram-бота)
"""
import os
from flask import Flask
from app.models.database import Database
from app.web.routes import setup_routes_without_bot

def create_web_app():
    """Create and configure the Flask application for web admin panel only"""
    app = Flask(__name__)
    
    # Load secret key from environment
    from app.config import FLASK_SECRET_KEY
    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    
    # Initialize database
    db = Database()
    
    # Setup routes without bot instance (will be handled differently)
    setup_routes_without_bot(app, db)
    
    return app

if __name__ == '__main__':
    app = create_web_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

## Шаг 2: Модификация маршрутов для веб-админки

Создайте файл `app/web/web_routes_only.py`:

```python
"""
Web routes for admin panel (without bot integration for hosting compatibility)
"""
import io
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.database import Database

from app.web.services import User, load_user as user_loader_func
from app.config import ADMIN_USERNAME, ADMIN_PASSWORD_HASH


def setup_routes_without_bot(app: Flask, db: 'Database'):
    """Setup all routes for the Flask app without bot integration"""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id: str) -> User:
        return user_loader_func(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page for admin panel"""
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
                user = User(1)  # For simplicity, single admin with ID=1
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Неверный логин или пароль')
        
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        """Logout from admin panel"""
        logout_user()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def dashboard():
        """Admin dashboard showing requests"""
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page
        
        # Get all requests
        all_requests = db.get_all_requests()
        total_requests = len(all_requests)
        requests = all_requests[offset:offset + per_page]
        
        # Calculate total pages
        total_pages = (total_requests + per_page - 1) // per_page
        
        return render_template('dashboard.html', requests=requests, page=page, total_pages=total_pages)

    @app.route('/update_status/<int:request_id>', methods=['POST'])
    @login_required
    def update_status(request_id: int):
        """Update request status"""
        new_status = request.form['status']
        comment = request.form.get('comment', '')
        
        # Update status in database
        db.update_status(request_id, new_status)
        
        # If there's a comment, update it too
        if comment:
            db.update_comment(request_id, comment)
        
        # Note: Without bot instance, we cannot send notifications
        # These would need to be handled separately or through API calls
        
        flash('Статус заявки успешно обновлен!')
        return redirect(url_for('dashboard'))

    @app.route('/export_csv')
    @login_required
    def export_csv():
        """Export all requests to CSV file"""
        # Get all requests
        all_requests = db.get_all_requests()
        
        # Define column headers
        headers = [
            'ID', 'User ID', 'Full Name', 'Address', 'Service Type', 
            'Phone', 'Status', 'Comment', 'Created At'
        ]
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(headers)
        
        # Write data rows
        for row in all_requests:
            writer.writerow(row)
        
        # Get the CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Create BytesIO object for sending
        mem = io.BytesIO()
        mem.write(csv_content.encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'requests_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
```

## Шаг 3: Создание отдельного файла для бота

Создайте файл `bot_app.py`:

```python
"""
Telegram-бот (для развертывания на отдельном хостинге)
"""
import asyncio
import logging
from app.models.database import Database
from app.bot.bot_handler import TelegramBot

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run_bot():
    """Function to run Telegram bot only"""
    db = Database()
    telegram_bot = TelegramBot(db)
    
    try:
        await telegram_bot.run()
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Error running bot: {e}")

if __name__ == '__main__':
    asyncio.run(run_bot())
```

## Шаг 4: Альтернативное решение - использование webhook

Для интеграции с bothost.ru рекомендуется использовать webhook вместо polling. Ниже пример модификации:

### Модифицированный `web_app_with_webhook.py`:

```python
"""
Веб-админка с поддержкой Telegram webhook
"""
import os
import json
from flask import Flask, request
from app.models.database import Database
from app.bot.bot_handler import TelegramBot  # Предполагаем, что бот может работать в режиме webhook

def create_web_app_with_webhook():
    app = Flask(__name__)
    
    # Load secret key from environment
    from app.config import FLASK_SECRET_KEY
    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    
    # Initialize database
    db = Database()
    
    # Initialize bot in webhook mode
    telegram_bot = TelegramBot(db)
    
    # Setup routes
    from app.web.webhook_routes import setup_webhook_routes
    setup_webhook_routes(app, db, telegram_bot)
    
    return app

if __name__ == '__main__':
    app = create_web_app_with_webhook()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Маршруты для webhook в `app/web/webhook_routes.py`:

```python
"""
Routes for webhook handling
"""
from flask import Flask, request, jsonify
from flask_login import login_required
from app.web.routes import setup_routes_without_bot

def setup_webhook_routes(app: Flask, db, telegram_bot):
    """Setup routes including webhook endpoint"""
    
    # Setup regular admin routes
    setup_routes_without_bot(app, db)
    
    # Telegram webhook endpoint
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Handle incoming webhook from Telegram"""
        try:
            update_data = request.get_json()
            
            # Process the update using the bot instance
            # This requires modification of the bot to handle webhook updates
            # instead of using polling
            
            # For now, return OK
            return jsonify({'status': 'OK'})
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return jsonify({'error': str(e)}), 500
```

## Шаг 5: Обновленный Procfile для bothost.ru

```
web: python web_app.py
```

## Шаг 6: Рекомендации по деплою

### Для веб-админки на bothost.ru:
1. Загрузите файлы: `web_app.py`, `requirements.txt`, `templates/`, `app/`, `Procfile`
2. Установите переменные окружения в панели bothost.ru
3. Укажите точку входа: `web_app.py`

### Для Telegram-бота:
1. Разверните на VPS, Heroku или любом хостинге с поддержкой постоянных процессов
2. Используйте тот же файл базы данных или настройте общую базу (MySQL)

### Альтернатива: общая база данных
Если используется общая база данных (MySQL), обновите `app/models/database.py`:

```python
import os
import sqlite3
import logging
from datetime import datetime
from typing import List, Tuple, Optional

# Add support for MySQL
try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

class Database:
    def __init__(self, db_path: str = "requests.db"):
        # Check if MySQL is configured
        self.use_mysql = os.getenv('USE_MYSQL', '').lower() == 'true' and MYSQL_AVAILABLE
        
        if self.use_mysql:
            self.connection_params = {
                'host': os.getenv('MYSQL_HOST', 'localhost'),
                'user': os.getenv('MYSQL_USER', 'root'),
                'password': os.getenv('MYSQL_PASSWORD', ''),
                'database': os.getenv('MYSQL_DATABASE', 'kanaltex'),
                'charset': 'utf8mb4'
            }
        else:
            self.db_path = db_path
        
        self.init_db()

    def get_connection(self):
        if self.use_mysql:
            return pymysql.connect(**self.connection_params)
        else:
            return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize database and create tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.use_mysql:
                # MySQL table creation
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS requests (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        full_name VARCHAR(255) NOT NULL,
                        address VARCHAR(255) NOT NULL,
                        service_type VARCHAR(255) NOT NULL,
                        phone VARCHAR(20) NOT NULL,
                        status VARCHAR(50) DEFAULT 'Новая',
                        comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                ''')
            else:
                # SQLite table creation (original)
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
    # ... остальные методы класса обновляются аналогично
```

## Заключение

Разделение приложения на веб-админку и Telegram-бота позволяет:
1. Развернуть веб-админку на bothost.ru
2. Развернуть бота на хостинге с поддержкой постоянных процессов
3. При необходимости использовать общую базу данных для синхронизации данных