"""
Main entry point for the application
"""
import asyncio
import logging
import threading
import os
import sys

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_flask_app(app, port):
    """Запуск Flask приложения"""
    try:
        logger.info(f"🚀 Запуск Flask сервера на порту {port}")
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"❌ Ошибка запуска Flask: {e}")

async def main():
    """Основная асинхронная функция запуска"""
    try:
        # 1. Инициализация базы данных
        logger.info("🔄 Инициализация базы данных...")
        from app.models.database import Database
        db = Database()
        logger.info("✅ База данных инициализирована")
        
        # 2. Инициализация Telegram бота
        logger.info("🔄 Инициализация Telegram бота...")
        from app.bot.bot_handler import TelegramBot
        from app.config import BOT_TOKEN, ADMIN_IDS
        
        if not BOT_TOKEN:
            logger.error("❌ Токен бота не найден. Проверьте файл .env")
            return
        
        telegram_bot = TelegramBot(db)
        logger.info(f"✅ Бот инициализирован. Администраторы: {ADMIN_IDS}")
        
        # 3. Создание и запуск Flask приложения в отдельном потоке
        logger.info("🔄 Создание Flask приложения...")
        from app.web.routes import create_app
        app = create_app(db, telegram_bot)
        
        # Запуск Flask в отдельном потоке
        port = int(os.environ.get('PORT', 5000))
        flask_thread = threading.Thread(
            target=run_flask_app,
            args=(app, port),
            daemon=True
        )
        flask_thread.start()
        logger.info(f"✅ Flask сервер запущен на http://localhost:{port}")
        
        # 4. Запуск Telegram бота
        logger.info("🤖 Запуск Telegram бота...")
        logger.info("=" * 50)
        logger.info("💧 КаналТехСервис - Telegram Bot")
        logger.info(f"📞 Телефон: +7 (904) 363-36-36")
        logger.info("📍 Ярцево, Смоленская область")
        logger.info("⏰ Режим работы: 24/7")
        logger.info("=" * 50)
        
        await telegram_bot.run()
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        logger.info("Проверьте структуру проекта и наличие всех файлов")
    except KeyboardInterrupt:
        logger.info("👋 Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)

def check_dependencies():
    """Проверка зависимостей и структуры проекта"""
    required_dirs = [
        'app',
        'app/models',
        'app/web',
        'app/bot',
        'app/config',
        'templates'
    ]
    
    required_files = [
        'app/models/database.py',
        'app/web/routes.py',
        'app/bot/bot_handler.py',
        'app/config/__init__.py',
        '.env'
    ]
    
    logger.info("🔍 Проверка структуры проекта...")
    
    # Проверка директорий
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            logger.info(f"   ✅ {dir_path}/")
        else:
            logger.warning(f"   ⚠️  {dir_path}/ - не найдено")
    
    # Проверка файлов
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"   ✅ {file_path}")
        else:
            if file_path == '.env':
                logger.error(f"   ❌ {file_path} - критический файл не найден!")
                logger.info("Создайте .env файл на основе .env.example")
            else:
                logger.warning(f"   ⚠️  {file_path} - не найден")
    
    # Проверка переменных окружения
    logger.info("🔍 Проверка переменных окружения...")
    from dotenv import load_dotenv
    load_dotenv()
    
    required_env_vars = ['BOT_TOKEN', 'ADMIN_IDS', 'FLASK_SECRET_KEY']
    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"   ✅ {var} = {'***' if var == 'BOT_TOKEN' else value[:20]}")
        else:
            logger.error(f"   ❌ {var} - не установлена")

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Запуск КаналТехСервис")
    print("=" * 50)
    
    # Проверка зависимостей
    check_dependencies()
    
    # Запуск основного приложения
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Приложение остановлено")
    except Exception as e:
        logger.error(f"❌ Фатальная ошибка: {e}")
        logger.info("Пожалуйста, проверьте логи и настройки")
        input("Нажмите Enter для выхода...")
