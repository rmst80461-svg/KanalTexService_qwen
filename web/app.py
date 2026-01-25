from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from database.database import Database
import pandas as pd
import io
import csv
import os
from datetime import datetime


# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Инициализация базы данных
db = Database()

# Класс пользователя для Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа в админку"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Проверяем логин и пароль из .env файла
        env_username = os.getenv('ADMIN_USERNAME', 'admin')
        env_password_hash = os.getenv('ADMIN_PASSWORD_HASH')
        
        if env_password_hash is None:
            flash('Администратор не настроен. Обратитесь к системному администратору.')
            return render_template('login.html')
        
        if username == env_username and check_password_hash(env_password_hash, password):
            user = User(1)  # Для простоты один администратор с ID=1
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный логин или пароль')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Выход из админки"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    """Главная страница админки - дашборд с заявками"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    # Получаем все заявки
    all_requests = db.get_all_requests()
    total_requests = len(all_requests)
    requests = all_requests[offset:offset + per_page]
    
    # Расчет общего количества страниц
    total_pages = (total_requests + per_page - 1) // per_page
    
    return render_template('dashboard.html', requests=requests, page=page, total_pages=total_pages)

@app.route('/update_status/<int:request_id>', methods=['POST'])
@login_required
def update_status(request_id):
    """Обновление статуса заявки"""
    new_status = request.form['status']
    comment = request.form.get('comment', '')
    
    # Обновляем статус в базе данных
    db.update_status(request_id, new_status)
    
    # Если есть комментарий, обновляем его тоже
    if comment:
        db.update_comment(request_id, comment)
    
    # Получаем информацию о заявке для отправки уведомления пользователю
    request_info = db.get_request_by_id(request_id)
    if request_info:
        user_id, _, _, _, _, _, _, _, _ = request_info
        # Отправляем уведомление пользователю через бота
        try:
            from notifications import send_status_update_sync
            send_status_update_sync(user_id, request_id, new_status, comment)
        except Exception as e:
            print(f"Ошибка при отправке уведомления пользователю: {e}")
    
    flash('Статус заявки успешно обновлен!')
    return redirect(url_for('dashboard'))

@app.route('/export_csv')
@login_required
def export_csv():
    """Экспорт всех заявок в CSV файл"""
    # Получаем все заявки
    all_requests = db.get_all_requests()
    
    # Преобразуем в DataFrame
    df = pd.DataFrame(all_requests, columns=[
        'ID', 'User ID', 'Full Name', 'Address', 'Service Type', 
        'Phone', 'Status', 'Comment', 'Created At'
    ])
    
    # Сохраняем в буфер
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    # Создаем BytesIO объект для отправки
    mem = io.BytesIO()
    mem.write(buffer.getvalue().encode('utf-8'))
    mem.seek(0)
    
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'requests_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)