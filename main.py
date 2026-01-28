"""
Main entry point for the refactored application
"""
import asyncio
import logging
import os
from flask import Flask

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration
frnfig import FLASK_SECRET_KEY, BOT_TOKEN
from app.models.database import Database
from app.bot.bot_handler import TelegramBot
from app.web.routes import setup_routes


def create_app(db: Database, telegram_bot: TelegramBot):
    """Create and configure the Flask application"""
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
        # Initialize database
        logger.info("Initializing database...")
        db = Database()
        
        # Initialize bot
        logger.info("Initializing Telegram bot...")
        telegram_bot = TelegramBot(db)
        
        # Create Flask app with the shared instances
        logger.info("Creating Flask application...")
        app = create_app(db, telegram_bot)
        
        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))
        
        # Log startup info
        logger.info(f"Application configured to run on port {port}")
        logger.info("Starting application with Telegram bot polling...")
        
        # Run the bot
        asyncio.run(run_bot(telegram_bot))
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
