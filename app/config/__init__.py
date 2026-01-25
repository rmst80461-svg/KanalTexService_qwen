"""
Configuration module for the application
"""
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Flask configuration
# Вторым аргументом идет значение по умолчанию, если переменная не найдена
FLASK_SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-key-12345')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', 'default_hash_value')

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "") 
# Мы не кидаем ошибку здесь, чтобы приложение не падало. 
# Бот сам сообщит о проблеме при запуске, если токена не будет.
