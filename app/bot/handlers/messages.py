"""Обработчик обычных сообщений."""
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных текстовых сообщений."""
    from app.models.database import Database
    
    # Обновляем активность пользователя
    db = Database()
    db.update_user_activity(update.effective_user.id)
    
    text = update.message.text
    
    # Обрабатываем простые сообщения
    if "привет" in text.lower():
        await update.message.reply_text(
            "👋 Здравствуйте! Чем могу помочь?\n"
            "Нажмите /start для просмотра меню."
        )
    elif "цен" in text.lower():
        await update.message.reply_text(
            "💰 Посмотреть цены можно в меню 'Услуги и цены' или нажмите /services"
        )
    elif "контакт" in text.lower() or "телефон" in text.lower():
        await update.message.reply_text(
            "📞 Наши контакты:\n"
            "\u0422елефон: +7 (XXX) XXX-XX-XX\n"
            "Или нажмите /contact"
        )
    else:
        await update.message.reply_text(
            "🤔 Не совсем понял...\n\n"
            "Используйте кнопки меню или команду /help для справки."
        )
