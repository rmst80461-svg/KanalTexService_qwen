"""
Main entry point for the refactored application
"""
import asyncio
import logging
import os
import sys
import re
from flask import Flask

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration
from app.config import FLASK_SECRET_KEY, BOT_TOKEN
from app.models.database import Database
from app.bot.bot_handler import TelegramBot
from app.web.routes import setup_routes


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


def create_app(db: Database, telegram_bot: TelegramBot):
    """Create and configure the Flask application"""
    try:
        app = Flask(__name__)
        app.config['SECRET_KEY'] = FLASK_SECRET_KEY
        
        # Setup routes with database and bot instances
        setup_routes(app, db, telegram_bot)
        
        logger.info("Flask app created successfully")
        return app
    except Exception as e:
        logger.error(f"Error creating Flask app: {e}")
        raise


async def run_bot(bot_instance: TelegramBot):
    """Function to run Telegram bot"""
    try:
        logger.info("Starting Telegram bot...")
        await bot_instance.run()
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise


def main():
    """Main function"""
    try:
        # ========== VALIDATE BOT_TOKEN ==========
        logger.info("Validating BOT_TOKEN...")
        
        if not BOT_TOKEN:
            logger.error(
                "\n" + "="*60 + "\n"
                "🔴 CRITICAL ERROR: BOT_TOKEN is not set!\n\n"
                "To fix this:\n"
                "1. Go to Telegram and find @BotFather\n"
                "2. Send /mybots → select your bot → API Token\n"
                "3. Copy the token (format: 1234567890:ABCdef...)\n"
                "4. On BotHost: Settings → Environment Variables\n"
                "5. Add: BOT_TOKEN = your_token_here\n"
                "6. Restart the application\n"
                "="*60
            )
            sys.exit(1)
        
        if not validate_bot_token(BOT_TOKEN):
            logger.error(
                "\n" + "="*60 + "\n"
                "🔴 CRITICAL ERROR: BOT_TOKEN format is invalid!\n\n"
                f"Current token: {BOT_TOKEN[:20]}...\n\n"
                "Valid format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n\n"
                "Check for:\n"
                "- Extra spaces or quotes\n"
                "- Missing colon (:)\n"
                "- Invalid characters\n"
                "="*60
            )
            sys.exit(1)
        
        logger.info("✓ BOT_TOKEN format is valid")
        
        # ========== INITIALIZE DATABASE ==========
        logger.info("Initializing database...")
        db = Database()
        logger.info("✓ Database initialized")
        
        # ========== INITIALIZE BOT ==========
        logger.info("Initializing Telegram bot...")
        telegram_bot = TelegramBot(db)
        logger.info("✓ Telegram bot initialized")
        
        # ========== CREATE FLASK APP ==========
        logger.info("Creating Flask application...")
        app = create_app(db, telegram_bot)
        logger.info("✓ Flask app created")
        
        # ========== GET PORT ==========
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"✓ Port configured: {port}")
        
        # ========== START BOT ==========
        logger.info("="*60)
        logger.info("🚀 Starting application with Telegram bot polling...")
        logger.info("="*60)
        
        # Run the bot
        asyncio.run(run_bot(telegram_bot))
        
    except KeyboardInterrupt:
        logger.info("\n" + "="*60)
        logger.info("⏹️  Application stopped by user")
        logger.info("="*60)
    except Exception as e:
        logger.error("\n" + "="*60)
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
        logger.error("="*60)
        sys.exit(1)


if __name__ == '__main__':
    main()
