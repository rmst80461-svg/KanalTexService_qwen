"""Клавиатуры для Telegram бота швейной мастерской."""
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from typing import List


# === ГЛАВНОЕ МЕНЮ ===
def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота."""
    keyboard = [
        ["📋 Новый заказ", "📦 Мои заказы"],
        ["💰 Цены", "❓ FAQ"],
        ["⭐ Оставить отзыв", "📞 Контакты"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# === АДМИН МЕНЮ ===
def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Меню администратора."""
    keyboard = [
        ["📊 Статистика", "📋 Заказы"],
        ["👥 Пользователи", "📢 Рассылка"],
        ["💰 Управление ценами", "❓ Управление FAQ"],
        ["🔙 Выход из админ-панели"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# === КАТЕГОРИИ УСЛУГ ===
def get_service_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора категории услуг."""
    keyboard = [
        [InlineKeyboardButton("👗 Ремонт одежды", callback_data="cat_repair")],
        [InlineKeyboardButton("✂️ Пошив одежды", callback_data="cat_sewing")],
        [InlineKeyboardButton("🎨 Декор и украшение", callback_data="cat_decor")],
        [InlineKeyboardButton("🧵 Подгонка по фигуре", callback_data="cat_fitting")],
        [InlineKeyboardButton("🔙 Назад", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === СТАТУСЫ ЗАКАЗОВ ===
def get_order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура управления статусом заказа."""
    keyboard = [
        [InlineKeyboardButton("✅ Принят в работу", callback_data=f"status_{order_id}_in_progress")],
        [InlineKeyboardButton("⏰ Ожидает клиента", callback_data=f"status_{order_id}_waiting_client")],
        [InlineKeyboardButton("🎉 Завершен", callback_data=f"status_{order_id}_completed")],
        [InlineKeyboardButton("❌ Отменен", callback_data=f"status_{order_id}_cancelled")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"order_details_{order_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === ПРОСМОТР ЗАКАЗОВ ===
def get_orders_filter_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура фильтрации заказов."""
    keyboard = [
        [InlineKeyboardButton("🆕 Новые", callback_data="filter_new")],
        [InlineKeyboardButton("⏳ В работе", callback_data="filter_in_progress")],
        [InlineKeyboardButton("⏰ Ожидают клиента", callback_data="filter_waiting_client")],
        [InlineKeyboardButton("✅ Завершенные", callback_data="filter_completed")],
        [InlineKeyboardButton("📋 Все заказы", callback_data="filter_all")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === ПАГИНАЦИЯ ===
def get_pagination_keyboard(page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура пагинации."""
    keyboard = []
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"{prefix}_page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="current_page"))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"{prefix}_page_{page+1}"))
    
    keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_menu")])
    
    return InlineKeyboardMarkup(keyboard)


# === ДЕТАЛИ ЗАКАЗА ===
def get_order_details_keyboard(order_id: int, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура деталей заказа."""
    keyboard = []
    
    if is_admin:
        keyboard.append([InlineKeyboardButton("✏️ Изменить статус", callback_data=f"change_status_{order_id}")])
        keyboard.append([InlineKeyboardButton("💬 Добавить заметку", callback_data=f"add_note_{order_id}")])
    else:
        keyboard.append([InlineKeyboardButton("❌ Отменить заказ", callback_data=f"cancel_order_{order_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="my_orders" if not is_admin else "orders_list")])
    
    return InlineKeyboardMarkup(keyboard)


# === РЕЙТИНГ ===
def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора рейтинга."""
    keyboard = [
        [
            InlineKeyboardButton("⭐", callback_data="rating_1"),
            InlineKeyboardButton("⭐⭐", callback_data="rating_2"),
            InlineKeyboardButton("⭐⭐⭐", callback_data="rating_3"),
        ],
        [
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rating_4"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rating_5"),
        ],
        [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === ПОДТВЕРЖДЕНИЕ ===
def get_confirmation_keyboard(action: str, item_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия."""
    callback_yes = f"confirm_{action}_{item_id}" if item_id else f"confirm_{action}"
    callback_no = f"cancel_{action}_{item_id}" if item_id else f"cancel_{action}"
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=callback_yes),
            InlineKeyboardButton("❌ Нет", callback_data=callback_no)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# === РАССЫЛКА ===
def get_broadcast_keyboard(broadcast_id: int) -> InlineKeyboardMarkup:
    """Клавиатура управления рассылкой."""
    keyboard = [
        [InlineKeyboardButton("📤 Отправить всем", callback_data=f"broadcast_send_{broadcast_id}")],
        [InlineKeyboardButton("✏️ Редактировать", callback_data=f"broadcast_edit_{broadcast_id}")],
        [InlineKeyboardButton("❌ Удалить", callback_data=f"broadcast_delete_{broadcast_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === FAQ КАТЕГОРИИ ===
def get_faq_categories_keyboard(categories: List[str]) -> InlineKeyboardMarkup:
    """Клавиатура категорий FAQ."""
    keyboard = []
    
    for category in categories:
        keyboard.append([InlineKeyboardButton(category, callback_data=f"faq_cat_{category}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


# === КОНТАКТ (ЗАПРОС ТЕЛЕФОНА) ===
def get_phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура запроса номера телефона."""
    keyboard = [
        [KeyboardButton("📱 Отправить номер телефона", request_contact=True)],
        ["🔙 Отмена"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


# === ПРОПУСТИТЬ ШАГ ===
def get_skip_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой пропуска."""
    keyboard = [["⏭ Пропустить"], ["🔙 Отмена"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


# === СПИСОК ПОЛЬЗОВАТЕЛЕЙ ===
def get_user_details_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура деталей пользователя."""
    keyboard = [
        [InlineKeyboardButton("📋 Заказы пользователя", callback_data=f"user_orders_{user_id}")],
        [InlineKeyboardButton("📢 Отправить сообщение", callback_data=f"message_user_{user_id}")],
        [InlineKeyboardButton("🚫 Заблокировать", callback_data=f"block_user_{user_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="users_list")]
    ]
    return InlineKeyboardMarkup(keyboard)
