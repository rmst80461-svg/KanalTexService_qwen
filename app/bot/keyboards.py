"""Клавиатуры для КаналТехСервис бота (по структуре ShveinyiHUB).
Кнопки, меню, услуги и цены для ассенизаторских и сантехнических услуг.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def get_persistent_menu() -> ReplyKeyboardMarkup:
    """Одна кнопка меню внизу экрана."""
    keyboard = [[KeyboardButton("☰ Меню")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def remove_keyboard() -> ReplyKeyboardRemove:
    """Убрать клавиатуру."""
    return ReplyKeyboardRemove()


def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню бота."""
    buttons = [
        [InlineKeyboardButton("📋  Услуги и цены           ", callback_data="services")],
        [InlineKeyboardButton("➕  Создать заявку          ", callback_data="new_order")],
        [InlineKeyboardButton("🔍  Статус заявки            ", callback_data="check_status")],
        [InlineKeyboardButton("❓  Частые вопросы          ", callback_data="faq")],
        [InlineKeyboardButton("📍  Контакты                    ", callback_data="contacts")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_prices_menu() -> InlineKeyboardMarkup:
    """Меню выбора категории цен."""
    buttons = [
        [InlineKeyboardButton("🚚  Откачка септика          ", callback_data="price_septic")],
        [InlineKeyboardButton("🚽  Прочистка канализации", callback_data="price_cleaning")],
        [InlineKeyboardButton("🔍  Диагностика труб          ", callback_data="price_diagnostics")],
        [InlineKeyboardButton("◀️  Назад в меню              ", callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_services_menu() -> InlineKeyboardMarkup:
    """Меню услуг для заявки."""
    buttons = [
        [InlineKeyboardButton("🚚  Откачка септика          ", callback_data="service_septic")],
        [InlineKeyboardButton("🚽  Прочистка канализации", callback_data="service_cleaning")],
        [InlineKeyboardButton("💧  Каналопромывка          ", callback_data="service_canal_wash")],
        [InlineKeyboardButton("🔧  Илосос                          ", callback_data="service_sludge")],
        [InlineKeyboardButton("🔍  Видеодиагностика        ", callback_data="service_video")],
        [InlineKeyboardButton("🧹  Промывка канализации ", callback_data="service_flushing")],
        [InlineKeyboardButton("❓  Другое                           ", callback_data="service_other")],
        [InlineKeyboardButton("◀️  Назад в меню              ", callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_faq_menu() -> InlineKeyboardMarkup:
    """Меню FAQ."""
    buttons = [
        [InlineKeyboardButton("📋  Какие услуги?               ", callback_data="faq_services")],
        [InlineKeyboardButton("💰  Цены на услуги            ", callback_data="faq_prices")],
        [InlineKeyboardButton("⏰  Сроки выполнения       ", callback_data="faq_timing")],
        [InlineKeyboardButton("📍  Адрес и график            ", callback_data="faq_location")],
        [InlineKeyboardButton("💳  Оплата и гарантия       ", callback_data="faq_payment")],
        [InlineKeyboardButton("📝  Как оформить заявку?  ", callback_data="faq_order")],
        [InlineKeyboardButton("🚚  Зоны обслуживания      ", callback_data="faq_zones")],
        [InlineKeyboardButton("❓  Другой вопрос              ", callback_data="faq_other")],
        [InlineKeyboardButton("◀️  Назад в меню              ", callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка назад в меню."""
    buttons = [[InlineKeyboardButton("◀️  Главное меню               ", callback_data="back_menu")]]
    return InlineKeyboardMarkup(buttons)


def get_ai_chat_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для AI-чата с кнопкой заказа."""
    buttons = [
        [InlineKeyboardButton("📝 Оформить заявку", callback_data="new_order")],
        [InlineKeyboardButton("📞 Позвонить: +7 (904) 363-36-36", callback_data="show_phone")],
        [InlineKeyboardButton("◀️  Главное меню", callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_skip_comment_keyboard() -> InlineKeyboardMarkup:
    """Кнопка пропустить комментарий."""
    buttons = [
        [InlineKeyboardButton("⏭ Без комментария", callback_data="skip_comment")],
        [InlineKeyboardButton("❌ Отменить заявку", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_cancel_order_keyboard() -> InlineKeyboardMarkup:
    """Кнопка отмены заказа."""
    buttons = [
        [InlineKeyboardButton("❌ Отменить заявку", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_confirm_order_keyboard() -> InlineKeyboardMarkup:
    """Кнопки подтверждения заказа."""
    buttons = [
        [InlineKeyboardButton("✅ Подтвердить заявку", callback_data="confirm_order")],
        [InlineKeyboardButton("✏️ Изменить данные", callback_data="edit_order")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_admin_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню админа."""
    keyboard = [
        [KeyboardButton("📋 Новые заявки"), KeyboardButton("⏳ В работе")],
        [KeyboardButton("✅ Выполнены"), KeyboardButton("📊 Все заявки")],
        [KeyboardButton("📈 Статистика"), KeyboardButton("👥 Пользователи")],
        [KeyboardButton("📢 Рассылка"), KeyboardButton("⚙️ Настройки")],
        [KeyboardButton("◀️ Выйти")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_admin_orders_submenu() -> InlineKeyboardMarkup:
    """Подменю управления заявками."""
    buttons = [
        [InlineKeyboardButton("🆕 Новые", callback_data="admin_orders_new")],
        [InlineKeyboardButton("🔄 В процессе", callback_data="admin_orders_in_progress")],
        [InlineKeyboardButton("✅ Завершенные", callback_data="admin_orders_completed")],
        [InlineKeyboardButton("❌ Отмененные", callback_data="admin_orders_cancelled")],
        [InlineKeyboardButton("◀️ Назад", callback_data="admin_back_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_admin_order_detail_keyboard(order_id: int, order_status: str) -> InlineKeyboardMarkup:
    """Клавиатура для деталей заявки."""
    buttons = []

    if order_status == 'new':
        buttons.append([
            InlineKeyboardButton("🔄 В работу", callback_data=f"status_in_progress_{order_id}"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"status_cancelled_{order_id}")
        ])
    elif order_status == 'in_progress':
        buttons.append([
            InlineKeyboardButton("✅ Выполнен", callback_data=f"status_completed_{order_id}"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"status_cancelled_{order_id}")
        ])
    elif order_status == 'completed':
        buttons.append([
            InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_order_{order_id}")
        ])
    else:
        buttons.append([
            InlineKeyboardButton("🗑 Удалить заявку", callback_data=f"delete_order_{order_id}")
        ])

    buttons.append([
        InlineKeyboardButton("✉️ Написать клиенту", callback_data=f"contact_client_{order_id}"),
        InlineKeyboardButton("📜 История", callback_data=f"client_history_{order_id}")
    ])

    back_data = {
        'new': 'admin_orders_new',
        'in_progress': 'admin_orders_in_progress',
        'completed': 'admin_orders_completed',
        'cancelled': 'admin_orders_cancelled'
    }.get(order_status, 'admin_back_menu')

    buttons.append([InlineKeyboardButton("◀️ Назад к списку", callback_data=back_data)])

    return InlineKeyboardMarkup(buttons)
