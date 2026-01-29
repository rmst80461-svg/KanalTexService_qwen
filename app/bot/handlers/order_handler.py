"""Обработчики для работы с заказами ассенизаторских услуг."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ..keyboards import Keyboards
import logging

logger = logging.getLogger(__name__)

# States для ConversationHandler
SELECT_CATEGORY, ENTER_DESCRIPTION, UPLOAD_PHOTO, ENTER_ADDRESS, CONFIRM_ORDER = range(5)


class OrderHandler:
    """Класс для обработки заказов."""

    def __init__(self, db):
        self.db = db
        self.kb = Keyboards()

    async def start_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало создания заказа."""
        await update.message.reply_text(
            "📋 Создание нового заказа\n\nВыберите необходимую услугу:",
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
            "cat_septic": "Откачка септиков",
            "cat_cleaning": "Прочистка канализации",
            "cat_blockage": "Устранение засоров",
            "cat_installation": "Монтаж септиков",
            "cat_diagnostics": "Диагностика системы"
        }

        context.user_data['order_category'] = category_map.get(query.data, "Другое")
        
        await query.edit_message_text(
            f"✅ Выбрана услуга: {context.user_data['order_category']}\n\n"
            "📍 Укажите адрес объекта:",
            reply_markup=self.kb.cancel_keyboard()
        )
        return ENTER_ADDRESS

    async def enter_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ввод адреса объекта."""
        if update.message.text == "❌ Отменить":
            await update.message.reply_text(
                "❌ Создание заказа отменено.",
                reply_markup=self.kb.main_menu()
            )
            return ConversationHandler.END

        context.user_data['order_address'] = update.message.text
        
        await update.message.reply_text(
            "📝 Опишите детали заказа:\n"
            "- Объем септика (если применимо)\n"
            "- Степень засора\n"
            "- Дополнительные пожелания",
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
        
        await update.message.reply_text(
            "📸 Можете отправить фото проблемы (или нажмите 'Пропустить'):",
            reply_markup=self.kb.skip_keyboard()
        )
        return UPLOAD_PHOTO

    async def upload_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Загрузка фото к заказу."""
        if update.callback_query and update.callback_query.data == "skip":
            await update.callback_query.answer()
            context.user_data['order_photo'] = None
            return await self.confirm_order(update, context)

        if update.message.photo:
            context.user_data['order_photo'] = update.message.photo[-1].file_id
            
        return await self.confirm_order(update, context)

    async def confirm_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение заказа."""
        category = context.user_data.get('order_category', 'Не указано')
        address = context.user_data.get('order_address', 'Не указано')
        description = context.user_data.get('order_description', 'Не указано')
        has_photo = "Да" if context.user_data.get('order_photo') else "Нет"

        text = (
            "📋 Проверьте данные заказа:\n\n"
            f"🚰 Услуга: {category}\n"
            f"📍 Адрес: {address}\n"
            f"📝 Описание: {description}\n"
            f"📸 Фото: {has_photo}\n\n"
            "Подтвердить создание заказа?"
        )

        if update.callback_query:
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
        address = context.user_data.get('order_address')
        description = f"Адрес: {address}\n{context.user_data.get('order_description', '')}"
        photo = context.user_data.get('order_photo')

        order_id = self.db.create_order(
            user_id=user_id,
            service_type=category,
            category=category,
            description=description,
            photo_path=photo
        )

        await query.edit_message_text(
            f"✅ Заказ #{order_id:04d} успешно создан!\n\n"
            "📞 Наш диспетчер свяжется с вами в ближайшее время для уточнения деталей и назначения времени выезда.\n\n"
            "Вы можете отслеживать статус в разделе '📦 Мои заказы'.",
            reply_markup=None
        )

        # Уведомляем админов
        await self.notify_admins_new_order(context, order_id, user_id, category, description)

        context.user_data.clear()
        return ConversationHandler.END

    async def notify_admins_new_order(self, context, order_id, user_id, category, description):
        """Уведомление админов о новом заказе."""
        # TODO: Получить список админов из конфига
        admin_ids = []  # Заполнить из config
        
        text = (
            f"🆕 Новый заказ #{order_id:04d}\n\n"
            f"👤 Пользователь: {user_id}\n"
            f"🚰 Услуга: {category}\n"
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
            'in_progress': '🔧 Выполняется',
            'completed': '✔️ Завершен',
            'cancelled': '❌ Отменен'
        }.get(order['status'], '❓ Неизвестно')

        text = (
            f"📋 Заказ #{order['order_id']:04d}\n\n"
            f"Статус: {status_text}\n"
            f"Услуга: {order['category']}\n"
            f"Описание: {order['description']}\n"
            f"Создан: {order['created_at']}\n"
        )

        if order.get('price'):
            text += f"💰 Стоимость: {order['price']} руб.\n"

        if order.get('admin_notes'):
            text += f"\n💬 Комментарий мастера: {order['admin_notes']}"

        await query.edit_message_text(text)

    async def cancel_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена операции."""
        await update.message.reply_text(
            "❌ Операция отменена.",
            reply_markup=self.kb.main_menu()
        )
        context.user_data.clear()
        return ConversationHandler.END
