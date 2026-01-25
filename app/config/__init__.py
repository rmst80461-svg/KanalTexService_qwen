"""
Configuration module for the application
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask configuration
FLASK_SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')

# Устанавливаем значение по умолчанию 'default_hash', чтобы не вылетала ошибка
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', 'default_hash')

# Bot configuration
# Устанавливаем значение по умолчанию 'your_bot_token', чтобы приложение запускалось
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

# Мы убрали блоки 'if not ... raise ValueError', чтобы приложение не падало при отсутствии .env
