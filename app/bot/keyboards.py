"""Клавиатуры для Telegram бота ассенизаторских услуг."""
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
            [InlineKeyboardButton("🚽 Откачка септиков", callback_data="cat_septic")],
            [InlineKeyboardButton("🚰 Прочистка канализации", callback_data="cat_cleaning")],
            [InlineKeyboardButton("🔧 Ремонт септиков", callback_data="cat_repair")],
            [InlineKeyboardButton("📦 Установка септика", callback_data="cat_installation")],
            [InlineKeyboardButton("🔍 Диагностика", callback_data="cat_diagnostic")],
            [InlineKeyboardButton("🚚 Вывоз отходов", callback_data="cat_waste")],
            [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("✅ Принять", callback_data=f"order_accept_{order_id}")],
            [InlineKeyboardButton("🔧 В работе", callback_data=f"order_progress_{order_id}")],
            [InlineKeyboardButton("✔️ Завершен", callback_data=f"order_complete_{order_id}")],
            [InlineKeyboardButton("❌ Отменить", callback_data=f"order_cancel_{order_id}")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def pagination_keyboard(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
        keyboard = []
        nav_row = []
        if current_page > 1:
            nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"{prefix}_page_{current_page-1}"))
        nav_row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        if current_page < total_pages:
            nav_row.append(InlineKeyboardButton("➡️", callback_data=f"{prefix}_page_{current_page+1}"))
        keyboard.append(nav_row)
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def contact_request() -> ReplyKeyboardMarkup:
        keyboard = [[KeyboardButton("📱 Отправить номер", request_contact=True)]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def confirm_keyboard() -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_yes")],
            [InlineKeyboardButton("❌ Отмена", callback_data="confirm_no")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def rating_keyboard() -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("⭐", callback_data="rating_1"),
             InlineKeyboardButton("⭐⭐", callback_data="rating_2"),
             InlineKeyboardButton("⭐⭐⭐", callback_data="rating_3")],
            [InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rating_4"),
             InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rating_5")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def cancel_keyboard() -> ReplyKeyboardMarkup:
        keyboard = [["❌ Отменить"]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def skip_keyboard() -> InlineKeyboardMarkup:
        keyboard = [[InlineKeyboardButton("⏭ Пропустить", callback_data="skip")]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def faq_categories() -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("📋 Общие вопросы", callback_data="faq_general")],
            [InlineKeyboardButton("💰 Цены и оплата", callback_data="faq_pricing")],
            [InlineKeyboardButton("⏱ Сроки работы", callback_data="faq_timing")],
            [InlineKeyboardButton("🚚 Выезд и территория", callback_data="faq_area")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_main")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def my_orders_keyboard(orders: List[dict]) -> InlineKeyboardMarkup:
        keyboard = []
        for order in orders[:10]:
            status_emoji = {'new': '🆕', 'accepted': '✅', 'in_progress': '🔧',
                          'completed': '✔️', 'cancelled': '❌'}.get(order['status'], '❓')
            order_text = f"{status_emoji} #KTS-{order['order_id']:04d} - {order['service_type'][:20]}"
            keyboard.append([InlineKeyboardButton(order_text, callback_data=f"view_order_{order['order_id']}")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_main")])
        return InlineKeyboardMarkup(keyboard)
