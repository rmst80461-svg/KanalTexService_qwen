"""Клавиатуры для Telegram бота КаналТехСервис."""
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from typing import List


class Keyboards:
    """Класс для создания клавиатур."""

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Главное меню."""
        keyboard = [
            ["📋 Новый заказ", "📦 Мои заказы"],
            ["💰 Прайс-лист", "❓ FAQ"],
            ["⭐ Оставить отзыв", "📞 Контакты"],
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def admin_menu() -> ReplyKeyboardMarkup:
        """Админ меню."""
        keyboard = [
            ["📊 Статистика", "📋 Заказы"],
            ["👥 Пользователи", "📢 Рассылка"],
            ["⚙️ Настройки", "🔙 Выход"],
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def order_categories() -> InlineKeyboardMarkup:
        """Категории услуг для заказа."""
        keyboard = [
            [InlineKeyboardButton("🚰 Откачка септиков", callback_data="cat_septic")],
            [InlineKeyboardButton("🔧 Прочистка канализации", callback_data="cat_cleaning")],
            [InlineKeyboardButton("🚨 Устранение засоров", callback_data="cat_blockage")],
            [InlineKeyboardButton("🏗️ Монтаж септиков", callback_data="cat_installation")],
            [InlineKeyboardButton("🔍 Диагностика системы", callback_data="cat_diagnostics")],
            [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
        """Клавиатура для управления статусом заказа."""
        keyboard = [
            [InlineKeyboardButton("✅ Принять", callback_data=f"order_accept_{order_id}")],
            [InlineKeyboardButton("🔧 В работе", callback_data=f"order_progress_{order_id}")],
            [InlineKeyboardButton("✔️ Завершен", callback_data=f"order_complete_{order_id}")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"order_cancel_{order_id}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_orders")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def pagination_keyboard(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
        """Клавиатура пагинации."""
        keyboard = []
        nav_row = []
        
        if current_page > 1:
            nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"{prefix}_page_{current_page-1}"))
        
        nav_row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages:
            nav_row.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"{prefix}_page_{current_page+1}"))
        
        keyboard.append(nav_row)
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def contact_request() -> ReplyKeyboardMarkup:
        """Запрос контакта."""
        keyboard = [[KeyboardButton("📱 Отправить номер телефона", request_contact=True)]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def confirm_keyboard() -> InlineKeyboardMarkup:
        """Подтверждение действия."""
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_yes")],
            [InlineKeyboardButton("❌ Отмена", callback_data="confirm_no")],
        ]
        return InlineKeyboardMarkup(keyboard)

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
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def cancel_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура отмены."""
        keyboard = [["❌ Отменить"]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def skip_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура пропуска."""
        keyboard = [[InlineKeyboardButton("⏭ Пропустить", callback_data="skip")]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def faq_categories() -> InlineKeyboardMarkup:
        """Категории FAQ."""
        keyboard = [
            [InlineKeyboardButton("📋 Общие вопросы", callback_data="faq_general")],
            [InlineKeyboardButton("💰 Цены и оплата", callback_data="faq_pricing")],
            [InlineKeyboardButton("⏱ Сроки выполнения", callback_data="faq_timing")],
            [InlineKeyboardButton("🚗 Выезд и график", callback_data="faq_schedule")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_main")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def broadcast_confirm() -> InlineKeyboardMarkup:
        """Подтверждение рассылки."""
        keyboard = [
            [InlineKeyboardButton("✅ Отправить всем", callback_data="broadcast_send")],
            [InlineKeyboardButton("❌ Отменить", callback_data="broadcast_cancel")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def my_orders_keyboard(orders: List[dict]) -> InlineKeyboardMarkup:
        """Клавиатура со списком заказов пользователя."""
        keyboard = []
        for order in orders[:10]:  # Показываем до 10 заказов
            status_emoji = {
                'new': '🆕',
                'accepted': '✅',
                'in_progress': '🔧',
                'completed': '✔️',
                'cancelled': '❌'
            }.get(order['status'], '❓')
            
            order_text = f"{status_emoji} Заказ #{order['order_id']:04d} - {order['service_type']}"
            keyboard.append([InlineKeyboardButton(order_text, callback_data=f"view_order_{order['order_id']}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="back_main")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def price_categories() -> InlineKeyboardMarkup:
        """Категории прайс-листа."""
        keyboard = [
            [InlineKeyboardButton("🚰 Откачка септиков", callback_data="price_septic")],
            [InlineKeyboardButton("🔧 Прочистка канализации", callback_data="price_cleaning")],
            [InlineKeyboardButton("🚨 Устранение засоров", callback_data="price_blockage")],
            [InlineKeyboardButton("🏗️ Монтаж септиков", callback_data="price_installation")],
            [InlineKeyboardButton("🔍 Диагностика", callback_data="price_diagnostics")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="back_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
