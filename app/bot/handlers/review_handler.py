"""Обработчик системы отзывов для КаналТехСервис."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ..keyboards import Keyboards
import logging

logger = logging.getLogger(__name__)

# States для отзыва
RATING, REVIEW_TEXT = range(2)


class ReviewHandler:
    """Класс для работы с отзывами."""

    def __init__(self, db):
        self.db = db
        self.kb = Keyboards()

    async def start_review(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать процесс оставления отзыва."""
        user_id = update.effective_user.id
        
        # Проверяем есть ли у пользователя завершенные заказы
        orders = self.db.get_user_orders(user_id)
        completed_orders = [o for o in orders if o['status'] == 'completed']
        
        if not completed_orders:
            await update.message.reply_text(
                "У вас пока нет завершенных заказов.\n\n"
                "Оставить отзыв можно после выполнения хотя бы одного заказа."
            )
            return ConversationHandler.END

        await update.message.reply_text(
            "⭐ **Оставить отзыв о КаналТехСервис**\n\n"
            "Мы ценим ваше мнение! Оцените качество наших услуг:",
            parse_mode='Markdown',
            reply_markup=self.kb.rating_keyboard()
        )
        return RATING

    async def select_rating(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор оценки."""
        query = update.callback_query
        await query.answer()

        rating = int(query.data.split('_')[1])
        context.user_data['review_rating'] = rating

        stars = "⭐" * rating
        
        await query.edit_message_text(
            f"Вы поставили оценку: {stars}\n\n"
            "📝 Теперь расскажите подробнее о вашем опыте работы с нами "
            "(или нажмите /skip чтобы пропустить):",
            reply_markup=None
        )
        return REVIEW_TEXT

    async def enter_review_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ввод текста отзыва."""
        comment = None if update.message.text == "/skip" else update.message.text
        rating = context.user_data.get('review_rating')
        user_id = update.effective_user.id

        # Находим последний завершенный заказ
        orders = self.db.get_user_orders(user_id)
        completed_orders = [o for o in orders if o['status'] == 'completed']
        order_id = completed_orders[0]['order_id'] if completed_orders else None

        # Сохраняем отзыв в БД
        review_id = self.db.add_review(
            user_id=user_id,
            rating=rating,
            comment=comment,
            order_id=order_id
        )

        await update.message.reply_text(
            "✅ Спасибо за ваш отзыв!\n\n"
            "Ваше мнение очень важно для нас и помогает улучшать качество услуг КаналТехСервис.",
            reply_markup=self.kb.main_menu()
        )

        context.user_data.clear()
        return ConversationHandler.END

    async def view_reviews(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр отзывов (для админов)."""
        reviews = self.db.get_reviews(published_only=True, limit=10)
        
        if not reviews:
            await update.message.reply_text("Пока нет опубликованных отзывов.")
            return

        text = "⭐ **Отзывы клиентов КаналТехСервис:**\n\n"
        
        for review in reviews:
            stars = "⭐" * review['rating']
            name = review.get('first_name', 'Клиент')
            comment = review.get('comment', '')
            date = review['created_at'][:10]
            
            text += f"{stars}\n👤 {name}\n📅 {date}\n"
            if comment:
                text += f"💬 {comment}\n"
            text += "―――――――――――\n"

        await update.message.reply_text(text, parse_mode='Markdown')

    async def cancel_review(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена создания отзыва."""
        await update.message.reply_text(
            "❌ Создание отзыва отменено.",
            reply_markup=self.kb.main_menu()
        )
        context.user_data.clear()
        return ConversationHandler.END
