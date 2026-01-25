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
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')

if ADMIN_PASSWORD_HASH is None:
    raise ValueError("Не установлен ADMIN_PASSWORD_HASH в .env файле")

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не установлен BOT_TOKEN в .env файле")