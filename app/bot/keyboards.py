"""Клавиатуры для Telegram бота КаналТехСервис (адаптировано из ShveinyiHUB)."""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List


class Keyboards:
    """Класс для создания клавиатур."""

    @staticmethod
    def main_menu_inline() -> InlineKeyboardMarkup:
        """Главное меню (inline версия)."""
        keyboard = [
            [InlineKeyboardButton("➕ Новый заказ", callback_data="new_order")],
            [InlineKeyboardButton("🔍 Мои заказы", callback_data="check_status")],
            [InlineKeyboardButton("💰 Услуги и цены", callback_data="services")],
            [InlineKeyboardButton("❓ FAQ", callback_data="faq")],
            [InlineKeyboardButton("📞 Контакты", callback_data="contacts")],
            [InlineKeyboardButton("⭐ Оставить отзыв", callback_data="leave_review")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Главное меню (reply клавиатура)."""
        keyboard = [
            ["➕ Новый заказ", "🔍 Мои заказы"],
            ["💰 Услуги и цены", "❓ FAQ"],
            ["⭐ Оставить отзыв", "📞 Контакты"],
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @staticmethod
    def admin_menu() -> ReplyKeyboardMarkup:
        """Админ меню."""
        keyboard = [
            ["📊 Статистика", "📋 Заказы"],
            ["👥 Пользователи", "📢 Рассылка"],
            ["⚙️ Настройки", "◀️ Выйти"],
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @staticmethod
    def order_categories() -> InlineKeyboardMarkup:
        """Категории услуг для заказа (ассенизаторские)."""
        keyboard = [
            [InlineKeyboardButton("🚛 Вызов ассенизатора", callback_data="cat_assenizator")],
            [InlineKeyboardButton("🔧 Прочистка канализации", callback_data="cat_drain")],
            [InlineKeyboardButton("🚿 Прочистка септика", callback_data="cat_septic")],
            [InlineKeyboardButton("🔨 Вызов сантехника", callback_data="cat_plumber")],
            [InlineKeyboardButton("🚰 Установка сантехники", callback_data="cat_install")],
            [InlineKeyboardButton("❌ Отмена", callback_data="back_menu")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
        """Управление статусом заказа (для админов)."""
        keyboard = [
            [InlineKeyboardButton("✅ Принять", callback_data=f"order_accept_{order_id}")],
            [InlineKeyboardButton("🔄 В работу", callback_data=f"order_progress_{order_id}")],
            [InlineKeyboardButton("✅ Завершен", callback_data=f"order_complete_{order_id}")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"order_cancel_{order_id}")],
            [InlineKeyboardButton("◀️ Назад", callback_data="admin_orders")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def pagination_keyboard(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
        """Пагинация."""
        keyboard = []
        nav_row = []
        
        if current_page > 1:
            nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"{prefix}_page_{current_page-1}"))
        
        nav_row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages:
            nav_row.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"{prefix}_page_{current_page+1}"))
        
        keyboard.append(nav_row)
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_menu")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def contact_request() -> ReplyKeyboardMarkup:
        """Запрос контакта."""
        keyboard = [[KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def confirm_keyboard() -> InlineKeyboardMarkup:
        """Подтверждение действия."""
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_yes")],
            [InlineKeyboardButton("❌ Отмена", callback_data="confirm_no")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def rating_keyboard() -> InlineKeyboardMarkup:
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
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def cancel_keyboard() -> ReplyKeyboardMarkup:
        """Кнопка отмены."""
        keyboard = [["❌ Отменить"]]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    @staticmethod
    def skip_keyboard() -> InlineKeyboardMarkup:
        """Кнопка пропуска."""
        keyboard = [[InlineKeyboardButton("⏭ Пропустить", callback_data="skip")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def faq_categories() -> InlineKeyboardMarkup:
        """Категории FAQ для ассенизаторских услуг."""
        keyboard = [
            [InlineKeyboardButton("📋 Наши услуги", callback_data="faq_services")],
            [InlineKeyboardButton("💰 Цены и оплата", callback_data="faq_prices")],
            [InlineKeyboardButton("⏱ Сроки выполнения", callback_data="faq_timing")],
            [InlineKeyboardButton("📍 Адрес и график", callback_data="faq_location")],
            [InlineKeyboardButton("❓ Другой вопрос", callback_data="faq_other")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_menu")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def prices_menu() -> InlineKeyboardMarkup:
        """Меню цен на услуги."""
        keyboard = [
            [InlineKeyboardButton("🚛 Вызов ассенизатора", callback_data="price_assenizator")],
            [InlineKeyboardButton("🔧 Прочистка канализации", callback_data="price_drain")],
            [InlineKeyboardButton("🚿 Прочистка септика", callback_data="price_septic")],
            [InlineKeyboardButton("🔨 Вызов сантехника", callback_data="price_plumber")],
            [InlineKeyboardButton("🚰 Установка сантехники", callback_data="price_install")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_menu")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def broadcast_confirm() -> InlineKeyboardMarkup:
        """Подтверждение рассылки."""
        keyboard = [
            [InlineKeyboardButton("✅ Отправить всем", callback_data="broadcast_send")],
            [InlineKeyboardButton("❌ Отменить", callback_data="broadcast_cancel")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def back_button() -> InlineKeyboardMarkup:
        """Кнопка 'Назад'."""
        keyboard = [[InlineKeyboardButton("◀️ Назад в меню", callback_data="back_menu")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def my_orders_keyboard(orders: List[dict]) -> InlineKeyboardMarkup:
        """Список заказов пользователя."""
        keyboard = []
        for order in orders[:10]:
            status_emoji = {
                'new': '🆕',
                'accepted': '✅',
                'in_progress': '🔄',
                'completed': '✅',
                'cancelled': '❌'
            }.get(order['status'], '❓')
            
            order_text = f"{status_emoji} Заказ #{order['order_id']:04d} - {order['service_type']}"
            keyboard.append([InlineKeyboardButton(order_text, callback_data=f"view_order_{order['order_id']}")])
        
        keyboard.append([InlineKeyboardButton("◀️ Главное меню", callback_data="back_menu")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
