"""Обработчики для работы с заказами ассенизаторских услуг."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ..keyboards import Keyboards
import logging

logger = logging.getLogger(__name__)

# States для ConversationHandler
SELECT_CATEGORY, ENTER_DESCRIPTION, SELECT_VOLUME, SELECT_URGENCY, ENTER_ADDRESS, CONFIRM_ORDER = range(6)


class OrderHandler:
    """Класс для обработки заказов."""

    def __init__(self, db):
        self.db = db
        self.kb = Keyboards()

    async def start_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало создания заказа."""
        await update.message.reply_text(
            "📋 Создание нового заказа\n\nВыберите тип услуги:",
            reply_markup=self.kb.order_categories()
        )
        return SELECT_CATEGORY

    async def select_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор категории заказа."""
        query = update.callback_query
        await query.answer()

        if query.data == "cancel":
            await query.edit_message_text("❌ Создание заказа отменено.")
            return ConversationHandler.END

        category_map = {
            "cat_septik": "Откачка септиков",
            "cat_vygrebnaya": "Очистка выгребных ям",
            "cat_kanalizaciya": "Прочистка канализации",
            "cat_promyvka": "Промывка труб высоким давлением",
            "cat_video": "Видеодиагностика труб",
            "cat_vyvoz": "Вывоз жидких отходов"
        }

        context.user_data['order_category'] = category_map.get(query.data, "Другое")
        
        await query.edit_message_text(
            f"✅ Выбрана услуга: {context.user_data['order_category']}\n\n"
            "📝 Опишите проблему или укажите дополнительные детали:",
            reply_markup=self.kb.cancel_keyboard()
        )
        return ENTER_DESCRIPTION

    async def enter_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ввод описания заказа."""
        if update.message.text == "❌ Отменить":
            await update.message.reply_text(
                "❌ Создание заказа отменено.",
                reply_markup=self.kb.main_menu()
            )
            return ConversationHandler.END

        context.user_data['order_description'] = update.message.text
        
        # Для откачки и вывоза спрашиваем объем
        category = context.user_data.get('order_category', '')
        if 'Откачка' in category or 'Вывоз' in category or 'выгребн' in category:
            await update.message.reply_text(
                "📏 Укажите примерный объем работ:",
                reply_markup=self.kb.volume_selection()
            )
            return SELECT_VOLUME
        else:
            return await self.ask_urgency(update, context)

    async def select_volume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор объема."""
        query = update.callback_query
        await query.answer()

        volume_map = {
            "vol_5": "До 5 м³",
            "vol_10": "5-10 м³",
            "vol_15": "10-15 м³",
            "vol_more": "Более 15 м³"
        }

        context.user_data['order_volume'] = volume_map.get(query.data, "Не указано")
        return await self.ask_urgency(update, context)

    async def ask_urgency(self, update, context):
        """Запрос срочности."""
        text = "⏰ Когда необходимо выполнить работы?"
        
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=self.kb.urgency_keyboard()
            )
        else:
            await update.message.reply_text(
                text,
                reply_markup=self.kb.urgency_keyboard()
            )
        return SELECT_URGENCY

    async def select_urgency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор срочности."""
        query = update.callback_query
        await query.answer()

        urgency_map = {
            "urgent_today": "Срочно (сегодня)",
            "urgent_tomorrow": "Завтра",
            "urgent_week": "В течение недели"
        }

        context.user_data['order_urgency'] = urgency_map.get(query.data, "Не указано")
        
        await query.edit_message_text(
            "📍 Укажите адрес объекта:\n\n"
            "Например: г. Москва, ул. Ленина, д. 10"
        )
        return ENTER_ADDRESS

    async def enter_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ввод адреса."""
        context.user_data['order_address'] = update.message.text
        return await self.confirm_order(update, context)

    async def confirm_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение заказа."""
        category = context.user_data.get('order_category', 'Не указано')
        description = context.user_data.get('order_description', 'Не указано')
        volume = context.user_data.get('order_volume', '')
        urgency = context.user_data.get('order_urgency', 'Не указано')
        address = context.user_data.get('order_address', 'Не указано')

        text = (
            "📋 Проверьте данные заказа:\n\n"
            f"🔧 Услуга: {category}\n"
            f"📝 Описание: {description}\n"
        )
        
        if volume:
            text += f"📏 Объем: {volume}\n"
        
        text += (
            f"⏰ Срочность: {urgency}\n"
            f"📍 Адрес: {address}\n\n"
            "Подтвердить создание заказа?"
        )

        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=self.kb.confirm_keyboard())
        else:
            await update.message.reply_text(text, reply_markup=self.kb.confirm_keyboard())
        
        return CONFIRM_ORDER

    async def finalize_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Финализация заказа."""
        query = update.callback_query
        await query.answer()

        if query.data == "confirm_no":
            await query.edit_message_text(
                "❌ Создание заказа отменено.",
                reply_markup=None
            )
            context.user_data.clear()
            return ConversationHandler.END

        # Создаем заказ в БД
        user_id = update.effective_user.id
        category = context.user_data.get('order_category')
        description = context.user_data.get('order_description')
        volume = context.user_data.get('order_volume', '')
        urgency = context.user_data.get('order_urgency')
        address = context.user_data.get('order_address')

        full_description = f"{description}\n\nОбъем: {volume}\nСрочность: {urgency}\nАдрес: {address}"

        order_id = self.db.create_order(
            user_id=user_id,
            service_type=category,
            category=category,
            description=full_description
        )

        await query.edit_message_text(
            f"✅ Заказ #{order_id:04d} успешно создан!\n\n"
            "Наш диспетчер свяжется с вами в ближайшее время для уточнения деталей.\n"
            "Вы можете отслеживать статус в разделе 'Мои заказы'.",
            reply_markup=None
        )

        # Уведомляем админов
        await self.notify_admins_new_order(context, order_id, user_id, category, full_description)

        context.user_data.clear()
        return ConversationHandler.END

    async def notify_admins_new_order(self, context, order_id, user_id, category, description):
        """Уведомление админов о новом заказе."""
        # TODO: Получить список админов из конфига
        admin_ids = []  # Заполнить из config
        
        text = (
            f"🆕 Новый заказ #{order_id:04d}\n\n"
            f"👤 Пользователь: {user_id}\n"
            f"🔧 Услуга: {category}\n"
            f"📋 Детали:\n{description}"
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
        """Просмотр заказов пользователя."""
        user_id = update.effective_user.id
        orders = self.db.get_user_orders(user_id)

        if not orders:
            await update.message.reply_text(
                "У вас пока нет заказов.\n\nСоздайте первый заказ!",
                reply_markup=self.kb.main_menu()
            )
            return

        await update.message.reply_text(
            "📦 Ваши заказы:\n\nВыберите заказ для просмотра деталей:",
            reply_markup=self.kb.my_orders_keyboard(orders)
        )

    async def view_order_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр деталей заказа."""
        query = update.callback_query
        await query.answer()

        order_id = int(query.data.split('_')[-1])
        order = self.db.get_order(order_id)

        if not order:
            await query.edit_message_text("❌ Заказ не найден.")
            return

        status_text = {
            'new': '🆕 Новый',
            'accepted': '✅ Принят',
            'in_progress': '🚗 Выехали на объект',
            'completed': '✔️ Завершен',
            'cancelled': '❌ Отменен'
        }.get(order['status'], '❓ Неизвестно')

        text = (
            f"📋 Заказ #{order['order_id']:04d}\n\n"
            f"Статус: {status_text}\n"
            f"Услуга: {order['category']}\n"
            f"Детали: {order['description']}\n"
            f"Создан: {order['created_at']}\n"
        )

        if order.get('price'):
            text += f"\n💰 Стоимость: {order['price']} руб."

        if order.get('admin_notes'):
            text += f"\n\n💬 Комментарий диспетчера: {order['admin_notes']}"

        await query.edit_message_text(text)

    async def cancel_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена операции."""
        await update.message.reply_text(
            "❌ Операция отменена.",
            reply_markup=self.kb.main_menu()
        )
        context.user_data.clear()
        return ConversationHandler.END
