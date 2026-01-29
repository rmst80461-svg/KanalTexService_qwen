"""Обработчики для работы с заказами."""
from telegram import Update, PhotoSize
from telegram.ext import ContextTypes, ConversationHandler
import logging
from app.bot.keyboards import (
    get_services_keyboard, get_categories_keyboard, get_confirm_order_keyboard,
    get_cancel_keyboard, get_main_menu_keyboard, get_skip_keyboard
)
from app.models.database import Database

logger = logging.getLogger(__name__)

# States
SELECT_SERVICE, SELECT_CATEGORY, ENTER_DESCRIPTION, UPLOAD_PHOTO, CONFIRM_ORDER = range(5)

db = Database()


async def start_new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало оформления заказа."""
    query = update.callback_query
    
    if query:
        await query.answer()
        await query.edit_message_text(
            "📝 <b>Оформление заказа</b>\n\n"
            "Выберите тип услуги:",
            reply_markup=get_services_keyboard(),
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            "📝 <b>Оформление заказа</b>\n\n"
            "Выберите тип услуги:",
            reply_markup=get_services_keyboard(),
            parse_mode='HTML'
        )
    
    return SELECT_SERVICE


async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор услуги."""
    query = update.callback_query
    await query.answer()
    
    service = query.data.split(':')[1]
    context.user_data['order_service'] = service
    
    service_names = {
        'repair': 'Ремонт одежды',
        'custom': 'Пошив на заказ',
        'alter': 'Ушив/расшив',
        'cleaning': 'Чистка и уход',
        'decoration': 'Декорирование',
        'other': 'Другое'
    }
    
    await query.edit_message_text(
        f"✂️ <b>Выбрано:</b> {service_names.get(service, service)}\n\n"
        "Выберите категорию:",
        reply_markup=get_categories_keyboard(service),
        parse_mode='HTML'
    )
    
    return SELECT_CATEGORY


async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор категории."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_services":
        await query.edit_message_text(
            "📝 <b>Оформление заказа</b>\n\n"
            "Выберите тип услуги:",
            reply_markup=get_services_keyboard(),
            parse_mode='HTML'
        )
        return SELECT_SERVICE
    
    category = query.data.split(':')[1]
    context.user_data['order_category'] = category
    
    await query.edit_message_text(
        "📝 <b>Опишите ваш заказ</b>\n\n"
        "Пожалуйста, опишите что нужно сделать с вашей одеждой.\n"
        "📝 Например: 'Подшить брюки на 5 см, ушить в поясе'",
        parse_mode='HTML'
    )
    
    return ENTER_DESCRIPTION


async def enter_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод описания заказа."""
    description = update.message.text
    
    if description == '❌ Отмена':
        await update.message.reply_text(
            "❌ Оформление заказа отменено",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    context.user_data['order_description'] = description
    
    await update.message.reply_text(
        "📷 <b>Загрузите фото</b>\n\n"
        "Пожалуйста, отправьте фото вашей одежды.\n"
        "Или нажмите 'Пропустить' если фото нет.",
        reply_markup=get_skip_keyboard(),
        parse_mode='HTML'
    )
    
    return UPLOAD_PHOTO


async def upload_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Загрузка фото."""
    if update.callback_query:
        # Пропуск фото
        await update.callback_query.answer()
        context.user_data['order_photo'] = None
    else:
        # Сохранение file_id фото
        photo = update.message.photo[-1]  # Берем самое большое разрешение
        context.user_data['order_photo'] = photo.file_id
    
    # Подтверждение заказа
    service = context.user_data.get('order_service', 'Не указано')
    category = context.user_data.get('order_category', 'Не указано')
    description = context.user_data.get('order_description', 'Не указано')
    has_photo = '✅ Да' if context.user_data.get('order_photo') else '❌ Нет'
    
    confirmation_text = (
        "✅ <b>Подтвердите заказ</b>\n\n"
        f"🔹 <b>Услуга:</b> {service}\n"
        f"🔹 <b>Категория:</b> {category}\n"
        f"🔹 <b>Описание:</b> {description}\n"
        f"🔹 <b>Фото:</b> {has_photo}\n\n"
        "Подтвердить заказ?"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            confirmation_text,
            reply_markup=get_confirm_order_keyboard(),
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            confirmation_text,
            reply_markup=get_confirm_order_keyboard(),
            parse_mode='HTML'
        )
    
    return CONFIRM_ORDER


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение заказа."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_order":
        await query.edit_message_text(
            "❌ Оформление заказа отменено"
        )
        await query.message.reply_text(
            "🏠 Главное меню",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    # Создание заказа в БД
    user_id = update.effective_user.id
    service = context.user_data.get('order_service')
    category = context.user_data.get('order_category')
    description = context.user_data.get('order_description')
    photo = context.user_data.get('order_photo')
    
    try:
        order_id = db.create_order(
            user_id=user_id,
            service_type=service,
            category=category,
            description=description,
            photo_path=photo
        )
        
        await query.edit_message_text(
            f"✅ <b>Заказ №{order_id:04d} успешно создан!</b>\n\n"
            "Мы получили ваш заказ и свяжемся с вами в ближайшее время.\n\n"
            "📞 Мы свяжемся с вами для уточнения деталей!",
            parse_mode='HTML'
        )
        
        await query.message.reply_text(
            "🏠 Возврат в главное меню",
            reply_markup=get_main_menu_keyboard()
        )
        
        # TODO: Отправить уведомление админу
        
        # Очистка данных
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Ошибка при создании заказа: {e}")
        await query.edit_message_text(
            "❌ Произошла ошибка. Попробуйте позже."
        )
    
    return ConversationHandler.END


async def cancel_order_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена оформления заказа."""
    await update.message.reply_text(
        "❌ Оформление заказа отменено",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END
