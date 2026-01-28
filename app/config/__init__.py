"""
Configuration module for the application
NOTE: .env loading happens in main.py before this module is imported
"""
import os
import sys
from pathlib import Path

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

# ========== TELEGRAM ADMINS CONFIGURATION ==========
# Parse ADMIN_IDS from comma-separated string in .env
# Example in .env: ADMIN_IDS=12345, 67890, 112233
raw_admin_ids = os.getenv('ADMIN_IDS', '').strip()

ADMIN_IDS = []
if raw_admin_ids:
    for part in raw_admin_ids.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            admin_id = int(part)
            ADMIN_IDS.append(admin_id)
        except ValueError:
            print(f"⚠️  ADMIN_IDS: Skipping invalid value '{part}' (must be a number)")
else:
    print("ℹ️  ADMIN_IDS not set - admin access available only via web interface")

if ADMIN_IDS:
    print(f"✓ Loaded {len(ADMIN_IDS)} Telegram admin(s): {ADMIN_IDS}")

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
