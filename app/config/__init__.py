"""
Configuration module for the application
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ========== FLEXIBLE .ENV LOADING ==========
# Try to load .env from multiple locations
def load_env_file():
    """
    Load .env file from multiple possible locations:
    1. Current working directory
    2. Project root (where main.py is)
    3. Parent directory
    """
    possible_paths = [
        Path.cwd() / '.env',                    # Current directory
        Path(__file__).parent.parent.parent / '.env',  # Project root
        Path.cwd().parent / '.env',             # Parent directory
    ]
    
    for env_path in possible_paths:
        if env_path.exists():
            print(f"📄 Loading .env from: {env_path}")
            load_dotenv(env_path)
            return True
    
    print("⚠️  No .env file found, using system environment variables only")
    return False

# Load environment variables
load_env_file()

# ========== ENVIRONMENT DETECTION ==========
ENV_MODE = os.getenv('ENVIRONMENT', 'development').lower()
IS_PRODUCTION = ENV_MODE == 'production'
IS_DEVELOPMENT = ENV_MODE == 'development'

if IS_PRODUCTION:
    print("⚠️  PRODUCTION MODE - Strict validation enabled")
else:
    print("🔧 DEVELOPMENT MODE - Using flexible defaults")

# ========== FLASK CONFIGURATION ==========
if IS_PRODUCTION:
    # In production, FLASK_SECRET_KEY is REQUIRED
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    if not FLASK_SECRET_KEY:
        raise ValueError(
            "PRODUCTION ERROR: FLASK_SECRET_KEY is not set!\n"
            "Please set FLASK_SECRET_KEY environment variable or add to .env file."
        )
else:
    # In development, use default if not set
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-me')
    if FLASK_SECRET_KEY == 'dev-secret-key-change-me':
        print("⚠️  Using default FLASK_SECRET_KEY for development")

# ========== ADMIN CONFIGURATION ==========
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')

if IS_PRODUCTION:
    # In production, ADMIN_PASSWORD_HASH is REQUIRED
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')
    if not ADMIN_PASSWORD_HASH:
        raise ValueError(
            "PRODUCTION ERROR: ADMIN_PASSWORD_HASH is not set!\n"
            "Use create_admin_password.py to generate a hash or add to .env file."
        )
else:
    # In development, use default hash for password '12345'
    ADMIN_PASSWORD_HASH = os.getenv(
        'ADMIN_PASSWORD_HASH',
        '$2b$12$R9h/cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ee3XEALtW5RhHKNa'
    )
    if ADMIN_PASSWORD_HASH == '$2b$12$R9h/cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ee3XEALtW5RhHKNa':
        print("⚠️  Using default admin password: 12345")

# ========== BOT CONFIGURATION ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')

if IS_PRODUCTION:
    # In production, BOT_TOKEN is REQUIRED
    if not BOT_TOKEN:
        raise ValueError(
            "PRODUCTION ERROR: BOT_TOKEN is not set!\n"
            "Get your token from @BotFather and set in environment or .env file."
        )
else:
    # In development, provide helpful message if not set
    if not BOT_TOKEN:
        print(
            "⚠️  BOT_TOKEN is not set!\n"
            "The Telegram bot will not work until you:\n"
            "1. Create .env file in project root\n"
            "2. Add: BOT_TOKEN=your_token_here\n"
            "3. Or set system environment variable\n"
            "Get token from @BotFather: https://t.me/botfather"
        )
    else:
        print(f"✓ BOT_TOKEN loaded (starts with: {BOT_TOKEN[:20]}...)")

# ========== DATABASE CONFIGURATION ==========
DATABASE_URL = os.getenv('DATABASE_URL', 'requests.db')

# ========== PORT CONFIGURATION ==========
PORT = int(os.getenv('PORT', 5000))

print(f"✓ Configuration loaded: {ENV_MODE.upper()} mode")
print(f"✓ Admin username: {ADMIN_USERNAME}")
print(f"✓ Database: {DATABASE_URL}")
print(f"✓ Port: {PORT}")
