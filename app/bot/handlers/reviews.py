"""Обработчики для работы с отзывами."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import logging

logger = logging.getLogger(__name__)

# States для ConversationHandler
REVIEW_RATING, REVIEW_COMMENT = range(2)


async def request_review(application, user_id: int, order_id: int):
    """Запрос отзыва у клиента."""
    from app.bot.keyboards import get_rating_keyboard
    from app.bot.handlers.orders import format_order_id
    from datetime import datetime
    
    text = (
        f"⭐ *Оцените нашу работу*\n\n"
        f"Ваш заказ {format_order_id(order_id, datetime.now())} завершен.\n"
        f"Пожалуйста, оцените качество нашей работы:"
    )
    
    try:
        await application.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=get_rating_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить запрос на отзыв: {e}")


async def start_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало оставления отзыва."""
    from app.bot.keyboards import get_rating_keyboard
    
    text = "⭐ *Оставить отзыв*\n\nОцените нашу работу:"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_rating_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text=text,
            reply_markup=get_rating_keyboard(),
            parse_mode="Markdown"
        )
    
    return REVIEW_RATING


async def receive_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение оценки."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "skip_review":
        await query.edit_message_text("✅ Спасибо! Мы всегда рады вам помочь!")
        return ConversationHandler.END
    
    rating = int(query.data.split('_')[1])
    context.user_data['review_rating'] = rating
    
    stars = "⭐" * rating
    
    text = (
        f"✅ Вы поставили оценку: {stars}\n\n"
        "📝 Теперь напишите комментарий (или /skip для пропуска):"
    )
    
    await query.edit_message_text(text, parse_mode="Markdown")
    return REVIEW_COMMENT


async def receive_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение комментария."""
    from app.models.database import Database
    
    comment = update.message.text if update.message.text != "/skip" else None
    rating = context.user_data.get('review_rating', 5)
    
    # Сохраняем отзыв в БД
    db = Database()
    db.add_review(
        user_id=update.effective_user.id,
        rating=rating,
        comment=comment
    )
    
    await update.message.reply_text(
        "✅ *Спасибо за отзыв!*\n\n"
        "Ваше мнение очень важно для нас!\n"
        "Будем рады видеть вас снова! 💧",
        parse_mode="Markdown"
    )
    
    context.user_data.clear()
    return ConversationHandler.END


async def skip_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск комментария."""
    from app.models.database import Database
    
    rating = context.user_data.get('review_rating', 5)
    
    # Сохраняем отзыв без комментария
    db = Database()
    db.add_review(
        user_id=update.effective_user.id,
        rating=rating,
        comment=None
    )
    
    await update.message.reply_text(
        "✅ *Спасибо за оценку!*\n\n"
        "Будем рады видеть вас снова! 💧",
        parse_mode="Markdown"
    )
    
    context.user_data.clear()
    return ConversationHandler.END


def get_review_conversation_handler():
    """Получить ConversationHandler для отзывов."""
    from telegram.ext import CallbackQueryHandler, MessageHandler, filters, CommandHandler
    
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_review, pattern="^leave_review$"),
        ],
        states={
            REVIEW_RATING: [
                CallbackQueryHandler(receive_rating, pattern="^rating_"),
                CallbackQueryHandler(receive_rating, pattern="^skip_review$"),
            ],
            REVIEW_COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_comment),
                CommandHandler("skip", skip_comment),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", lambda u, c: ConversationHandler.END),
        ],
        allow_reentry=True,
        per_message=False
    )
