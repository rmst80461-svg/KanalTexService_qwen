"""
Configuration module for the application
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask configuration
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
if not FLASK_SECRET_KEY:
    raise ValueError(
        "FLASK_SECRET_KEY is not set! Please set it in your environment variables. "
        "For development, you can add it to .env file."
    )

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')
if not ADMIN_PASSWORD_HASH:
    raise ValueError(
        "ADMIN_PASSWORD_HASH is not set! Please set it in your environment variables. "
        "Use create_admin_password.py to generate a hash."
    )

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is not set! Please set it in your environment variables. "
        "Get your token from @BotFather on Telegram."
    )
