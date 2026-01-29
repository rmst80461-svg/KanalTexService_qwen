"""Configuration module"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
PORT = int(os.getenv("PORT", "5000"))
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-key-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///botdata.db")

# Company info
COMPANY_NAME = os.getenv("COMPANY_NAME", "КаналТехСервис")
COMPANY_PHONE = os.getenv("COMPANY_PHONE", "+7 (910) 555-84-14")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "info@kanalteh.ru")
COMPANY_CITY = os.getenv("COMPANY_CITY", "Ярцево")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
