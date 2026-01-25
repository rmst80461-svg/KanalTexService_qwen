import asyncio
import logging
import sqlite3
import os
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ParseMode
import pandas as pd
import io
import re
from dotenv import load_dotenv


# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Получение токена бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не установлен BOT_TOKEN в .env файле")

# Конфигурация Flask
FLASK_SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')

if ADMIN_PASSWORD_HASH is None:
    raise ValueError("Не установлен ADMIN_PASSWORD_HASH в .env файле")


# FSM состояния
class RequestForm(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_address = State()
    waiting_for_service = State()
    waiting_for_phone = State()


# Класс для работы с базой данных
class Database:
    def __init__(self, db_path="requests.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создание таблицы заявок
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

    def create_request(self, user_id, full_name, address, service_type, phone):
        """Создание новой заявки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO requests (user_id, full_name, address, service_type, phone) VALUES (?, ?, ?, ?, ?)",
            (user_id, full_name, address, service_type, phone)
        )
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return request_id

    def get_user_last_request_within_24h(self, user_id):
        """Проверка, была ли заявка от пользователя за последние 24 часа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Вычисляем время 24 часа назад
        time_threshold = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "SELECT COUNT(*) FROM requests WHERE user_id = ? AND created_at >= datetime(?, '-1 day')",
            (user_id, time_threshold)
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0

    def get_all_requests(self):
        """Получение всех заявок"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, user_id, full_name, address, service_type, phone, status, comment, created_at FROM requests ORDER BY created_at DESC"
        )
        
        results = cursor.fetchall()
        conn.close()
        
        return results

    def get_request_by_id(self, request_id):
        """Получение заявки по ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, user_id, full_name, address, service_type, phone, status, comment, created_at FROM requests WHERE id = ?",
            (request_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result

    def update_status(self, request_id, new_status):
        """Обновление статуса заявки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE requests SET status = ? WHERE id = ?",
            (new_status, request_id)
        )
        
        conn.commit()
        conn.close()

    def update_comment(self, request_id, comment):
        """Обновление комментария к заявке"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE requests SET comment = ? WHERE id = ?",
            (comment, request_id)
        )
        
        conn.commit()
        conn.close()


# Класс Telegram-бота
class TelegramBot:
    def __init__(self, db):
        self.bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self.db = db
        
        # Регистрация хендлеров
        self.register_handlers()
    
    def register_handlers(self):
        """Регистрация хендлеров"""
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message(Command("help"))(self.cmd_help)
        self.dp.message(Command("status"))(self.cmd_status)
        self.dp.message(F.text == "Новая заявка")(self.process_new_request_command)
        
        # FSM handlers
        self.dp.message(RequestForm.waiting_for_full_name)(self.process_full_name)
        self.dp.message(RequestForm.waiting_for_address)(self.process_address)
        self.dp.message(RequestForm.waiting_for_service)(self.process_service)
        self.dp.message(RequestForm.waiting_for_phone)(self.process_phone)
    
    async def cmd_start(self, message: Message, state: FSMContext):
        """Обработка команды /start"""
        await state.clear()
        welcome_text = (
            f"Добро пожаловать в систему подачи заявок <b>КаналТехСервис</b>, г. Ярцево!\n\n"
            f"С помощью этого бота вы можете подать заявку на ассенизаторские услуги.\n\n"
            f"Для начала работы нажмите кнопку <b>Новая заявка</b> или введите /help для справки."
        )
        
        # Клавиатура с кнопкой "Новая заявка"
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Новая заявка")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(welcome_text, reply_markup=keyboard)
    
    async def cmd_help(self, message: Message, state: FSMContext):
        """Обработка команды /help"""
        await state.clear()
        help_text = (
            "<b>КаналТехСервис, г. Ярцево</b>\n\n"
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/status - Проверить статус вашей последней заявки\n\n"
            "Чтобы подать новую заявку, нажмите кнопку <b>Новая заявка</b>"
        )
        await message.answer(help_text)
    
    async def cmd_status(self, message: Message):
        """Обработка команды /status"""
        user_id = message.from_user.id
        
        # Получаем последнюю заявку пользователя
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, status, comment, created_at FROM requests WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            request_id, status, comment, created_at = result
            status_text = f"Ваша последняя заявка №{request_id}:\n"
            status_text += f"<b>Статус:</b> {status}\n"
            status_text += f"<b>Дата создания:</b> {created_at}\n"
            
            if comment:
                status_text += f"<b>Комментарий:</b> {comment}"
            
            await message.answer(status_text)
        else:
            await message.answer("У вас пока нет заявок в системе.")
    
    async def process_new_request_command(self, message: Message, state: FSMContext):
        """Начало процесса подачи новой заявки"""
        user_id = message.from_user.id
        
        # Проверяем, не было ли заявки от пользователя за последние 24 часа
        if self.db.get_user_last_request_within_24h(user_id):
            await message.answer(
                "Вы уже подавали заявку за последние 24 часа. "
                "Подождите до истечения этого периода перед подачей новой заявки."
            )
            return
        
        await state.set_state(RequestForm.waiting_for_full_name)
        await message.answer(
            "Введите ваше полное имя (ФИО):"
        )
    
    async def process_full_name(self, message: Message, state: FSMContext):
        """Обработка введенного ФИО"""
        full_name = message.text.strip()
        
        if len(full_name.split()) < 2:
            await message.answer("Пожалуйста, введите полное имя (ФИО):")
            return
        
        await state.update_data(full_name=full_name)
        await state.set_state(RequestForm.waiting_for_address)
        
        # Клавиатура с вариантами адресов
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Ярцево"),
                    KeyboardButton(text="Дачный посёлок")
                ],
                [
                    KeyboardButton(text="п. Солнечный"),
                    KeyboardButton(text="Другое")
                ]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            "Выберите адрес выполнения работ:",
            reply_markup=keyboard
        )
    
    async def process_address(self, message: Message, state: FSMContext):
        """Обработка выбранного адреса"""
        address = message.text.strip()
        
        # Валидация адреса
        valid_addresses = ["Ярцево", "Дачный посёлок", "п. Солнечный", "Другое"]
        if address not in valid_addresses:
            await message.answer(
                "Пожалуйста, выберите адрес из предложенных вариантов:"
            )
            return
        
        await state.update_data(address=address)
        await state.set_state(RequestForm.waiting_for_service)
        
        # Клавиатура с вариантами услуг
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Ассенизаторские услуги"),
                    KeyboardButton(text="Вызов сантехника")
                ],
                [
                    KeyboardButton(text="Прочистка труб"),
                    KeyboardButton(text="Установка сантехники")
                ]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            "Выберите тип услуги:",
            reply_markup=keyboard
        )
    
    async def process_service(self, message: Message, state: FSMContext):
        """Обработка выбранного типа услуги"""
        service_type = message.text.strip()
        
        # Валидация типа услуги
        valid_services = ["Ассенизаторские услуги", "Вызов сантехника", "Прочистка труб", "Установка сантехники"]
        if service_type not in valid_services:
            await message.answer(
                "Пожалуйста, выберите тип услуги из предложенных вариантов:"
            )
            return
        
        await state.update_data(service_type=service_type)
        await state.set_state(RequestForm.waiting_for_phone)
        
        # Убираем клавиатуру после выбора услуги
        from aiogram.types import ReplyKeyboardRemove
        await message.answer(
            "Введите ваш номер телефона в формате +7XXXXXXXXXX:",
            reply_markup=ReplyKeyboardRemove()
        )
    
    async def process_phone(self, message: Message, state: FSMContext):
        """Обработка введенного номера телефона"""
        phone = message.text.strip()
        
        # Проверяем формат номера телефона
        phone_pattern = r'^\+7\d{10}$'
        if not re.match(phone_pattern, phone):
            await message.answer(
                "Неверный формат номера телефона. Введите номер в формате +7XXXXXXXXXX:"
            )
            return
        
        # Получаем данные из состояния
        data = await state.get_data()
        user_id = message.from_user.id
        full_name = data['full_name']
        address = data['address']
        service_type = data['service_type']
        
        # Создаем заявку в базе данных
        request_id = self.db.create_request(user_id, full_name, address, service_type, phone)
        
        # Очищаем состояние
        await state.clear()
        
        # Отправляем подтверждение
        success_message = (
            f"Спасибо, <b>{full_name}</b>! Ваша заявка №{request_id} принята.\n\n"
            f"Адрес: {address}\n"
            f"Услуга: {service_type}\n"
            f"Телефон: {phone}\n\n"
            f"С вами свяжется наш специалист для уточнения деталей.\n\n"
            f"Компания <b>КаналТехСервис</b>, г. Ярцево"
        )
        
        await message.answer(success_message)
    
    async def send_status_update(self, user_id, request_id, new_status, comment=None):
        """Отправка обновления статуса пользователю"""
        try:
            status_message = f"Статус вашей заявки №{request_id} обновлен: <b>{new_status}</b>"
            if comment:
                status_message += f"\nКомментарий: {comment}"
            
            await self.bot.send_message(user_id, status_message)
        except Exception as e:
            logging.error(f"Ошибка при отправке обновления статуса пользователю {user_id}: {e}")
    
    async def run(self):
        """Запуск бота"""
        await self.dp.start_polling(self.bot)


# Создание Flask-приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Инициализация базы данных
db = Database()

# Глобальная переменная для бота
telegram_bot = None

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
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
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
    if request_info and telegram_bot:
        user_id, _, _, _, _, _, _, _, _ = request_info
        # Отправляем уведомление пользователю через бота
        try:
            asyncio.run(telegram_bot.send_status_update(user_id, request_id, new_status, comment))
        except Exception as e:
            logging.error(f"Ошибка при отправке уведомления пользователю: {e}")
    
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


async def run_bot():
    """Функция для запуска бота"""
    global telegram_bot
    telegram_bot = TelegramBot(db)
    await telegram_bot.run()


def run_flask():
    """Функция для запуска Flask-приложения"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем бота
    asyncio.run(run_bot())