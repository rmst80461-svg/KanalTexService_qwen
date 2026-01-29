"""Обработчики для создания и управления заказами."""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from app.models.database import Database
from app.bot.keyboards import get_services_menu, get_back_button
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# States для ConversationHandler
SELECT_SERVICE, SEND_PHOTO, ENTER_DESCRIPTION, ENTER_NAME, ENTER_PHONE, CONFIRM_ORDER = range(6)

db = Database()

def format_order_id(order_id: int, created_at) -> str:
    """Форматирование ID заказа с датой."""
    if isinstance(created_at, str):
        try:
            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except:
            return f"#{order_id:04d}"
    else:
        date_obj = created_at
    
    return f"#{date_obj.strftime('%d%m')}-{order_id:03d}"

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания заказа."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text="🚿 *КаналТехСервис* — Создание заявки\n\nВыберите необходимую услугу:",
            reply_markup=get_services_menu(),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text="🚿 *КаналТехСервис* — Создание заявки\n\nВыберите необходимую услугу:",
            reply_markup=get_services_menu(),
            parse_mode="Markdown"
        )
    return SELECT_SERVICE

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор услуги."""
    query = update.callback_query
    await query.answer()

    service_map = {
        "service_septic": "Откачка септика",
        "service_cleaning": "Прочистка канализации",
        "service_blockage": "Устранение засоров",
        "service_flushing": "Промывка труб",
        "service_service": "Обслуживание септика",
        "service_storm": "Ливневая канализация",
        "service_video": "Видеодиагностика",
        "service_repair": "Ремонт систем",
        "service_other": "Другая услуга"
    }

    service_name = service_map.get(query.data, "Услуга")
    context.user_data['order_service'] = service_name

    keyboard = [
        [InlineKeyboardButton("📷 Отправить фото", callback_data="send_photo_yes")],
        [InlineKeyboardButton("⏭ Пропустить фото", callback_data="skip_photo")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_order")]
    ]
    
    await query.edit_message_text(
        text=f"✅ Выбрана услуга: *{service_name}*\n\n📸 Отправьте фото проблемы (если есть) или пропустите этот шаг:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return SEND_PHOTO

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение фото."""
    if update.message and update.message.photo:
        # Сохраняем file_id самого большого фото
        context.user_data['order_photo'] = update.message.photo[-1].file_id
        
        keyboard = [
            [InlineKeyboardButton("📝 Добавить описание", callback_data="add_description")],
            [InlineKeyboardButton("⏭ Пропустить описание", callback_data="skip_description")],
        ]
        
        await update.message.reply_text(
            text="✅ Фото получено!\n\n📝 Опишите подробнее проблему или пропустите:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ENTER_DESCRIPTION
    return SEND_PHOTO

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск фото."""
    query = update.callback_query
    await query.answer()
    
    context.user_data['order_photo'] = None
    
    keyboard = [
        [InlineKeyboardButton("📝 Добавить описание", callback_data="add_description")],
        [InlineKeyboardButton("⏭ Пропустить описание", callback_data="skip_description")],
    ]
    
    await query.edit_message_text(
        text="📝 Опишите подробнее проблему или пропустите:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ENTER_DESCRIPTION

async def enter_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод описания."""
    if update.message and update.message.text:
        context.user_data['order_description'] = update.message.text
    elif update.callback_query:
        await update.callback_query.answer()
        context.user_data['order_description'] = None

    # Проверяем, есть ли имя в Telegram
    user = update.effective_user
    telegram_name = user.first_name or user.username or "Клиент"
    
    keyboard = [
        [InlineKeyboardButton(f"✅ Использовать '{telegram_name}'", callback_data="use_tg_name")],
        [InlineKeyboardButton("✏️ Ввести другое имя", callback_data="enter_custom_name")],
    ]
    
    text = "👤 Как к вам обращаться?"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    return ENTER_NAME

async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск описания."""
    query = update.callback_query
    await query.answer()
    context.user_data['order_description'] = None
    
    user = update.effective_user
    telegram_name = user.first_name or user.username or "Клиент"
    
    keyboard = [
        [InlineKeyboardButton(f"✅ Использовать '{telegram_name}'", callback_data="use_tg_name")],
        [InlineKeyboardButton("✏️ Ввести другое имя", callback_data="enter_custom_name")],
    ]
    
    await query.edit_message_text(
        "👤 Как к вам обращаться?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ENTER_NAME

async def use_tg_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Использовать имя из Telegram."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    context.user_data['client_name'] = user.first_name or user.username or "Клиент"
    
    keyboard = [
        [InlineKeyboardButton("📱 Отправить номер", callback_data="send_phone")],
        [InlineKeyboardButton("⏭ Пропустить", callback_data="skip_phone")],
    ]
    
    await query.edit_message_text(
        "📞 Укажите контактный телефон:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ENTER_PHONE

async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод имени."""
    if update.message and update.message.text:
        context.user_data['client_name'] = update.message.text
        
        keyboard = [
            [InlineKeyboardButton("📱 Отправить номер", callback_data="send_phone")],
            [InlineKeyboardButton("⏭ Пропустить", callback_data="skip_phone")],
        ]
        
        await update.message.reply_text(
            "📞 Укажите контактный телефон:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ENTER_PHONE
    elif update.callback_query and update.callback_query.data == "enter_custom_name":
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "👤 Введите ваше имя:"
        )
        return ENTER_NAME

async def enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод телефона."""
    if update.message and update.message.text:
        context.user_data['client_phone'] = update.message.text
    elif update.callback_query:
        await update.callback_query.answer()
    
    return await confirm_order_view(update, context)

async def skip_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск телефона."""
    query = update.callback_query
    await query.answer()
    context.user_data['client_phone'] = None
    return await confirm_order_view(update, context)

async def confirm_order_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать подтверждение заказа."""
    service = context.user_data.get('order_service', 'Не указано')
    description = context.user_data.get('order_description', 'Не указано')
    name = context.user_data.get('client_name', 'Не указано')
    phone = context.user_data.get('client_phone', 'Не указано')
    has_photo = "Да" if context.user_data.get('order_photo') else "Нет"
    
    text = (
        "📋 *Проверьте данные заявки:*\n\n"
        f"🚿 Услуга: {service}\n"
        f"📝 Описание: {description}\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"📷 Фото: {has_photo}\n\n"
        "Подтвердить создание заявки?"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_order")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_order")]
    ]
    
    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    return CONFIRM_ORDER

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение и создание заказа."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    service = context.user_data.get('order_service')
    description = context.user_data.get('order_description')
    photo = context.user_data.get('order_photo')
    name = context.user_data.get('client_name')
    phone = context.user_data.get('client_phone')
    
    # Создаем заказ в БД
    order_id = db.create_order(
        user_id=user_id,
        service_type=service,
        category=service,
        description=description,
        photo_path=photo
    )
    
    # Обновляем имя и телефон пользователя
    user = db.get_user(user_id)
    if not user:
        db.add_user(user_id, update.effective_user.username, 
                   update.effective_user.first_name, 
                   update.effective_user.last_name)
    
    formatted_id = format_order_id(order_id, datetime.now())
    
    await query.edit_message_text(
        f"✅ Заявка *{formatted_id}* успешно создана!\n\n"
        "🚿 *КаналТехСервис*\n\n"
        "Наш специалист свяжется с вами в ближайшее время для уточнения деталей и согласования времени выезда.\n\n"
        "📞 Вы также можете позвонить нам:\n"
        "+7 (XXX) XXX-XX-XX",
        parse_mode="Markdown"
    )
    
    # Очищаем данные
    context.user_data.clear()
    
    # TODO: Уведомить админов о новом заказе
    
    return ConversationHandler.END

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена создания заказа."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            "❌ Создание заявки отменено.\n\n"
            "Вы можете вернуться в главное меню командой /start"
        )
    else:
        await update.message.reply_text(
            "❌ Создание заявки отменено.\n\n"
            "Вы можете вернуться в главное меню командой /start"
        )
    
    context.user_data.clear()
    return ConversationHandler.END

async def handle_order_status_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка изменения статуса заказа админом."""
    query = update.callback_query
    await query.answer()
    
    # TODO: Реализовать логику изменения статуса
    await query.edit_message_text("Функция в разработке")
