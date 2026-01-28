"""
Configuration module for the application
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== ENVIRONMENT DETECTION ==========
ENV_MODE = os.getenv('ENVIRONMENT', 'development').lower()
IS_PRODUCTION = ENV_MODE == 'production'
IS_DEVELOPMENT = ENV_MODE == 'development'

# ========== FLASK CONFIGURATION ==========
if IS_PRODUCTION:
    # In production, FLASK_SECRET_KEY is REQUIRED
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    if not FLASK_SECRET_KEY:
        raise ValueError(
            "PRODUCTION ERROR: FLASK_SECRET_KEY is not set!\n"
            "Please set FLASK_SECRET_KEY environment variable."
        )
else:
    # In development, use default if not set
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-me')

# ========== ADMIN CONFIGURATION ==========
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')

if IS_PRODUCTION:
    # In production, ADMIN_PASSWORD_HASH is REQUIRED
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')
    if not ADMIN_PASSWORD_HASH:
        raise ValueError(
            "PRODUCTION ERROR: ADMIN_PASSWORD_HASH is not set!\n"
            "Use create_admin_password.py to generate a hash."
        )
else:
    # In development, use default hash for password '12345'
    ADMIN_PASSWORD_HASH = os.getenv(
        'ADMIN_PASSWORD_HASH',
        '$2b$12$R9h/cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ee3XEALtW5RhHKNa'
    )

# ========== BOT CONFIGURATION ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')

if IS_PRODUCTION:
    # In production, BOT_TOKEN is REQUIRED
    if not BOT_TOKEN:
        raise ValueError(
            "PRODUCTION ERROR: BOT_TOKEN is not set!\n"
            "Get your token from @BotFather on Telegram."
        )

# ========== DATABASE CONFIGURATION ==========
DATABASE_URL = os.getenv('DATABASE_URL', 'requests.db')

# ========== PORT CONFIGURATION ==========
PORT = int(os.getenv('PORT', 5000))
