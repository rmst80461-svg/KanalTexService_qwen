"""Обработчики для работы с заявками."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ..keyboards import Keyboards
import logging

logger = logging.getLogger(__name__)

# States для ConversationHandler
SELECT_CATEGORY, ENTER_ADDRESS, ENTER_DESCRIPTION, SELECT_URGENCY, CONFIRM_ORDER = range(5)


class OrderHandler:
    """Класс для обработки заявок."""

    def __init__(self, db):
        self.db = db
        self.kb = Keyboards()

    async def start_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало создания заявки."""
        await update.message.reply_text(
            "📋 Создание новой заявки\n\nВыберите тип услуги:",
            reply_markup=self.kb.order_categories()
        )
        return SELECT_CATEGORY

    async def select_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор категории заявки."""
        query = update.callback_query
        await query.answer()

        if query.data == "cancel":
            await query.edit_message_text("❌ Создание заявки отменено.")
            return ConversationHandler.END

        category_map = {
            "cat_septic": "Выкачка септиков и выгребных ям",
            "cat_cleaning": "Прочистка канализации",
            "cat_blockage": "Устранение засоров",
            "cat_repair": "Ремонт канализационных систем",
            "cat_video": "Видеодиагностика труб",
            "cat_install": "Монтаж канализационных систем"
        }

        context.user_data['order_category'] = category_map.get(query.data, "Другое")
        
        await query.edit_message_text(
            f"✅ Выбрана услуга: {context.user_data['order_category']}\n\n"
            "📍 Теперь укажите адрес объекта:",
            reply_markup=self.kb.location_request()
        )
        return ENTER_ADDRESS

    async def enter_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ввод адреса объекта."""
        if update.message.location:
            # Получена геолокация
            lat = update.message.location.latitude
            lon = update.message.location.longitude
            context.user_data['order_address'] = f"Координаты: {lat}, {lon}"
            context.user_data['order_location'] = {'lat': lat, 'lon': lon}
        elif update.message.text and update.message.text != "❌ Отменить":
            if update.message.text == "✏️ Ввести адрес вручную":
                await update.message.reply_text(
                    "Введите адрес текстом (улица, дом, корпус):",
                    reply_markup=self.kb.cancel_keyboard()
                )
                return ENTER_ADDRESS
            context.user_data['order_address'] = update.message.text
        elif update.message.text == "❌ Отменить":
            await update.message.reply_text(
                "❌ Создание заявки отменено.",
                reply_markup=self.kb.main_menu()
            )
            return ConversationHandler.END
        
        await update.message.reply_text(
            "📝 Опишите проблему или детали работы:",
            reply_markup=self.kb.cancel_keyboard()
        )
        return ENTER_DESCRIPTION

    async def enter_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ввод описания заявки."""
        if update.message.text == "❌ Отменить":
            await update.message.reply_text(
                "❌ Создание заявки отменено.",
                reply_markup=self.kb.main_menu()
            )
            return ConversationHandler.END

        context.user_data['order_description'] = update.message.text
        
        await update.message.reply_text(
            "⏰ Когда нужно выполнить работу?",
            reply_markup=self.kb.urgency_keyboard()
        )
        return SELECT_URGENCY

    async def select_urgency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор срочности."""
        query = update.callback_query
        await query.answer()

        urgency_map = {
            "urgency_urgent": "Срочно (в течение часа)",
            "urgency_today": "Сегодня",
            "urgency_tomorrow": "Завтра",
            "urgency_scheduled": "По согласованию"
        }

        context.user_data['order_urgency'] = urgency_map.get(query.data, "Не указано")
        
        return await self.confirm_order(update, context)

    async def confirm_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение заявки."""
        category = context.user_data.get('order_category', 'Не указано')
        address = context.user_data.get('order_address', 'Не указано')
        description = context.user_data.get('order_description', 'Не указано')
        urgency = context.user_data.get('order_urgency', 'Не указано')

        text = (
            "📋 Проверьте данные заявки:\n\n"
            f"🔧 Услуга: {category}\n"
            f"📍 Адрес: {address}\n"
            f"📝 Описание: {description}\n"
            f"⏰ Срочность: {urgency}\n\n"
            "Подтвердить создание заявки?"
        )

        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=self.kb.confirm_keyboard())
        else:
            await update.message.reply_text(text, reply_markup=self.kb.confirm_keyboard())
        
        return CONFIRM_ORDER

    async def finalize_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Финализация заявки."""
        query = update.callback_query
        await query.answer()

        if query.data == "confirm_no":
            await query.edit_message_text(
                "❌ Создание заявки отменено.",
                reply_markup=None
            )
            context.user_data.clear()
            return ConversationHandler.END

        # Создаем заявку в БД
        user_id = update.effective_user.id
        category = context.user_data.get('order_category')
        address = context.user_data.get('order_address')
        description = context.user_data.get('order_description')
        urgency = context.user_data.get('order_urgency')

        # Формируем полное описание
        full_description = f"{description}\n\nАдрес: {address}\nСрочность: {urgency}"

        order_id = self.db.create_order(
            user_id=user_id,
            service_type=category,
            category=category,
            description=full_description
        )

        await query.edit_message_text(
            f"✅ Заявка №{order_id:04d} успешно создана!\n\n"
            "Наш диспетчер свяжется с вами в ближайшее время для уточнения деталей.\n\n"
            "📞 Телефон: +7 (XXX) XXX-XX-XX\n"
            "Вы можете отслеживать статус в разделе 'Мои заявки'.",
            reply_markup=None
        )

        # Уведомляем админов
        await self.notify_admins_new_order(context, order_id, user_id, category, full_description)

        context.user_data.clear()
        return ConversationHandler.END

    async def notify_admins_new_order(self, context, order_id, user_id, category, description):
        """Уведомление админов о новой заявке."""
        # TODO: Получить список админов из конфига
        admin_ids = []  # Заполнить из config
        
        user = self.db.get_user(user_id)
        user_info = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or f"ID: {user_id}"
        if user.get('phone'):
            user_info += f" | {user['phone']}"

        text = (
            f"🆕 Новая заявка #{order_id:04d}\n\n"
            f"👤 Клиент: {user_info}\n"
            f"🔧 Услуга: {category}\n"
            f"📝 Описание: {description}"
        )

        for admin_id in admin_ids:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    reply_markup=self.kb.order_status_keyboard(order_id)
                )
            except Exception as e:
                logger.error(f"Не удалось уведомить админа {admin_id}: {e}")

    async def view_my_orders(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр заявок пользователя."""
        user_id = update.effective_user.id
        orders = self.db.get_user_orders(user_id)

        if not orders:
            await update.message.reply_text(
                "У вас пока нет заявок.\n\nСоздайте первую заявку!",
                reply_markup=self.kb.main_menu()
            )
            return

        await update.message.reply_text(
            "📦 Ваши заявки:\n\nВыберите заявку для просмотра деталей:",
            reply_markup=self.kb.my_orders_keyboard(orders)
        )

    async def view_order_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр деталей заявки."""
        query = update.callback_query
        await query.answer()

        order_id = int(query.data.split('_')[-1])
        order = self.db.get_order(order_id)

        if not order:
            await query.edit_message_text("❌ Заявка не найдена.")
            return

        status_text = {
            'new': '🆕 Новая',
            'accepted': '✅ Принята',
            'dispatched': '🚗 Бригада выехала',
            'in_progress': '🔧 В работе',
            'completed': '✔️ Завершена',
            'cancelled': '❌ Отменена'
        }.get(order['status'], '❓ Неизвестно')

        text = (
            f"📋 Заявка #{order['order_id']:04d}\n\n"
            f"Статус: {status_text}\n"
            f"Услуга: {order['category']}\n"
            f"Описание: {order['description']}\n"
            f"Создана: {order['created_at']}\n"
        )

        if order.get('price'):
            text += f"\n💰 Стоимость: {order['price']} руб."

        if order.get('admin_notes'):
            text += f"\n\n💬 Комментарий мастера: {order['admin_notes']}"

        await query.edit_message_text(text)

    async def cancel_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена операции."""
        await update.message.reply_text(
            "❌ Операция отменена.",
            reply_markup=self.kb.main_menu()
        )
        context.user_data.clear()
        return ConversationHandler.END
