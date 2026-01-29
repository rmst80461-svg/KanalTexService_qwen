"""Обработчики команд бота."""
from telegram import Update
from telegram.ext import ContextTypes
from app.bot.keyboards import get_main_menu, get_back_button
from app.models.database import Database
import os
import logging

logger = logging.getLogger(__name__)

COMPANY_INFO = {
    "name": "КаналТехСервис",
    "phone": "+7 (XXX) XXX-XX-XX",
    "email": "info@kanalteh.ru",
    "address": "Москва и Московская область",
    "hours": "Круглосуточно, 24/7"
}

LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets', 'logo.jpg')

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user = update.effective_user
    user_id = user.id
    
    # Регистрируем пользователя
    db.add_user(user_id, user.username, user.first_name, user.last_name)
    db.update_user_activity(user_id)
    
    name = user.first_name or "друг"
    caption = f"🚿 *КаналТехСервис*\n\nЗдравствуйте, {name}!\nЧем могу помочь?"
    
    # Отправляем логотип если есть
    if os.path.exists(LOGO_PATH):
        try:
            with open(LOGO_PATH, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=caption,
                    parse_mode="Markdown"
                )
        except:
            await update.message.reply_text(caption, parse_mode="Markdown")
    else:
        await update.message.reply_text(caption, parse_mode="Markdown")
    
    await update.message.reply_text(
        "🚿 *КаналТехСервис* — Главное меню",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    help_text = (
        "ℹ️ *Справка по боту КаналТехСервис*\n\n"
        "*Доступные команды:*\n"
        "/start - Главное меню\n"
        "/order - Оформить заявку\n"
        "/services - Услуги и цены\n"
        "/status - Статус заявки\n"
        "/faq - Частые вопросы\n"
        "/contact - Контакты\n"
        "/help - Эта справка\n\n"
        "*Наши услуги:*\n"
        "🚿 Откачка септиков и выгребных ям\n"
        "🔧 Прочистка канализации\n"
        "💧 Устранение засоров\n"
        "🌊 Промывка труб\n"
        "⚙️ Обслуживание септиков\n"
        "🌧 Ливневая канализация\n"
        "📹 Видеодиагностика\n"
        "🔨 Ремонт систем\n\n"
        f"📞 Телефон: {COMPANY_INFO['phone']}\n"
        f"⏰ Режим работы: {COMPANY_INFO['hours']}"
    )
    
    await update.message.reply_text(
        help_text,
        reply_markup=get_back_button(),
        parse_mode="Markdown"
    )

async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /faq."""
    from app.bot.keyboards import get_faq_menu
    
    if update.message:
        await update.message.reply_text(
            "❓ Выберите интересующий вопрос:",
            reply_markup=get_faq_menu()
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /status."""
    user_id = update.effective_user.id
    orders = db.get_user_orders(user_id)
    
    if not orders:
        text = "🔍 У вас нет заявок.\n\nОформите первую заявку через /order"
    else:
        from app.bot.handlers.orders import format_order_id
        text = "🔍 *Ваши заявки:*\n\n"
        status_map = {
            "new": "🆕 Новая",
            "accepted": "✅ Принята",
            "in_progress": "🔄 В работе",
            "completed": "✅ Выполнена",
            "issued": "📤 Закрыта",
            "cancelled": "❌ Отменена"
        }
        for order in orders[:5]:
            status = status_map.get(str(order['status']), str(order['status']))
            desc = str(order['description']) if order['description'] else "Услуга"
            formatted_id = format_order_id(int(order['order_id']), order['created_at'])
            text += f"*{formatted_id}* - {status}\n{desc[:50]}...\n\n"
    
    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
