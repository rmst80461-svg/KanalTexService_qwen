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
        """Категории ассенизаторских услуг."""
        keyboard = [
            [InlineKeyboardButton("🚽 Откачка септиков", callback_data="cat_septik")],
            [InlineKeyboardButton("🕳 Очистка выгребных ям", callback_data="cat_vygrebnaya")],
            [InlineKeyboardButton("🔧 Прочистка канализации", callback_data="cat_kanalizaciya")],
            [InlineKeyboardButton("🚿 Промывка труб высоким давлением", callback_data="cat_promyvka")],
            [InlineKeyboardButton("🔍 Видеодиагностика труб", callback_data="cat_video")],
            [InlineKeyboardButton("🚛 Вывоз жидких отходов", callback_data="cat_vyvoz")],
            [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
        """Клавиатура для управления статусом заказа."""
        keyboard = [
            [InlineKeyboardButton("✅ Принять", callback_data=f"order_accept_{order_id}")],
            [InlineKeyboardButton("🚗 Выехали на объект", callback_data=f"order_progress_{order_id}")],
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
            [InlineKeyboardButton("🚗 График работы", callback_data="faq_schedule")],
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
        for order in orders[:10]:
            status_emoji = {
                'new': '🆕',
                'accepted': '✅',
                'in_progress': '🚗',
                'completed': '✔️',
                'cancelled': '❌'
            }.get(order['status'], '❓')
            
            order_text = f"{status_emoji} Заказ #{order['order_id']:04d} - {order['service_type']}"
            keyboard.append([InlineKeyboardButton(order_text, callback_data=f"view_order_{order['order_id']}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="back_main")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def volume_selection() -> InlineKeyboardMarkup:
        """Выбор объема для откачки."""
        keyboard = [
            [InlineKeyboardButton("До 5 м³", callback_data="vol_5")],
            [InlineKeyboardButton("5-10 м³", callback_data="vol_10")],
            [InlineKeyboardButton("10-15 м³", callback_data="vol_15")],
            [InlineKeyboardButton("Более 15 м³", callback_data="vol_more")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def urgency_keyboard() -> InlineKeyboardMarkup:
        """Срочность заказа."""
        keyboard = [
            [InlineKeyboardButton("🔴 Срочно (сегодня)", callback_data="urgent_today")],
            [InlineKeyboardButton("🟡 Завтра", callback_data="urgent_tomorrow")],
            [InlineKeyboardButton("🟢 В течение недели", callback_data="urgent_week")],
        ]
        return InlineKeyboardMarkup(keyboard)
