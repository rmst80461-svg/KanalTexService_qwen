"""Команды бота."""
from telegram import Update
from telegram.ext import ContextTypes
import os
import logging

logger = logging.getLogger(__name__)

COMPANY_INFO = {
    "name": "КаналТехСервис",
    "phone": "+7 (XXX) XXX-XX-XX",  # Замените на реальный
    "address": "г. Москва и МО",  # Замените на реальный
    "hours": "Круглосуточно",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start."""
    from app.bot.keyboards import get_main_menu
    from app.models.database import Database
    
    user = update.effective_user
    
    # Добавляем пользователя в БД
    db = Database()
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.update_user_activity(user.id)
    
    name = user.first_name or "Друг"
    
    # Проверяем, есть ли логотип
    logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "logo.jpg")
    
    text = (
        f"💧 *КаналТехСервис*\n\n"
        f"Здравствуйте, {name}!\n\n"
        f"Мы предоставляем полный спектр ассенизаторских услуг:\n"
        "• Откачка септиков\n"
        "• Прочистка канализации\n"
        "• Ремонт труб\n"
        "• Видеодиагностика\n\n"
        "🕰 Работаем круглосуточно!\n"
        "🚛 Выезд в течение 1-2 часов!"
    )
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=text,
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text(text, parse_mode="Markdown")
    
    await update.message.reply_text(
        "💧 *КаналТехСервис — Главное меню*",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help."""
    text = (
        "🆘 *Справка по боту*\n\n"
        "*Доступные команды:*\n"
        "/start — Главное меню\n"
        "/order — Создать заказ\n"
        "/status — Проверить статус заказа\n"
        "/services — Услуги и цены\n"
        "/faq — Частые вопросы\n"
        "/contact — Контакты\n\n"
        "*Как сделать заказ:*\n"
        "1. Нажмите /order\n"
        "2. Выберите услугу\n"
        "3. Опишите проблему\n"
        "4. Отправьте фото (опционально)\n"
        "5. Укажите контакты\n\n"
        f"📞 *Связь:* {COMPANY_INFO['phone']}"
    )
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /faq."""
    from app.bot.keyboards import get_faq_menu
    
    text = "❓ *Частые вопросы*\n\nВыберите интересующий вопрос:"
    
    await update.message.reply_text(
        text=text,
        reply_markup=get_faq_menu(),
        parse_mode="Markdown"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status - проверка статуса заказов."""
    from app.models.database import Database
    from app.bot.handlers.orders import format_order_id
    
    db = Database()
    user_id = update.effective_user.id
    orders = db.get_user_orders(user_id)
    
    if not orders:
        text = (
            "🔍 *Ваши заказы*\n\n"
            "У вас пока нет заказов.\n\n"
            f"Создайте первый заказ или позвоните: {COMPANY_INFO['phone']}"
        )
    else:
        text = "🔍 *Ваши заказы:*\n\n"
        
        status_map = {
            "new": "🆕 Новый",
            "accepted": "✅ Принят",
            "in_progress": "🔄 В работе",
            "completed": "✔️ Завершен",
            "cancelled": "❌ Отменен"
        }
        
        for order in orders[:10]:  # Показываем до 10 заказов
            status = status_map.get(order['status'], order['status'])
            service = order['service_type'] or "Услуга"
            formatted_id = format_order_id(order['order_id'], order['created_at'])
            text += f"*{formatted_id}* - {status}\n{service}\n\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")
