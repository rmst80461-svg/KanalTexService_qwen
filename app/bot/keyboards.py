"""Клавиатуры для КаналТехСервис бота (по структуре ShveinyiHUB)."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def get_persistent_menu() -> ReplyKeyboardMarkup:
    """Одна кнопка меню внизу экрана."""
    keyboard = [[KeyboardButton("☰ Меню")]]
    return ReplyKeyboardMarkup(keyboard,
                               resize_keyboard=True,
                               one_time_keyboard=False)


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
        [InlineKeyboardButton("🔧  Сантехнические работы", callback_data="price_plumbing")],
        [InlineKeyboardButton("💧  Установка септика       ", callback_data="price_installation")],
        [InlineKeyboardButton("🔍  Диагностика труб          ", callback_data="price_diagnostics")],
        [InlineKeyboardButton("🛠  Ремонт канализации     ", callback_data="price_repair")],
        [InlineKeyboardButton("◀️  Назад в меню              ", callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_services_menu() -> InlineKeyboardMarkup:
    """Меню услуг для заявки."""
    buttons = [
        [InlineKeyboardButton("🚚  Откачка септика          ", callback_data="service_septic")],
        [InlineKeyboardButton("🚽  Прочистка канализации", callback_data="service_cleaning")],
        [InlineKeyboardButton("🔧  Вызов сантехника         ", callback_data="service_plumber")],
        [InlineKeyboardButton("💧  Установка септика       ", callback_data="service_installation")],
        [InlineKeyboardButton("🔍  Видеодиагностика        ", callback_data="service_video")],
        [InlineKeyboardButton("🛠  Ремонт труб                  ", callback_data="service_pipe_repair")],
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
    buttons = [[
        InlineKeyboardButton("◀️  Главное меню               ", callback_data="back_menu")
    ]]
    return InlineKeyboardMarkup(buttons)


def get_ai_response_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для ответа AI."""
    buttons = [
        [InlineKeyboardButton("📝  Оформить заявку          ", callback_data="new_order")],
        [InlineKeyboardButton("◀️  В меню                          ", callback_data="back_menu")]
    ]
    return InlineKeyboardMarkup(buttons)


def get_admin_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню админа (Reply Keyboard) с фильтрами."""
    keyboard = [
        [KeyboardButton("📋 Новые заявки"), KeyboardButton("⏳ В работе")],
        [KeyboardButton("✅ Выполнены"), KeyboardButton("📊 Все заявки")],
        [KeyboardButton("📈 Статистика"), KeyboardButton("👥 Пользователи")],
        [KeyboardButton("📢 Рассылка"), KeyboardButton("⚙️ Настройки")],
        [KeyboardButton("◀️ Выйти")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_admin_inline_menu() -> InlineKeyboardMarkup:
    """Инлайн меню админа."""
    buttons = [
        [InlineKeyboardButton("📦 Управление через веб", callback_data="open_web_admin")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_admin_orders_submenu() -> InlineKeyboardMarkup:
    """Подменю управления заявками."""
    buttons = [
        [InlineKeyboardButton("🆕 Новые заявки", callback_data="admin_orders_new")],
        [InlineKeyboardButton("🔄 В процессе", callback_data="admin_orders_in_progress")],
        [InlineKeyboardButton("✅ Завершенные", callback_data="admin_orders_completed")],
        [InlineKeyboardButton("❌ Отмененные", callback_data="admin_orders_cancelled")],
        [InlineKeyboardButton("◀️ Назад", callback_data="admin_back_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_admin_back_menu() -> InlineKeyboardMarkup:
    """Кнопка назад в админ-панель."""
    buttons = [[
        InlineKeyboardButton("◀️ В админ-панель", callback_data="admin_back_menu")
    ]]
    return InlineKeyboardMarkup(buttons)


def get_admin_order_detail_keyboard(order_id: int, order_status: str) -> InlineKeyboardMarkup:
    """Клавиатура для детального просмотра заявки."""
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
            InlineKeyboardButton("🗑 Удалить", callback_data=f"status_deleted_{order_id}")
        ])
    else:
        buttons.append([
            InlineKeyboardButton("🗑 Удалить заявку", callback_data=f"status_deleted_{order_id}")
        ])

    buttons.append([
        InlineKeyboardButton("✉️ Написать клиенту", callback_data=f"contact_client_{order_id}")
    ])

    back_data = {
        'new': 'admin_orders_new',
        'in_progress': 'admin_orders_in_progress',
        'completed': 'admin_orders_completed',
        'cancelled': 'admin_orders_cancelled'
    }.get(order_status, 'admin_back_menu')

    buttons.append(
        [InlineKeyboardButton("◀️ Назад к списку", callback_data=back_data)]
    )

    return InlineKeyboardMarkup(buttons)


def get_admin_orders_menu() -> InlineKeyboardMarkup:
    """Меню управления заявками."""
    return get_admin_orders_submenu()


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для отправки контакта."""
    keyboard = [[KeyboardButton("📱 Отправить номер телефона", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для отправки местоположения."""
    keyboard = [
        [KeyboardButton("📍 Отправить местоположение", request_location=True)],
        [KeyboardButton("✏️ Ввести адрес вручную")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения."""
    buttons = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_yes")],
        [InlineKeyboardButton("❌ Отменить", callback_data="confirm_no")]
    ]
    return InlineKeyboardMarkup(buttons)
