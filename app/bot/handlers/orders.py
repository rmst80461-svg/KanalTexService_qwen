"""Обработчики для работы с заказами."""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# States для ConversationHandler
SELECT_SERVICE, SEND_PHOTO, ENTER_DESCRIPTION, ENTER_NAME, ENTER_PHONE, CONFIRM_ORDER = range(6)

SERVICE_NAMES = {
    "service_septic": "Откачка септика/выгребной ямы",
    "service_cleaning": "Прочистка канализации",
    "service_repair": "Ремонт канализационных труб",
    "service_video": "Видеодиагностика",
    "service_installation": "Монтаж канализации",
    "service_chemical": "Химочистка труб",
    "service_emergency": "Аварийный выезд 24/7",
}


def format_order_id(order_id: int, created_at) -> str:
    """Форматирует ID заказа в формате #0001."""
    return f"#{order_id:04d}"


async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания заказа."""
    from app.bot.keyboards import get_service_selection
    
    text = (
        "📋 *Создание нового заказа*\n\n"
        "Выберите необходимую услугу:"
    )
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_service_selection(),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text=text,
            reply_markup=get_service_selection(),
            parse_mode="Markdown"
        )
    
    return SELECT_SERVICE


async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор услуги."""
    from app.bot.keyboards import get_skip_button
    
    query = update.callback_query
    await query.answer()
    
    service_key = query.data
    service_name = SERVICE_NAMES.get(service_key, "Неизвестная услуга")
    
    context.user_data['service_type'] = service_name
    context.user_data['service_key'] = service_key
    
    text = (
        f"✅ Выбрана услуга: *{service_name}*\n\n"
        "📸 Отправьте фото проблемы (если есть) или нажмите 'Пропустить':"
    )
    
    await query.edit_message_text(
        text=text,
        reply_markup=get_skip_button(),
        parse_mode="Markdown"
    )
    
    return SEND_PHOTO


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение фото от пользователя."""
    from app.bot.keyboards import get_skip_description_button
    
    photo = update.message.photo[-1]
    context.user_data['photo_file_id'] = photo.file_id
    
    text = (
        "✅ Фото получено!\n\n"
        "📝 Опишите проблему подробнее (адрес, этаж, особенности) или нажмите 'Пропустить':"
    )
    
    await update.message.reply_text(
        text=text,
        reply_markup=get_skip_description_button(),
        parse_mode="Markdown"
    )
    
    return ENTER_DESCRIPTION


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск фото."""
    from app.bot.keyboards import get_skip_description_button
    
    query = update.callback_query
    await query.answer()
    
    context.user_data['photo_file_id'] = None
    
    text = "📝 Опишите проблему подробнее (адрес, этаж, особенности) или нажмите 'Пропустить':"
    
    await query.edit_message_text(
        text=text,
        reply_markup=get_skip_description_button(),
        parse_mode="Markdown"
    )
    
    return ENTER_DESCRIPTION


async def enter_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение описания от пользователя."""
    from app.bot.keyboards import get_name_keyboard
    
    context.user_data['description'] = update.message.text
    
    first_name = update.effective_user.first_name or "Клиент"
    
    text = (
        f"✅ Описание сохранено!\n\n"
        f"👤 Как к вам обращаться?\n\n"
        f"Вы можете использовать имя из Telegram: *{first_name}* "
        f"или написать другое имя."
    )
    
    await update.message.reply_text(
        text=text,
        reply_markup=get_name_keyboard(first_name),
        parse_mode="Markdown"
    )
    
    return ENTER_NAME


async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск описания."""
    from app.bot.keyboards import get_name_keyboard
    
    query = update.callback_query
    await query.answer()
    
    context.user_data['description'] = None
    
    first_name = update.effective_user.first_name or "Клиент"
    
    text = (
        f"👤 Как к вам обращаться?\n\n"
        f"Вы можете использовать имя из Telegram: *{first_name}* "
        f"или написать другое имя."
    )
    
    await query.edit_message_text(
        text=text,
        reply_markup=get_name_keyboard(first_name),
        parse_mode="Markdown"
    )
    
    return ENTER_NAME


async def use_tg_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Использование имени из Telegram."""
    from app.bot.keyboards import get_phone_keyboard
    
    query = update.callback_query
    await query.answer()
    
    first_name = update.effective_user.first_name or "Клиент"
    context.user_data['client_name'] = first_name
    
    text = (
        f"✅ Отлично, {first_name}!\n\n"
        "📞 Теперь укажите ваш телефон для связи\n"
        "(в формате +7XXXXXXXXXX):"
    )
    
    await query.edit_message_text(
        text=text,
        reply_markup=get_phone_keyboard(),
        parse_mode="Markdown"
    )
    
    return ENTER_PHONE


async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение имени от пользователя."""
    from app.bot.keyboards import get_phone_keyboard
    
    context.user_data['client_name'] = update.message.text
    
    text = (
        f"✅ Приятно познакомиться, {update.message.text}!\n\n"
        "📞 Укажите ваш телефон для связи\n"
        "(в формате +7XXXXXXXXXX):"
    )
    
    await update.message.reply_text(
        text=text,
        reply_markup=get_phone_keyboard(),
        parse_mode="Markdown"
    )
    
    return ENTER_PHONE


async def enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение телефона от пользователя."""
    from app.bot.keyboards import get_confirm_keyboard
    
    context.user_data['client_phone'] = update.message.text
    
    # Формируем итоговое сообщение
    service = context.user_data.get('service_type', 'Не указано')
    description = context.user_data.get('description', 'Не указано')
    name = context.user_data.get('client_name', 'Не указано')
    phone = context.user_data.get('client_phone', 'Не указано')
    has_photo = "Да" if context.user_data.get('photo_file_id') else "Нет"
    
    text = (
        "📋 *Проверьте данные заказа:*\n\n"
        f"🔧 Услуга: {service}\n"
        f"📝 Описание: {description}\n"
        f"📸 Фото: {has_photo}\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n\n"
        "Подтвердить создание заказа?"
    )
    
    await update.message.reply_text(
        text=text,
        reply_markup=get_confirm_keyboard(),
        parse_mode="Markdown"
    )
    
    return CONFIRM_ORDER


async def skip_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск телефона."""
    from app.bot.keyboards import get_confirm_keyboard
    
    query = update.callback_query
    await query.answer()
    
    context.user_data['client_phone'] = None
    
    # Формируем итоговое сообщение
    service = context.user_data.get('service_type', 'Не указано')
    description = context.user_data.get('description', 'Не указано')
    name = context.user_data.get('client_name', 'Не указано')
    has_photo = "Да" if context.user_data.get('photo_file_id') else "Нет"
    
    text = (
        "📋 *Проверьте данные заказа:*\n\n"
        f"🔧 Услуга: {service}\n"
        f"📝 Описание: {description}\n"
        f"📸 Фото: {has_photo}\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: Не указан\n\n"
        "Подтвердить создание заказа?"
    )
    
    await query.edit_message_text(
        text=text,
        reply_markup=get_confirm_keyboard(),
        parse_mode="Markdown"
    )
    
    return CONFIRM_ORDER


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение и создание заказа."""
    from app.models.database import Database
    
    query = update.callback_query
    await query.answer()
    
    db = Database()
    
    # Создаем заказ в БД
    order_id = db.create_order(
        user_id=update.effective_user.id,
        service_type=context.user_data.get('service_type'),
        category=context.user_data.get('service_key'),
        description=context.user_data.get('description'),
        photo_path=context.user_data.get('photo_file_id')
    )
    
    # Обновляем информацию о пользователе
    db.add_user(
        user_id=update.effective_user.id,
        username=update.effective_user.username,
        first_name=context.user_data.get('client_name'),
        last_name=None
    )
    
    formatted_id = format_order_id(order_id, datetime.now())
    
    text = (
        f"✅ *Заказ {formatted_id} создан!*\n\n"
        "Мы свяжемся с вами в ближайшее время для уточнения деталей.\n\n"
        "Вы можете отследить статус заказа через меню 'Статус заказа'."
    )
    
    await query.edit_message_text(
        text=text,
        parse_mode="Markdown"
    )
    
    # Уведомляем админов о новом заказе
    await notify_admins_new_order(context, order_id, update.effective_user.id, context.user_data)
    
    # Очищаем данные
    context.user_data.clear()
    
    from telegram.ext import ConversationHandler
    return ConversationHandler.END


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена создания заказа."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text("❌ Создание заказа отменено.")
    else:
        await update.message.reply_text("❌ Создание заказа отменено.")
    
    context.user_data.clear()
    
    from telegram.ext import ConversationHandler
    return ConversationHandler.END


async def notify_admins_new_order(context, order_id, user_id, order_data):
    """Уведомление админов о новом заказе."""
    import os
    from app.bot.keyboards import get_order_status_keyboard
    
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    if not admin_ids_str:
        return
    
    admin_ids = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip()]
    
    formatted_id = format_order_id(order_id, datetime.now())
    
    text = (
        f"🆕 *Новый заказ {formatted_id}*\n\n"
        f"👤 Пользователь: {user_id}\n"
        f"🔧 Услуга: {order_data.get('service_type', 'Н/Д')}\n"
        f"📝 Описание: {order_data.get('description', 'Не указано')}\n"
        f"👤 Имя: {order_data.get('client_name', 'Н/Д')}\n"
        f"📞 Телефон: {order_data.get('client_phone', 'Не указан')}"
    )
    
    for admin_id in admin_ids:
        try:
            # Если есть фото, отправляем с фото
            if order_data.get('photo_file_id'):
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=order_data['photo_file_id'],
                    caption=text,
                    reply_markup=get_order_status_keyboard(order_id),
                    parse_mode="Markdown"
                )
            else:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    reply_markup=get_order_status_keyboard(order_id),
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Не удалось уведомить админа {admin_id}: {e}")


async def handle_order_status_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка изменения статуса заказа админом."""
    query = update.callback_query
    await query.answer("Статус обновлен!")
    
    # Парсим callback_data
    data_parts = query.data.split('_')
    new_status = data_parts[1]
    order_id = int(data_parts[2])
    
    # Обновляем статус в БД
    from app.models.database import Database
    db = Database()
    db.update_order_status(order_id, new_status)
    
    # Уведомляем клиента об изменении статуса
    order = db.get_order(order_id)
    if order:
        status_text = {
            'accepted': '✅ Принят в работу',
            'in_progress': '🔄 Выполняется',
            'completed': '✔️ Завершен',
            'cancelled': '❌ Отменен'
        }.get(new_status, 'Обновлен')
        
        formatted_id = format_order_id(order_id, order['created_at'])
        
        try:
            await context.bot.send_message(
                chat_id=order['user_id'],
                text=f"📢 Статус заказа {formatted_id} изменен:\n{status_text}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить клиента: {e}")
