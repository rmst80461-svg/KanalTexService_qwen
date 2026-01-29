"""Клавиатуры для Telegram бота ассенизаторских услуг."""
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from typing import List


def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню."""
    keyboard = [
        [InlineKeyboardButton("📋 Новый заказ", callback_data="new_order")],
        [InlineKeyboardButton("💰 Услуги и цены", callback_data="services")],
        [InlineKeyboardButton("🔍 Статус заказа", callback_data="check_status")],
        [InlineKeyboardButton("❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contacts")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_main_menu() -> ReplyKeyboardMarkup:
    """Админ меню."""
    keyboard = [
        ["📈 Статистика", "📊 Все заказы"],
        ["👥 Пользователи", "📢 Рассылка"],
        ["❌ Удалить спам", "◀️ Выйти"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_prices_menu() -> InlineKeyboardMarkup:
    """Меню услуг и цен."""
    keyboard = [
        [InlineKeyboardButton("🚛 Откачка септиков", callback_data="price_septic")],
        [InlineKeyboardButton("🔧 Прочистка канализации", callback_data="price_cleaning")],
        [InlineKeyboardButton("🛠 Ремонт труб", callback_data="price_repair")],
        [InlineKeyboardButton("📹 Видеодиагностика", callback_data="price_video")],
        [InlineKeyboardButton("🏗 Монтаж систем", callback_data="price_installation")],
        [InlineKeyboardButton("🧪 Химическая очистка", callback_data="price_chemical")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_service_selection() -> InlineKeyboardMarkup:
    """Выбор услуги при создании заказа."""
    keyboard = [
        [InlineKeyboardButton("🚛 Откачка септика/выгребной ямы", callback_data="service_septic")],
        [InlineKeyboardButton("🔧 Прочистка канализации", callback_data="service_cleaning")],
        [InlineKeyboardButton("🛠 Ремонт канализационных труб", callback_data="service_repair")],
        [InlineKeyboardButton("📹 Видеодиагностика", callback_data="service_video")],
        [InlineKeyboardButton("🏗 Монтаж канализации", callback_data="service_installation")],
        [InlineKeyboardButton("🧪 Химочистка труб", callback_data="service_chemical")],
        [InlineKeyboardButton("🆘 Аварийный выезд", callback_data="service_emergency")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для управления статусом заказа (админ)."""
    keyboard = [
        [InlineKeyboardButton("✅ Принять", callback_data=f"status_accepted_{order_id}")],
        [InlineKeyboardButton("🔄 В работе", callback_data=f"status_in_progress_{order_id}")],
        [InlineKeyboardButton("✔️ Завершен", callback_data=f"status_completed_{order_id}")],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"status_cancelled_{order_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="olist_all_1")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_skip_button() -> InlineKeyboardMarkup:
    """Кнопка пропуска."""
    keyboard = [[InlineKeyboardButton("⏭ Пропустить", callback_data="skip_photo")]]
    return InlineKeyboardMarkup(keyboard)


def get_skip_description_button() -> InlineKeyboardMarkup:
    """Кнопка пропуска описания."""
    keyboard = [[InlineKeyboardButton("⏭ Пропустить", callback_data="skip_description")]]
    return InlineKeyboardMarkup(keyboard)


def get_name_keyboard(first_name: str) -> InlineKeyboardMarkup:
    """Клавиатура с предложением использовать имя из Telegram."""
    keyboard = [
        [InlineKeyboardButton(f"✅ Использовать '{first_name}'", callback_data="use_tg_name")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_phone_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для пропуска телефона."""
    keyboard = [
        [InlineKeyboardButton("⏭ Пропустить", callback_data="skip_phone")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение заказа."""
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_order")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для оценки."""
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
        [InlineKeyboardButton("⏭ Пропустить", callback_data="skip_review")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_faq_menu() -> InlineKeyboardMarkup:
    """Категории FAQ."""
    keyboard = [
        [InlineKeyboardButton("📋 Какие услуги", callback_data="faq_services")],
        [InlineKeyboardButton("💰 Цены", callback_data="faq_prices")],
        [InlineKeyboardButton("⏰ Сроки работы", callback_data="faq_timing")],
        [InlineKeyboardButton("📍 Район работы", callback_data="faq_location")],
        [InlineKeyboardButton("💳 Оплата", callback_data="faq_payment")],
        [InlineKeyboardButton("📝 Как заказать", callback_data="faq_order")],
        [InlineKeyboardButton("❓ Другой вопрос", callback_data="faq_other")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка 'Назад'."""
    keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="back_menu")]]
    return InlineKeyboardMarkup(keyboard)


def get_broadcast_preview_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для предпросмотра рассылки."""
    keyboard = [
        [InlineKeyboardButton("✅ Отправить всем", callback_data="broadcast_confirm")],
        [InlineKeyboardButton("✏️ Изменить", callback_data="broadcast_edit")],
        [InlineKeyboardButton("❌ Отмена", callback_data="broadcast_cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_button() -> InlineKeyboardMarkup:
    """Кнопка отмены."""
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="cancel_order")]]
    return InlineKeyboardMarkup(keyboard)
