"""
Main entry point for the application
"""
import asyncio
import logging
import threading
import os
from flask import Flask

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from app.models.database import Database
from app.bot.bot_handler import TelegramBot
from app.web.routes import setup_routes
from app.config import FLASK_SECRET_KEY, BOT_TOKEN

def create_app(db, telegram_bot):
    """Создание и настройка Flask приложения"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    
    # Настройка роутов (передаем зависимости)
    setup_routes(app, db, telegram_bot)
    
    return app

async def run_bot(bot_instance):
    """Запуск Telegram бота с очисткой старых вебхуков"""
    if not BOT_TOKEN:
        logging.error("БОТ НЕ ЗАПУЩЕН: Токен (BOT_TOKEN) отсутствует в .env")
        return

    try:
        # Проверяем наличие объекта bot внутри TelegramBot
        if hasattr(bot_instance, 'bot'):
            logging.info("Удаление старых вебхуков (очистка конфликтов)...")
            await bot_instance.bot.delete_webhook(drop_pending_updates=True)
            logging.info("Вебхуки успешно очищены.")
        
        logging.info("Запуск polling (прием сообщений)...")
        await bot_instance.run()
    except Exception as e:
        logging.error(f"Ошибка при работе бота: {e}")

if __name__ == '__main__':
    # 1. Инициализация общих компонентов
    db = Database()
    telegram_bot = TelegramBot(db)
    
    # 2. Создание Flask приложения
    app = create_app(db, telegram_bot)
    
    # 3. Запуск Flask в отдельном потоке
    # use_reloader=False критически важен для работы с потоками!
    port = int(os.environ.get('PORT', 5000))
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    )
    flask_thread.daemon = True
    flask_thread.start()
    logging.info(f"Flask-сервер запущен на порту {port}")
    
    # 4. Запуск основного цикла бота (asyncio)
    try:
        asyncio.run(run_bot(telegram_bot))
    except (KeyboardInterrupt, SystemExit):
        logging.info("Приложение остановлено")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
