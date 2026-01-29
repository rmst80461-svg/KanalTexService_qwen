"""Обработчики админ-панели для КаналТехСервис."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ..keyboards import Keyboards
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# States для рассылки
BROADCAST_MESSAGE = range(1)


class AdminHandler:
    """Класс для работы с админ-панелью."""

    def __init__(self, db, admin_ids: list):
        self.db = db
        self.admin_ids = admin_ids
        self.kb = Keyboards()

    def is_admin(self, user_id: int) -> bool:
        """Проверка является ли пользователь администратором."""
        return user_id in self.admin_ids

    async def show_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать статистику бота."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет доступа к этой функции.")
            return

        stats = self.db.get_statistics()
        
        orders_status_text = "\n".join(
            [f"  • {status}: {count}" for status, count in stats.get('orders_by_status', {}).items()]
        )

        text = (
            "📊 **Статистика КаналТехСервис**\n\n"
            f"👥 Всего пользователей: {stats.get('total_users', 0)}\n"
            f"🆕 Новых за неделю: {stats.get('new_users_week', 0)}\n\n"
            f"📋 Всего заказов: {stats.get('total_orders', 0)}\n"
            f"Заказы по статусам:\n{orders_status_text}\n\n"
            f"⭐ Средний рейтинг: {stats.get('avg_rating', 0)}\n"
            f"💬 Всего отзывов: {stats.get('total_reviews', 0)}"
        )

        await update.message.reply_text(text, parse_mode='Markdown')

    async def view_orders(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр заказов (с пагинацией)."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет доступа к этой функции.")
            return

        page = context.user_data.get('orders_page', 1)
        per_page = 10
        
        # Получаем новые заказы
        orders = self.db.get_orders_by_status('new', limit=per_page, offset=(page-1)*per_page)
        
        if not orders:
            await update.message.reply_text("✅ Нет новых заказов!")
            return

        text = f"📋 **Новые заказы** (страница {page}):\n\n"
        
        for order in orders:
            text += (
                f"🆔 Заказ #{order['order_id']:04d}\n"
                f"👤 Клиент: {order.get('first_name', 'Неизвестно')} (@{order.get('username', 'нет')})\n"
                f"📞 Телефон: {order.get('phone', 'не указан')}\n"
                f"🚰 Услуга: {order['category']}\n"
                f"📝 Описание: {order['description'][:50]}...\n"
                f"📅 Создан: {order['created_at']}\n"
                "―――――――――――\n"
            )

        # Считаем общее количество страниц
        total_orders = self.db.get_orders_count_by_status('new')
        total_pages = (total_orders + per_page - 1) // per_page

        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=self.kb.pagination_keyboard(page, total_pages, 'orders')
        )

    async def change_order_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Изменить статус заказа."""
        query = update.callback_query
        await query.answer()

        if not self.is_admin(update.effective_user.id):
            await query.edit_message_text("❌ У вас нет доступа к этой функции.")
            return

        # Парсим данные из callback
        parts = query.data.split('_')
        action = parts[1]  # accept, progress, complete, cancel
        order_id = int(parts[2])

        status_map = {
            'accept': ('accepted', '✅ Заказ принят в работу'),
            'progress': ('in_progress', '🔧 Заказ выполняется'),
            'complete': ('completed', '✔️ Заказ завершен'),
            'cancel': ('cancelled', '❌ Заказ отменен')
        }

        new_status, message = status_map.get(action, ('new', 'Статус обновлен'))
        
        # Обновляем статус в БД
        self.db.update_order_status(order_id, new_status)
        
        # Уведомляем клиента об изменении статуса
        order = self.db.get_order(order_id)
        if order:
            await self.notify_client_status_change(context, order['user_id'], order_id, new_status)

        await query.edit_message_text(f"{message} для заказа #{order_id:04d}")

    async def notify_client_status_change(self, context, user_id, order_id, new_status):
        """Уведомление клиента об изменении статуса заказа."""
        status_messages = {
            'accepted': '✅ Ваш заказ принят в работу!',
            'in_progress': '🔧 Специалист выехал на объект. Заказ выполняется.',
            'completed': '✔️ Заказ выполнен! Благодарим за обращение в КаналТехСервис!',
            'cancelled': '❌ К сожалению, ваш заказ был отменен. Свяжитесь с нами для уточнения деталей.'
        }

        message = status_messages.get(new_status, 'Статус вашего заказа обновлен')
        text = f"📋 Заказ #{order_id:04d}\n\n{message}"

        try:
            await context.bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            logger.error(f"Не удалось уведомить клиента {user_id}: {e}")

    async def view_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр списка пользователей."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет доступа к этой функции.")
            return

        page = context.user_data.get('users_page', 1)
        per_page = 15
        
        users = self.db.get_all_users(limit=per_page, offset=(page-1)*per_page)
        total_users = self.db.get_users_count()
        total_pages = (total_users + per_page - 1) // per_page

        text = f"👥 **Пользователи** (страница {page}/{total_pages}):\n\n"
        
        for user in users:
            text += (
                f"🆔 {user['user_id']}\n"
                f"👤 {user.get('first_name', '')} {user.get('last_name', '')}\n"
                f"📞 {user.get('phone', 'не указан')}\n"
                f"📦 Заказов: {user.get('total_orders', 0)}\n"
                f"📅 Регистрация: {user.get('registration_date', 'н/д')[:10]}\n"
                "―――――――――――\n"
            )

        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=self.kb.pagination_keyboard(page, total_pages, 'users')
        )

    async def start_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать создание рассылки."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет доступа к этой функции.")
            return ConversationHandler.END

        await update.message.reply_text(
            "📢 Создание рассылки\n\n"
            "Введите текст сообщения для рассылки всем пользователям:",
            reply_markup=self.kb.cancel_keyboard()
        )
        return BROADCAST_MESSAGE

    async def confirm_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение рассылки."""
        if update.message.text == "❌ Отменить":
            await update.message.reply_text(
                "❌ Создание рассылки отменено.",
                reply_markup=self.kb.admin_menu()
            )
            return ConversationHandler.END

        context.user_data['broadcast_message'] = update.message.text
        users_count = self.db.get_users_count()

        await update.message.reply_text(
            f"📢 Предпросмотр рассылки:\n\n{update.message.text}\n\n"
            f"Будет отправлено {users_count} пользователям.",
            reply_markup=self.kb.broadcast_confirm()
        )
        return BROADCAST_MESSAGE

    async def send_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отправка рассылки."""
        query = update.callback_query
        await query.answer()

        if query.data == "broadcast_cancel":
            await query.edit_message_text("❌ Рассылка отменена.")
            context.user_data.clear()
            return ConversationHandler.END

        message = context.user_data.get('broadcast_message')
        if not message:
            await query.edit_message_text("❌ Сообщение не найдено.")
            return ConversationHandler.END

        # Создаем запись о рассылке
        broadcast_id = self.db.create_broadcast(message)
        
        # Получаем всех пользователей
        users = self.db.get_all_users(limit=10000)
        
        sent = 0
        failed = 0

        await query.edit_message_text("📤 Отправка рассылки...")

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user['user_id'],
                    text=message
                )
                sent += 1
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение пользователю {user['user_id']}: {e}")
                failed += 1

        # Обновляем статистику рассылки
        self.db.update_broadcast_stats(broadcast_id, sent, failed)

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"✅ Рассылка завершена!\n\n✔️ Отправлено: {sent}\n❌ Ошибок: {failed}"
        )

        context.user_data.clear()
        return ConversationHandler.END

    async def check_pending_orders(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Проверка зависших заказов."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет доступа к этой функции.")
            return

        pending = self.db.get_pending_orders(hours=48)
        
        if not pending:
            await update.message.reply_text("✅ Зависших заказов не обнаружено!")
            return

        text = f"⚠️ **Зависшие заказы** ({len(pending)} шт.):\n\n"
        
        for order in pending:
            hours_passed = (datetime.now() - datetime.fromisoformat(order['updated_at'])).total_seconds() / 3600
            text += (
                f"🆔 Заказ #{order['order_id']:04d}\n"
                f"⏱ Без изменений: {int(hours_passed)} ч.\n"
                f"🚰 Услуга: {order['category']}\n"
                "―――――――――――\n"
            )

        await update.message.reply_text(text, parse_mode='Markdown')
