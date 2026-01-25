"""
Main entry point for the application
"""
import asyncio
import logging
import threading
import os
from flask import Flask

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from app.models.database import Database
from app.bot.bot_handler import TelegramBot
from app.web.routes import setup_routes
from app.config import FLASK_SECRET_KEY


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    
    # Initialize database
    db = Database()
    
    # Initialize bot (will be passed to routes later)
    telegram_bot = TelegramBot(db)
    
    # Setup routes with database and bot instances
    setup_routes(app, db, telegram_bot)
    
    return app, telegram_bot


def run_flask():
    """Function to run Flask application"""
    app, _ = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


async def run_bot(bot_instance):
    """Function to run Telegram bot"""
    await bot_instance.run()


if __name__ == '__main__':
    # Initialize database and bot
    db = Database()
    telegram_bot = TelegramBot(db)
    
    # Create Flask app with the shared instances
    app = Flask(__name__)
    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    setup_routes(app, db, telegram_bot)
    
    # Run Flask in a separate thread
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run the bot
    try:
        asyncio.run(run_bot(telegram_bot))
    except KeyboardInterrupt:
        logging.info("Application stopped by user")
    except Exception as e:
        logging.error(f"Error running application: {e}")