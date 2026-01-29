#!/usr/bin/env python3
"""
Main entry point for KanalTexService Telegram Bot
Адаптировано из ShveinyiHUB для ассенизаторских услуг
Компания: КаналТехСервис, г. Ярцево
"""
import os
import sys
import time
import asyncio
import threading
import logging
from pathlib import Path
from dotenv import load_dotenv

# --- АВТОЗАПУСК ДЛЯ BOTHOST ---
def force_load_env():
    """Принудительная загрузка .env для работы на любом хостинге"""
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'),
        os.path.join(os.getcwd(), '.env'),
        '.env'
    ]
    for path in possible_paths:
        if os.path.exists(path):
            load_dotenv(path, override=True)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            k, v = line.split('=', 1)
                            key = k.strip()
                            value = v.strip().strip('"').strip("'")
                            os.environ[key] = value
            except:
                pass
            return True
    return False

# Принудительно загружаем переменные окружения
force_load_env()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Проверка токена
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error(
        "\n" + "="*60 + "\n"
        "🔴 CRITICAL ERROR: BOT_TOKEN not found!\n\n"
        "Please set BOT_TOKEN in .env file or environment variables.\n"
        "="*60
    )
    sys.exit(1)

# --- ИМПОРТ ВЕБ-АДМИНКИ (Flask) ---
try:
    from app.web.routes import create_app
    flask_app = None
except ImportError as e:
    logger.warning(f"⚠️ Web admin panel import failed: {e}")
    flask_app = None


def run_flask_app():
    """Запуск Flask в отдельном потоке"""
    global flask_app
    if os.getenv("SKIP_FLASK", "0") == "1":
        logger.info("⏭️ Flask отключен (SKIP_FLASK=1)")
        return
    
    try:
        from app.models.database import Database
        db = Database()
        
        # Здесь будет bot_instance, но пока None
        from app.web.routes import create_app
        flask_app = create_app(db, None)
        
        port = int(os.getenv("FLASK_PORT", "8080"))
        logger.info(f"🌐 Flask starting on port {port}...")
        flask_app.run(host="0.0.0.0", port=port, use_reloader=False, threaded=True)
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске Flask: {e}")


def main():
    """Главная функция запуска бота"""
    logger.info("="*60)
    logger.info("🚰 КаналТехСервис - Telegram Bot & Admin Panel")
    logger.info("🏙️ г. Ярцево, Смоленская область")
    logger.info("👨‍💻 Адаптировано из ShveinyiHUB")
    logger.info("="*60)
    
    # Задержка 5 секунд перед запуском
    logger.info("⏳ Ожидание 5 секунд перед запуском...")
    time.sleep(5)
    
    # Сброс webhook
    try:
        import requests
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true",
            timeout=10
        )
        logger.info("✅ Webhook сброшен")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось сбросить webhook: {e}")
    
    # Запуск Flask в отдельном потоке
    if not os.getenv("SKIP_FLASK") and not os.getenv("SKIP_BOT"):
        flask_thread = threading.Thread(target=run_flask_app, daemon=True)
        flask_thread.start()
        logger.info("✅ Flask запущен в фоновом режиме")
        time.sleep(3)  # Даём Flask время запуститься
    
    # Инициализация базы данных
    logger.info("\n[1/3] Инициализация базы данных...")
    from app.models.database import Database
    db = Database()
    db.init_db()  # Создание таблиц
    logger.info("✅ База данных инициализирована")
    
    # Загрузка цен из JSON
    try:
        from app.utils.prices import load_prices_from_json
        load_prices_from_json()
        logger.info("✅ Цены загружены")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось загрузить цены: {e}")
    
    # Инициализация Telegram бота
    logger.info("\n[2/3] Инициализация Telegram бота...")
    from app.bot.bot_handler import TelegramBot
    bot = TelegramBot(db)
    logger.info("✅ Telegram бот инициализирован")
    
    # Запуск бота
    logger.info("\n[3/3] Запуск бота...")
    logger.info("\n" + "="*60)
    logger.info("🚀 Бот запущен и готов к работе!")
    logger.info("📞 Контакты: +7 (XXX) XXX-XX-XX")  # TODO: Заполнить
    logger.info("(Нажмите Ctrl+C для остановки)")
    logger.info("="*60 + "\n")
    
    # Асинхронный запуск
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("\n" + "="*60)
        logger.info("⏹️ Бот остановлен пользователем")
        logger.info("="*60)
    except Exception as e:
        logger.error("\n" + "="*60)
        logger.error(f"💥 Критическая ошибка: {type(e).__name__}: {e}", exc_info=True)
        logger.error("="*60)
        sys.exit(1)


if __name__ == '__main__':
    main()
