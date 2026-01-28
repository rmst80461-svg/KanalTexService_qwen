"""
Main entry point for the refactored application
"""
import asyncio
import logging
import os
import sys
import re
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_env_from_root():
    """
    Load .env file from project root (where main.py is located)
    This ensures all settings (BOT_TOKEN, ADMIN_IDS, etc.) are loaded correctly
    """
    # Path to project root (where main.py is)
    base_dir = Path(__file__).resolve().parent
    env_path = base_dir / ".env"
    
    if env_path.exists():
        print(f"📄 Loading .env from project root: {env_path}")
        load_dotenv(env_path)
        return True
    else:
        print(f"⚠️  .env not found in project root ({env_path})")
        print("   Using system environment variables only")
        return False


def load_bot_token() -> str:
    """
    Load BOT_TOKEN with fallback strategy:
    1. Try to get from environment variable (BotHost sets it here)
    2. If not found, try to read from bot_token.txt in project root
    3. If neither exists, return empty string (will fail validation)
    """
    # Strategy 1: Environment variable (BotHost uses this)
    token = os.environ.get('BOT_TOKEN', '').strip()
    if token:
        logger.info("📌 BOT_TOKEN loaded from environment variable")
        return token
    
    # Strategy 2: Fallback to bot_token.txt in project root
    token_file = Path(__file__).parent / 'bot_token.txt'
    if token_file.exists():
        try:
            with open(token_file, 'r') as f:
                token = f.read().strip()
                if token:
                    logger.info("📌 BOT_TOKEN loaded from bot_token.txt (fallback)")
                    return token
        except Exception as e:
            logger.warning(f"Warning: Could not read bot_token.txt: {e}")
    
    # No token found
    return ''


def validate_bot_token(token: str) -> bool:
    """
    Validate Telegram bot token format
    Format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
    """
    if not token:
        return False
    
    # Telegram bot token format: number:alphanumeric
    pattern = r'^\d+:[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, token))


def create_app(db, telegram_bot):
    """Create and configure the Flask application"""
    try:
        app = Flask(__name__)
        # Dynamic secret key generation for development
        from app.config import FLASK_SECRET_KEY
        app.config['SECRET_KEY'] = FLASK_SECRET_KEY
        
        # Setup routes with database and bot instances
        from app.web.routes import setup_routes
        setup_routes(app, db, telegram_bot)
        
        logger.info("✓ Flask app created successfully")
        return app
    except Exception as e:
        logger.error(f"❌ Error creating Flask app: {e}")
        raise


async def run_bot(bot_instance):
    """Function to run Telegram bot"""
    try:
        logger.info("Starting Telegram bot...")
        await bot_instance.run()
    except Exception as e:
        # Check if it's an authorization error
        error_str = str(e).lower()
        if 'unauthorized' in error_str or '401' in error_str:
            logger.error(
                "\n" + "="*60 + "\n"
                "🔴 CRITICAL ERROR: Telegram Authorization Failed!\n\n"
                "The BOT_TOKEN is invalid or expired.\n\n"
                "To fix this:\n"
                "1. Open Telegram and find @BotFather\n"
                "2. Send /mybots → select your bot → API Token\n"
                "3. Copy the full token (1234567890:ABCdef...)\n"
                "4. On BotHost: Settings → Environment Variables\n"
                "5. Update BOT_TOKEN with the new token\n"
                "6. Click 'Restart' button\n\n"
                "OR if using bot_token.txt:\n"
                "1. Create bot_token.txt in project root\n"
                "2. Paste your token (just the token, nothing else)\n"
                "3. Push the changes to BotHost\n"
                "4. Restart the application\n"
                "="*60
            )
        else:
            logger.error(f"❌ Error running bot: {e}", exc_info=True)
        raise


def main():
    """Main function"""
    try:
        logger.info("="*60)
        logger.info("🤖 КаналТехСервис - Telegram Bot & Admin Panel")
        logger.info("="*60)
        
        # ========== LOAD .ENV FROM PROJECT ROOT ==========
        logger.info("\n[0/5] Loading configuration from .env...")
        load_env_from_root()
        
        # ========== LOAD AND VALIDATE BOT_TOKEN ==========
        logger.info("\n[1/5] Loading BOT_TOKEN...")
        bot_token = load_bot_token()
        
        if not bot_token:
            logger.error(
                "\n" + "="*60 + "\n"
                "🔴 CRITICAL ERROR: BOT_TOKEN not found!\n\n"
                "Setup options:\n\n"
                "Option 1: BotHost Environment Variable (Recommended)\n"
                "  1. Go to BotHost panel → Settings\n"
                "  2. Environment Variables section\n"
                "  3. Add new variable: BOT_TOKEN = your_token\n"
                "  4. Click Save and Restart\n\n"
                "Option 2: .env File in Project Root\n"
                "  1. Create file '.env' in project root\n"
                "  2. Add: BOT_TOKEN=your_token\n"
                "  3. Push to BotHost\n"
                "  4. Restart application\n\n"
                "Option 3: bot_token.txt File\n"
                "  1. Create file 'bot_token.txt' in project root\n"
                "  2. Paste your token (just the token, no spaces)\n"
                "  3. Push to BotHost\n"
                "  4. Restart application\n\n"
                "Get token from @BotFather:\n"
                "  1. Open Telegram, find @BotFather\n"
                "  2. Send /mybots\n"
                "  3. Select your bot → API Token\n"
                "  4. Copy token (format: 1234567890:ABCdef...)\n"
                "="*60
            )
            sys.exit(1)
        
        if not validate_bot_token(bot_token):
            logger.error(
                "\n" + "="*60 + "\n"
                "🔴 CRITICAL ERROR: BOT_TOKEN format is invalid!\n\n"
                f"Received: {bot_token[:30]}...\n\n"
                "Valid format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n\n"
                "Check for:\n"
                "- Extra spaces or quotes (❌ 'token' should be token)\n"
                "- Missing colon (:) separator\n"
                "- Invalid characters (only alphanumeric, _, -)\n"
                "="*60
            )
            sys.exit(1)
        
        logger.info(f"✓ BOT_TOKEN is valid ({bot_token[:15]}...)")
        
        # ========== INITIALIZE DATABASE ==========
        logger.info("\n[2/5] Initializing database...")
        from app.models.database import Database
        db = Database()
        logger.info("✓ Database initialized successfully")
        
        # ========== INITIALIZE BOT ==========
        logger.info("\n[3/5] Initializing Telegram bot...")
        # Temporarily set BOT_TOKEN for bot initialization
        os.environ['BOT_TOKEN'] = bot_token
        from app.bot.bot_handler import TelegramBot
        telegram_bot = TelegramBot(db)
        logger.info("✓ Telegram bot initialized successfully")
        
        # ========== CREATE FLASK APP ==========
        logger.info("\n[4/5] Creating Flask web application...")
        app = create_app(db, telegram_bot)
        
        # ========== STARTUP COMPLETE ==========
        logger.info("\n[5/5] Checking port configuration...")
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"✓ Port configured: {port}")
        
        logger.info("\n" + "="*60)
        logger.info("🚀 Ready to start!")
        logger.info("="*60)
        logger.info("Starting Telegram bot polling...")
        logger.info("(Press Ctrl+C to stop)")
        logger.info("="*60 + "\n")
        
        # Run the bot
        asyncio.run(run_bot(telegram_bot))
        
    except KeyboardInterrupt:
        logger.info("\n" + "="*60)
        logger.info("⏹️  Application stopped by user")
        logger.info("="*60)
    except SystemExit:
        # Re-raise sys.exit() calls
        raise
    except Exception as e:
        logger.error("\n" + "="*60)
        logger.error(f"💥 Fatal error: {type(e).__name__}: {e}", exc_info=True)
        logger.error("="*60)
        sys.exit(1)


if __name__ == '__main__':
    main()
