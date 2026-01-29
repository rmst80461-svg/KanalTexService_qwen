"""Клавиатуры для Telegram бота."""
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from typing import List


def get_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Главное меню."""
    keyboard = [
        ['📝 Оформить заказ', '📋 Мои заказы'],
        ['💰 Прайс-лист', '❓ FAQ'],
        ['⭐ Оставить отзыв', '📞 Контакты']
    ]
    
    if is_admin:
        keyboard.append(['🔑 Админ-панель'])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой Отмена."""
    keyboard = [['❌ Отмена']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_services_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора услуги."""
    keyboard = [
        [InlineKeyboardButton("🧵 Ремонт одежды", callback_data="service:repair")],
        [InlineKeyboardButton("✂️ Пошив на заказ", callback_data="service:custom")],
        [InlineKeyboardButton("👗 Ушив/расшив одежды", callback_data="service:alter")],
        [InlineKeyboardButton("🧵 Чистка и уход", callback_data="service:cleaning")],
        [InlineKeyboardButton("🎨 Декорирование", callback_data="service:decoration")],
        [InlineKeyboardButton("🛠 Другое", callback_data="service:other")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_categories_keyboard(service_type: str) -> InlineKeyboardMarkup:
    """Клавиатура категорий для услуги."""
    categories_map = {
        'repair': [
            ('👕 Верхняя одежда', 'outerwear'),
            ('👖 Брюки/юбки', 'bottoms'),
            ('👗 Платья', 'dresses'),
            ('🧥 Куртки/пальто', 'jackets'),
        ],
        'custom': [
            ('👗 Платье', 'dress'),
            ('👖 Брюки/юбка', 'pants_skirt'),
            ('👕 Блузка/рубашка', 'shirt'),
            ('🧥 Верхняя одежда', 'outerwear'),
        ],
        'alter': [
            ('👖 Укоротить брюки', 'shorten_pants'),
            ('👗 Ушить платье', 'take_in_dress'),
            ('👕 Расширить одежду', 'let_out'),
        ]
    }
    
    categories = categories_map.get(service_type, [('🛠 Стандартное', 'standard')])
    
    keyboard = [[InlineKeyboardButton(name, callback_data=f"category:{cat_id}")] 
                for name, cat_id in categories]
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_services")])
    
    return InlineKeyboardMarkup(keyboard)


def get_confirm_order_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение заказа."""
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить заказ", callback_data="confirm_order")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_my_orders_keyboard(orders: List[dict]) -> InlineKeyboardMarkup:
    """Клавиатура списка заказов."""
    keyboard = []
    
    for order in orders:
        order_id = order['order_id']
        status_emoji = {
            'new': '🆕',
            'in_progress': '⏳',
            'completed': '✅',
            'cancelled': '❌'
        }.get(order['status'], '❓')
        
        button_text = f"{status_emoji} Заказ #{order_id:04d} - {order['service_type']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"order_details:{order_id}")])
    
    if not keyboard:
        keyboard.append([InlineKeyboardButton("📝 Оформить первый заказ", callback_data="new_order")])
    
    return InlineKeyboardMarkup(keyboard)


def get_order_details_keyboard(order_id: int, can_cancel: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура деталей заказа."""
    keyboard = []
    
    if can_cancel:
        keyboard.append([InlineKeyboardButton("❌ Отменить заказ", callback_data=f"cancel_order:{order_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ К моим заказам", callback_data="my_orders")])
    
    return InlineKeyboardMarkup(keyboard)


def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для оценки."""
    keyboard = [
        [
            InlineKeyboardButton("⭐", callback_data="rating:1"),
            InlineKeyboardButton("⭐⭐", callback_data="rating:2"),
            InlineKeyboardButton("⭐⭐⭐", callback_data="rating:3"),
        ],
        [
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rating:4"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rating:5"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_skip_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой Пропустить."""
    keyboard = [[InlineKeyboardButton("⏩ Пропустить", callback_data="skip")]]
    return InlineKeyboardMarkup(keyboard)


# === АДМИН КЛАВИАТУРЫ ===

def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню админа."""
    keyboard = [
        [InlineKeyboardButton("📋 Управление заказами", callback_data="admin:orders")],
        [InlineKeyboardButton("👥 Список пользователей", callback_data="admin:users")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin:stats")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin:broadcast")],
        [InlineKeyboardButton("💰 Управление ценами", callback_data="admin:prices")],
        [InlineKeyboardButton("❓ Управление FAQ", callback_data="admin:faq")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_orders_keyboard() -> InlineKeyboardMarkup:
    """Меню управления заказами."""
    keyboard = [
        [InlineKeyboardButton("🆕 Новые заказы", callback_data="admin:orders:new")],
        [InlineKeyboardButton("⏳ В работе", callback_data="admin:orders:in_progress")],
        [InlineKeyboardButton("✅ Завершенные", callback_data="admin:orders:completed")],
        [InlineKeyboardButton("❌ Отмененные", callback_data="admin:orders:cancelled")],
        [InlineKeyboardButton("⚠️ Зависшие заказы", callback_data="admin:orders:pending")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin:back")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_order_actions_keyboard(order_id: int, current_status: str) -> InlineKeyboardMarkup:
    """Действия над заказом."""
    keyboard = []
    
    if current_status == 'new':
        keyboard.append([InlineKeyboardButton("⏳ Взять в работу", callback_data=f"admin:order:in_progress:{order_id}")])
    
    if current_status == 'in_progress':
        keyboard.append([InlineKeyboardButton("✅ Завершить", callback_data=f"admin:order:completed:{order_id}")])
    
    keyboard.append([InlineKeyboardButton("❌ Отменить", callback_data=f"admin:order:cancelled:{order_id}")])
    keyboard.append([InlineKeyboardButton("📝 Добавить комментарий", callback_data=f"admin:order:note:{order_id}")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin:orders")])
    
    return InlineKeyboardMarkup(keyboard)


def get_pagination_keyboard(current_page: int, total_pages: int, callback_prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура пагинации."""
    keyboard = []
    
    buttons = []
    if current_page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"{callback_prefix}:{current_page-1}"))
    
    buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
    
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"{callback_prefix}:{current_page+1}"))
    
    if buttons:
        keyboard.append(buttons)
    
    return InlineKeyboardMarkup(keyboard)


def get_phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура запроса телефона."""
    keyboard = [[KeyboardButton("📞 Поделиться номером", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
