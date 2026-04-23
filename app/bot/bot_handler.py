"""
Главный обработчик Telegram бота КаналТехСервис (структура ShveinyiHUB)
"""
import logging
import os
import asyncio
from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.database import Database

from .keyboards import (
    get_main_menu,
    get_persistent_menu,
    get_services_menu,
    get_prices_menu,
    get_faq_menu,
    get_back_button,
    get_ai_chat_keyboard,
    get_admin_main_menu,
    get_admin_order_detail_keyboard,
    get_admin_orders_submenu,
    remove_keyboard,
    get_skip_comment_keyboard,
    get_cancel_order_keyboard,
    get_confirm_order_keyboard
)
from .ai_helper import get_ai_response

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram бот КаналТехСервис с адаптацией структуры ShveinyiHUB."""

    def __init__(self, db: 'Database'):
        from app.config import BOT_TOKEN, ADMIN_IDS
        self.token = BOT_TOKEN
        self.db = db
        self.admin_ids = ADMIN_IDS if ADMIN_IDS else []
        self.application = None
        self.loop = None
        self.logo_path = "assets/logo.jpg"
        
        # Словарь для преобразования ключей услуг в русские названия
        self.service_names = {
            "septic": "🚚 Откачка септика",
            "cleaning": "🚽 Прочистка канализации",
            "canal_wash": "💧 Каналопромывка",
            "sludge": "🔧 Илосос",
            "video": "🔍 Видеодиагностика",
            "flushing": "🧹 Промывка канализации",
            "other": "❓ Другое",
            "plumbing": "🔧 Сантехнические работы",
            "installation": "💧 Установка септика",
            "diagnostics": "🔍 Видеодиагностика труб",
            "repair": "🛠 Ремонт канализации"
        }

    async def cmd_start(self, update: Update, context):
        """Команда /start с логотипом и меню ShveinyiHUB структуры."""
        user = update.effective_user
        user_id = user.id

        # Регистрируем пользователя
        self.db.add_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

        welcome_text = (
            f"👋 Привет, {user.first_name or 'друг'}! Меня зовут <b>Аква 💧</b>, и я виртуальный ассистент «<b>КаналТехСервис</b>». "
            f"Готова помочь вам с решением ассенизационных вопросов легко и быстро!\n\n"
            f"✨ <b>Чем мы занимаемся:</b>\n"
            f"🚚 Срочная откачка септиков и выгребных ям\n"
            f"💧 Эффективная прочистка канализации\n"
            f"✨ Промывка труб и услуги илососа\n"
            f"🔍 Видеодиагностика для точной оценки\n\n"
            f"⏰ Работаем круглосуточно и приезжаем уже в течение часа!\n"
            f"📍 Обслуживаем Ярцево и всю Смоленскую область.\n\n"
            f"Расскажите мне о вашей задаче — организую помощь в два счёта! 😊"
        )

        # Проверяем, админ ли это
        if user_id in self.admin_ids:
            welcome_text += f"\n\n👑 <b>Режим администратора</b>"
            reply_markup = get_admin_main_menu()
        else:
            reply_markup = get_persistent_menu()

        # Отправляем логотип если существует
        try:
            if os.path.exists(self.logo_path):
                with open(self.logo_path, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=welcome_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup
                    )
            else:
                await update.message.reply_text(
                    welcome_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"Ошибка отправки логотипа: {e}")
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )

        # Если обычный пользователь, показываем inline меню
        if user_id not in self.admin_ids:
            await update.message.reply_text(
                "👇 <b>Выбирайте нужное:</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=get_main_menu()
            )

    async def handle_menu_button(self, update: Update, context):
        """Обработка кнопки ☰ Меню."""
        context.user_data.clear()
        await update.message.reply_text(
            "👋 Это Аква 💧! Выбирайте, чем могу помочь 😊",
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu()
        )

    def get_order_action_keyboard(self, order_id: int, status: str):
        """Клавиатура действий с заявкой."""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        buttons = []
        if status == 'new':
            buttons.append([
                InlineKeyboardButton("🔄 В работу", callback_data=f"set_status_{order_id}_in_progress"),
                InlineKeyboardButton("❌ Отменить", callback_data=f"set_status_{order_id}_cancelled")
            ])
            buttons.append([
                InlineKeyboardButton("📤 Переслать исполнителю", callback_data=f"forward_order_{order_id}")
            ])
        elif status == 'in_progress':
            buttons.append([
                InlineKeyboardButton("✅ Выполнено", callback_data=f"set_status_{order_id}_completed"),
                InlineKeyboardButton("❌ Отменить", callback_data=f"set_status_{order_id}_cancelled")
            ])
        elif status == 'completed':
            buttons.append([
                InlineKeyboardButton("🔄 Вернуть в работу", callback_data=f"set_status_{order_id}_in_progress")
            ])
        elif status == 'cancelled':
            buttons.append([
                InlineKeyboardButton("🔄 Восстановить", callback_data=f"set_status_{order_id}_new")
            ])
        
        buttons.append([
            InlineKeyboardButton("📞 Позвонить клиенту", callback_data=f"call_client_{order_id}"),
            InlineKeyboardButton("📜 История", callback_data=f"client_history_{order_id}")
        ])
        buttons.append([
            InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_order_{order_id}")
        ])
        
        return InlineKeyboardMarkup(buttons)

    async def handle_admin_text_buttons(self, update: Update, context):
        """Обработка текстовых кнопок админ-меню."""
        text = update.message.text
        user_id = update.effective_user.id
        
        if user_id not in self.admin_ids:
            await update.message.reply_text("❌ Доступ запрещен")
            return
        
        status_map = {
            "📋 Новые заявки": "new",
            "⏳ В работе": "in_progress",
            "✅ Выполнены": "completed",
            "📊 Все заявки": "all"
        }
        
        if text in status_map:
            status = status_map[text]
            orders = self.db.get_all_orders() if status == "all" else self.db.get_orders_by_status(status)
            
            if orders:
                await update.message.reply_text(f"📋 <b>{text}:</b>", parse_mode=ParseMode.HTML)
                for order in orders[:10]:
                    order_id = order.get('order_id', '?')
                    service_key = order.get('service_type', 'Не указана')
                    service_name = self.service_names.get(service_key, service_key)
                    address = order.get('address', 'Не указан')
                    phone = order.get('phone', 'Не указан')
                    comment = order.get('comment', '')
                    order_status = order.get('status', 'new')
                    status_emoji = {'new': '🆕', 'in_progress': '🔄', 'completed': '✅', 'cancelled': '❌'}.get(order_status, '❓')
                    
                    order_text = (
                        f"{status_emoji} <b>Заявка #{order_id}</b>\n\n"
                        f"📋 Услуга: {service_name}\n"
                        f"📍 Адрес: {address}\n"
                        f"📞 Телефон: {phone}\n"
                        f"💬 Комментарий: {comment if comment else '—'}"
                    )
                    
                    keyboard = self.get_order_action_keyboard(order_id, order_status)
                    await update.message.reply_text(order_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            else:
                await update.message.reply_text(f"📋 <b>{text}:</b>\n\n<i>Заявок нет</i>", parse_mode=ParseMode.HTML)
        
        elif text == "📈 Статистика":
            stats = self.db.get_stats()
            response = (
                f"📊 <b>Статистика:</b>\n\n"
                f"🆕 Новых: {stats.get('new', 0)}\n"
                f"🔄 В работе: {stats.get('in_progress', 0)}\n"
                f"✅ Выполнено: {stats.get('completed', 0)}\n"
                f"❌ Отменено: {stats.get('cancelled', 0)}\n\n"
                f"📊 Всего: {stats.get('total', 0)}"
            )
            await update.message.reply_text(response, parse_mode=ParseMode.HTML)
        
        elif text == "👥 Пользователи":
            users_count = self.db.get_users_count()
            await update.message.reply_text(
                f"👥 <b>Пользователи:</b>\n\nВсего: {users_count}",
                parse_mode=ParseMode.HTML
            )
        
        elif text == "📢 Рассылка":
            context.user_data['step'] = 'enter_broadcast'
            await update.message.reply_text(
                "📢 <b>Рассылка сообщений</b>\n\n"
                "Напишите текст сообщения для рассылки всем пользователям.\n\n"
                "Отправьте /cancel для отмены.",
                parse_mode=ParseMode.HTML
            )
        
        elif text == "⚙️ Настройки":
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("👷 Исполнители", callback_data="settings_executors")],
                [InlineKeyboardButton("💰 Редактировать цены", callback_data="settings_prices")],
            ])
            await update.message.reply_text(
                "⚙️ <b>Настройки бота:</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        
        elif text == "◀️ Выйти":
            await update.message.reply_text(
                "👋 Вы вышли из админ-панели",
                parse_mode=ParseMode.HTML,
                reply_markup=get_persistent_menu()
            )

    async def handle_text_input(self, update: Update, context):
        """Обработка текстового ввода для заказа."""
        text = update.message.text
        user_id = update.effective_user.id
        step = context.user_data.get('step')
        
        logger.info(f"Text input from {user_id}: '{text}', step: {step}")
        
        # Обработка рассылки
        if step == 'enter_broadcast':
            if text == '/cancel':
                context.user_data.clear()
                await update.message.reply_text("❌ Рассылка отменена", parse_mode=ParseMode.HTML)
                return
            
            users = self.db.get_all_users()
            sent = 0
            failed = 0
            
            await update.message.reply_text(f"📤 Начинаю рассылку {len(users)} пользователям...", parse_mode=ParseMode.HTML)
            
            for user in users:
                try:
                    await self.application.bot.send_message(
                        chat_id=user['user_id'],
                        text=f"📢 <b>Уведомление от КаналТехСервис:</b>\n\n{text}",
                        parse_mode=ParseMode.HTML
                    )
                    sent += 1
                except Exception:
                    failed += 1
            
            context.user_data.clear()
            await update.message.reply_text(
                f"✅ Рассылка завершена!\n\n"
                f"📨 Отправлено: {sent}\n"
                f"❌ Ошибок: {failed}",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Обработка ввода ID исполнителя
        if step == 'enter_executor_id':
            try:
                executor_id = int(text)
                order_id = context.user_data.get('forward_order_id')
                order = self.db.get_order_by_id(order_id)
                
                if order:
                    service_key = order.get('service_type', 'Не указана')
                    service_name = self.service_names.get(service_key, service_key)
                    
                    order_text = (
                        f"📋 <b>Новая заявка #{order_id}</b>\n\n"
                        f"🔧 Услуга: {service_name}\n"
                        f"📍 Адрес: {order.get('address', 'Не указан')}\n"
                        f"📞 Телефон: {order.get('phone', 'Не указан')}\n"
                        f"💬 Комментарий: {order.get('comment', '') or '—'}\n\n"
                        f"Нажмите кнопку, когда возьмёте в работу:"
                    )
                    
                    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Взять в работу", callback_data=f"executor_take_{order_id}")]
                    ])
                    
                    await self.application.bot.send_message(
                        chat_id=executor_id,
                        text=order_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard
                    )
                    
                    await update.message.reply_text(
                        f"✅ Заявка #{order_id} переслана исполнителю!",
                        parse_mode=ParseMode.HTML
                    )
                
                context.user_data.clear()
                return
            except ValueError:
                await update.message.reply_text("❌ Неверный ID. Введите число.")
                return
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка: не удалось переслать. Проверьте ID исполнителя.")
                context.user_data.clear()
                return
        
        if step == 'enter_address':
            context.user_data['address'] = text
            context.user_data['step'] = 'enter_phone'
            await update.message.reply_text(
                "📞 Супер! Теперь напишите номер телефона для связи:",
                parse_mode=ParseMode.HTML,
                reply_markup=get_cancel_order_keyboard()
            )
        
        elif step == 'enter_phone':
            context.user_data['phone'] = text
            context.user_data['step'] = 'enter_comment'
            await update.message.reply_text(
                "💬 Почти готово! Напишите комментарий или нажмите кнопку:",
                parse_mode=ParseMode.HTML,
                reply_markup=get_skip_comment_keyboard()
            )
        
        elif step == 'enter_comment':
            context.user_data['comment'] = text
            await self.show_order_confirmation(update.message, context)
        
        elif step == 'ai_chat':
            response = get_ai_response(text)
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.HTML,
                reply_markup=get_ai_chat_keyboard()
            )
        
        else:
            await update.message.reply_text(
                "🤔 Не совсем поняла. Выберите действие из меню или напишите подробнее! 😊",
                reply_markup=get_main_menu()
            )

    async def handle_callback_query(self, update: Update, context):
        """Обработка всех callback запросов."""
        query = update.callback_query
        data = query.data
        user_id = update.effective_user.id
        
        logger.info(f"Callback received: {data} from user {user_id}")
        
        try:
            await query.answer()
            # Главное меню
            if data == "back_menu":
                await query.edit_message_text(
                    "<b>🔽 Главное меню КаналТехСервис:</b>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=get_main_menu()
                )

            # Услуги и цены
            elif data == "services":
                await query.edit_message_text(
                    "📋 <b>Выберите категорию услуг:</b>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=get_prices_menu()
                )

            # Создать заявку
            elif data == "new_order":
                context.user_data['step'] = 'select_service'
                await query.message.reply_text(
                    "<b>Выберите нужную услугу:</b>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=get_services_menu()
                )

            # Проверка статуса
            elif data == "check_status":
                orders = self.db.get_user_orders(user_id)
                if orders:
                    text = "<b>📊 Ваши заявки:</b>\n\n"
                    for i, order in enumerate(orders[:5], 1):
                        status_emoji = {
                            'new': '🆕',
                            'in_progress': '🔄',
                            'completed': '✅',
                            'cancelled': '❌'
                        }.get(order.get('status', 'new'), '❓')
                        text += f"{status_emoji} Заявка #{i:04d} - {order.get('status', 'неизвестно')}\n"
                    await query.edit_message_text(
                        text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=get_back_button()
                    )
                else:
                    await query.edit_message_text(
                        "❌ У вас пока нет заявок.",
                        reply_markup=get_back_button()
                    )

            # FAQ
            elif data == "faq":
                await query.edit_message_text(
                    "❓ <b>Часто задаваемые вопросы:</b>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=get_faq_menu()
                )

            # Контакты
            elif data == "contacts" or data == "show_phone":
                contacts_text = (
                    "📍 <b>КаналТехСервис</b>\n\n"
                    "📞 Телефон: <b>+7 (904) 363-36-36</b>\n"
                    "📧 Email: info@kanalteh.ru\n\n"
                    "⏰ Режим работы: <b>24/7</b>\n"
                    "🏠 г. Ярцево, Смоленская область\n\n"
                    "☎️ Звоните прямо сейчас — мы на связи!"
                )
                await query.message.reply_text(
                    contacts_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=get_ai_chat_keyboard()
                )

            # Обработка услуг для заказа
            elif data.startswith("service_"):
                service = data.replace("service_", "")
                service_names = self.service_names
                
                if service == "other":
                    context.user_data['step'] = 'ai_chat'
                    await query.message.reply_text(
                        "👋 Привет! Я <b>Аква 💧</b>.\n\n"
                        "Расскажите о вашей задаче — помогу разобраться и организую решение! 😊\n\n"
                        "💡 Отвечу на любые вопросы об услугах, ценах и сроках.",
                        parse_mode=ParseMode.HTML,
                        reply_markup=get_back_button()
                    )
                else:
                    context.user_data['service_type'] = service
                    context.user_data['service_name'] = service_names.get(service, service)
                    
                    await query.message.reply_text(
                        f"👍 Отлично! Вы выбрали: <b>{service_names.get(service, service)}</b>\n\n"
                        f"📍 Напишите адрес, куда приехать мастеру:",
                        parse_mode=ParseMode.HTML,
                        reply_markup=get_cancel_order_keyboard()
                    )
                    context.user_data['step'] = 'enter_address'

            # Пропустить комментарий
            elif data == "skip_comment":
                context.user_data['comment'] = ''
                await self.show_order_confirmation(query.message, context)

            # Отменить заявку
            elif data == "cancel_order":
                context.user_data.clear()
                await query.message.reply_text(
                    "❌ Заявка отменена.\n\nЕсли передумаете — я всегда на связи! 😊",
                    parse_mode=ParseMode.HTML,
                    reply_markup=get_main_menu()
                )

            # Подтвердить заявку
            elif data == "confirm_order":
                await self.finalize_order(query, context)

            # Изменить данные
            elif data == "edit_order":
                context.user_data['step'] = 'select_service'
                await query.message.reply_text(
                    "✏️ Давайте начнём заново!\n\n<b>Выберите нужную услугу:</b>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=get_services_menu()
                )

            # Показ цен по категориям
            elif data.startswith("price_"):
                await self.show_prices(query, data)

            # FAQ ответы
            elif data.startswith("faq_"):
                await self.show_faq_answer(query, data)

            # Смена статуса заявки
            elif data.startswith("set_status_"):
                await self.handle_set_status(query, data)
            
            # Переслать исполнителю
            elif data.startswith("forward_order_"):
                order_id = int(data.replace("forward_order_", ""))
                context.user_data['forward_order_id'] = order_id
                context.user_data['step'] = 'enter_executor_id'
                await query.message.reply_text(
                    "📤 <b>Пересылка заявки исполнителю</b>\n\n"
                    "Введите Telegram ID исполнителя или перешлите сообщение от него:",
                    parse_mode=ParseMode.HTML
                )
            
            # Показать телефон клиента
            elif data.startswith("call_client_"):
                order_id = int(data.replace("call_client_", ""))
                order = self.db.get_order_by_id(order_id)
                if order:
                    phone = order.get('phone', 'Не указан')
                    await query.answer(f"📞 Телефон: {phone}", show_alert=True)
                else:
                    await query.answer("❌ Заявка не найдена", show_alert=True)
            
            # Исполнитель берёт заявку
            elif data.startswith("executor_take_"):
                order_id = int(data.replace("executor_take_", ""))
                self.db.update_order_status(order_id, 'in_progress')
                await query.edit_message_text(
                    f"✅ <b>Заявка #{order_id} взята в работу!</b>\n\n"
                    f"Когда выполните — сообщите администратору.",
                    parse_mode=ParseMode.HTML
                )
                
                for admin_id in self.admin_ids:
                    try:
                        await self.application.bot.send_message(
                            chat_id=admin_id,
                            text=f"🔄 Заявка #{order_id} взята исполнителем в работу",
                            parse_mode=ParseMode.HTML
                        )
                    except:
                        pass

            # Удаление заявки
            elif data.startswith("delete_order_"):
                order_id = int(data.replace("delete_order_", ""))
                self.db.delete_order(order_id)
                await query.edit_message_text(
                    f"🗑 <b>Заявка #{order_id} удалена</b>",
                    parse_mode=ParseMode.HTML
                )
                await query.answer("Заявка удалена")
            
            # Настройки
            elif data == "settings_executors":
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Назад", callback_data="settings_back")]
                ])
                await query.edit_message_text(
                    "👷 <b>Исполнители</b>\n\n"
                    "Для добавления исполнителя:\n"
                    "1. Пусть он напишет боту /start\n"
                    "2. При пересылке заявки введите его Telegram ID\n\n"
                    "Узнать ID исполнителя можно через @userinfobot",
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
            
            elif data == "settings_prices":
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Назад", callback_data="settings_back")]
                ])
                await query.edit_message_text(
                    "💰 <b>Редактирование цен</b>\n\n"
                    "Цены настраиваются в файле app/config/__init__.py\n"
                    "Свяжитесь с разработчиком для изменения.",
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
            
            elif data == "settings_back":
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("👷 Исполнители", callback_data="settings_executors")],
                    [InlineKeyboardButton("💰 Редактировать цены", callback_data="settings_prices")],
                ])
                await query.edit_message_text(
                    "⚙️ <b>Настройки бота:</b>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
            
            # Просмотр истории клиента
            elif data.startswith("client_history_"):
                order_id = int(data.replace("client_history_", ""))
                order = self.db.get_order_by_id(order_id)
                if order:
                    client_id = order.get('user_id')
                    orders = self.db.get_user_orders(client_id)
                    if orders:
                        text = f"📋 <b>История заявок клиента:</b>\n\n"
                        for o in orders[:5]:
                            status_emoji = {'new': '🆕', 'in_progress': '🔄', 'completed': '✅', 'cancelled': '❌'}.get(o.get('status', ''), '❓')
                            service_key = o.get('service_type', '?')
                            service_name = self.service_names.get(service_key, service_key)
                            text += f"{status_emoji} #{o.get('order_id')} - {service_name}\n"
                        await query.answer()
                        await query.message.reply_text(text, parse_mode=ParseMode.HTML)
                    else:
                        await query.answer("У клиента нет других заявок", show_alert=True)
                else:
                    await query.answer("Заявка не найдена", show_alert=True)

            # Админ callbacks
            elif data.startswith("admin_") or data.startswith("status_"):
                await self.handle_admin_callbacks(query, context, data)

        except Exception as e:
            logger.error(f"Ошибка обработки callback {data}: {e}", exc_info=True)
            try:
                await query.answer("Произошла ошибка", show_alert=True)
            except:
                pass

    async def show_order_confirmation(self, message, context):
        """Показать подтверждение заявки перед отправкой."""
        service_name = context.user_data.get('service_name', 'Не указана')
        address = context.user_data.get('address', 'Не указан')
        phone = context.user_data.get('phone', 'Не указан')
        comment = context.user_data.get('comment', '')
        
        text = (
            f"📋 <b>Проверьте данные заявки:</b>\n\n"
            f"🔧 Услуга: {service_name}\n"
            f"📍 Адрес: {address}\n"
            f"📞 Телефон: {phone}\n"
            f"💬 Комментарий: {comment if comment else '—'}\n\n"
            f"Всё верно? Нажмите «Подтвердить» 👇"
        )
        
        context.user_data['step'] = 'confirm_order'
        await message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_confirm_order_keyboard()
        )

    async def finalize_order(self, query, context):
        """Создать заявку после подтверждения."""
        user_id = query.from_user.id
        
        service_name = context.user_data.get('service_name', 'Не указана')
        address = context.user_data.get('address', 'Не указан')
        phone = context.user_data.get('phone', 'Не указан')
        comment = context.user_data.get('comment', '')
        
        order_id = self.db.create_order(
            user_id=user_id,
            service_type=context.user_data.get('service_name', context.user_data.get('service_type', 'Не указана')),
            address=address,
            phone=phone,
            comment=comment
        )
        
        context.user_data.clear()
        
        await query.message.reply_text(
            f"🎉 <b>Заявка #{order_id} оформлена!</b>\n\n"
            f"📋 Услуга: {service_name}\n"
            f"📍 Адрес: {address}\n"
            f"📞 Телефон: {phone}\n"
            f"💬 Комментарий: {comment if comment else '—'}\n\n"
            f"👷 Мастер свяжется с вами в ближайшее время!\n"
            f"📞 Горячая линия: +7 (904) 363-36-36\n\n"
            f"Спасибо, что выбрали <b>КаналТехСервис</b>! Рада была помочь! 😊",
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu()
        )
        
        await self.notify_admins_new_order(order_id, service_name, address, phone, comment)

    async def show_prices(self, query, category_data):
        """Показать цены по категориям услуг."""
        category = category_data.replace("price_", "")
        
        prices_data = {
            "septic": (
                "🚚 <b>Откачка септика:</b>\n\n"
                "💰 Стоимость:\n"
                "• До 5м³ - 2 500₽\n"
                "• До 10м³ - 4 500₽\n"
                "• Свыше 10м³ - от 6 000₽\n\n"
                "⏰ Срок: 1-2 часа после вызова\n"
                "✅ Гарантия: 6 месяцев"
            ),
            "cleaning": (
                "🚽 <b>Прочистка канализации:</b>\n\n"
                "💰 Стоимость:\n"
                "• Механическая - от 1 500₽\n"
                "• Гидродинамическая - от 3 000₽\n"
                "• Устранение засора - от 1 000₽\n\n"
                "⏰ Срок: в день вызова\n"
                "✅ Гарантия: результат"
            ),
            "plumbing": (
                "🔧 <b>Сантехнические работы:</b>\n\n"
                "💰 Стоимость:\n"
                "• Вызов мастера - 500₽\n"
                "• Замена смесителя - от 800₽\n"
                "• Установка унитаза - от 1 500₽\n"
                "• Замена труб - от 2 000₽\n\n"
                "⏰ Срок: 2-4 часа\n"
                "✅ Гарантия: 6 месяцев"
            ),
            "installation": (
                "💧 <b>Установка септика:</b>\n\n"
                "💰 Стоимость:\n"
                "• Консультация - бесплатно\n"
                "• Установка под ключ - от 45 000₽\n"
                "• Монтаж дренажа - от 15 000₽\n\n"
                "⏰ Срок: 2-3 дня\n"
                "✅ Гарантия: 1 год"
            ),
            "diagnostics": (
                "🔍 <b>Видеодиагностика труб:</b>\n\n"
                "💰 Стоимость:\n"
                "• Видеоинспекция - от 3 000₽\n"
                "• Составление акта - 500₽\n"
                "• Выезд специалиста - 1 000₽\n\n"
                "⏰ Срок: до 4 часов\n"
                "✅ Результат: готовый отчет"
            ),
            "repair": (
                "🛠 <b>Ремонт канализации:</b>\n\n"
                "💰 Стоимость:\n"
                "• Замена участка трубы - от 2 000₽\n"
                "• Герметизация стыков - от 800₽\n"
                "• Ремонт колодца - от 5 000₽\n\n"
                "⏰ Срок: 3-5 часов\n"
                "✅ Гарантия: 6 месяцев"
            )
        }

        text = prices_data.get(category, "ℹ️ Информация временно недоступна")
        text += "\n\n💡 <i>Точную стоимость уточняйте при заказе</i>"

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_back_button()
        )

    async def show_faq_answer(self, query, faq_data):
        """Показать ответ на FAQ вопрос."""
        faq_type = faq_data.replace("faq_", "")
        
        faq_answers = {
            "services": (
                "📋 <b>Какие услуги мы предоставляем?</b>\n\n"
                "✓ Откачка септиков и выгребных ям\n"
                "✓ Прочистка канализации (все методы)\n"
                "✓ Сантехнические работы\n"
                "✓ Установка и замена септиков\n"
                "✓ Видеодиагностика труб\n"
                "✓ Ремонт канализации\n"
                "✓ Промывка систем\n\n"
                "💼 Профессиональная бригада с опытом 15+ лет"
            ),
            "prices": (
                "💰 <b>Цены на услуги:</b>\n\n"
                "Откачка септика - от 2 500₽\n"
                "Прочистка канализации - от 1 500₽\n"
                "Вызов сантехника - от 500₽\n"
                "Установка септика - от 45 000₽\n"
                "Видеодиагностика - от 3 000₽\n\n"
                "📝 <i>Скидки на постоянных клиентов до 15%</i>"
            ),
            "timing": (
                "⏰ <b>Сроки выполнения:</b>\n\n"
                "🚨 Экстренный выезд - 1-2 часа\n"
                "📅 Плановые работы - в день вызова\n"
                "🏗 Установка септика - 2-3 дня\n"
                "📋 Диагностика - до 4 часов\n\n"
                "24/7 готовы помочь в любой момент!"
            ),
            "location": (
                "📍 <b>Адрес и график:</b>\n\n"
                "Режим работы: 24/7 (без выходных)\n"
                "Город: Ярцево, Смоленская область\n\n"
                "📞 Телефон: +7 (904) 363-36-36\n"
                "📧 Email: info@kanalteh.ru\n\n"
                "🚗 Выезжаем во все районы города и области"
            ),
            "payment": (
                "💳 <b>Оплата и гарантия:</b>\n\n"
                "Принимаем:\n"
                "✓ Наличные\n"
                "✓ Карты (все системы)\n"
                "✓ Безналичный расчет\n"
                "✓ Сбербанк\n\n"
                "✅ Гарантия на работы: 6 месяцев\n"
                "📜 Работаем по договору"
            ),
            "order": (
                "📝 <b>Как оформить заявку?</b>\n\n"
                "1️⃣ Нажмите кнопку 'Создать заявку'\n"
                "2️⃣ Выберите нужную услугу\n"
                "3️⃣ Укажите адрес выполнения работ\n"
                "4️⃣ Оставьте номер телефона\n"
                "5️⃣ Подтвердите заявку\n\n"
                "☎️ Мы свяжемся с вами в течение 30 минут!"
            ),
            "zones": (
                "🚗 <b>Зоны обслуживания:</b>\n\n"
                "✓ г. Ярцево\n"
                "✓ Ярцевский район\n"
                "✓ Дачные поселки\n"
                "✓ п. Солнечный\n"
                "✓ Окрестные деревни\n\n"
                "🌍 Выезд за город - по договоренности\n"
                "💚 Кольцевая дорога - без доплаты"
            ),
            "other": (
                "❓ <b>Не нашли ответ?</b>\n\n"
                "☎️ Позвоните нам:\n"
                "+7 (904) 363-36-36\n\n"
                "📧 Напишите на email:\n"
                "info@kanalteh.ru\n\n"
                "💬 Или напишите в чат - ответим за 5 минут!"
            )
        }

        text = faq_answers.get(faq_type, "ℹ️ Информация временно недоступна.")
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_back_button()
        )

    async def handle_set_status(self, query, data):
        """Изменить статус заявки."""
        user_id = query.from_user.id
        if user_id not in self.admin_ids:
            await query.answer("❌ Доступ запрещен", show_alert=True)
            return
        
        parts = data.replace("set_status_", "").split("_", 1)
        order_id = int(parts[0])
        new_status = parts[1]
        
        self.db.update_order_status(order_id, new_status)
        
        # Русские названия статусов
        status_names = {
            'new': '🆕 Новая',
            'in_progress': '🔄 В работе',
            'completed': '✅ Выполнена',
            'cancelled': '❌ Отменена'
        }
        
        status_names_ru = {
            'new': 'Новая',
            'in_progress': 'В работе',
            'completed': 'Выполнена',
            'cancelled': 'Отменена'
        }
        
        order = self.db.get_order_by_id(order_id)
        if order:
            keyboard = self.get_order_action_keyboard(order_id, new_status)
            service_key = order.get('service_type', 'Не указана')
            service_name = self.service_names.get(service_key, service_key)
            
            order_text = (
                f"{status_names.get(new_status, new_status)} <b>Заявка #{order_id}</b>\n\n"
                f"📋 Услуга: {service_name}\n"
                f"📍 Адрес: {order.get('address', 'Не указан')}\n"
                f"📞 Телефон: {order.get('phone', 'Не указан')}\n"
                f"💬 Комментарий: {order.get('comment', '') or '—'}"
            )
            await query.edit_message_text(order_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            
            client_id = order.get('user_id')
            if client_id:
                await self.send_notification(client_id, order_id, new_status)
        
        await query.answer(f"✅ Статус изменён: {status_names_ru.get(new_status, new_status)}")

    async def handle_admin_callbacks(self, query, context, data):
        """Обработка админ-функций."""
        user_id = query.from_user.id
        if user_id not in self.admin_ids:
            await query.answer("❌ Доступ запрещен", show_alert=True)
            return

        if data == "admin_back_menu":
            await query.edit_message_text(
                "👑 <b>Админ-панель КаналТехСервис</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=get_admin_main_menu()
            )

        elif data.startswith("admin_orders_"):
            status = data.replace("admin_orders_", "")
            await query.edit_message_text(
                f"📋 <b>Заявки со статусом: {status}</b>\n\n<i>Функция в разработке</i>",
                parse_mode=ParseMode.HTML,
                reply_markup=get_admin_orders_submenu()
            )

    async def send_notification(self, user_id: int, order_id: int, new_status: str, comment: str = None):
        """Отправить уведомление об изменении статуса."""
        try:
            status_emoji = {
                'new': '🆕',
                'in_progress': '🔄',
                'completed': '✅',
                'cancelled': '❌'
            }.get(new_status, '❓')
            
            # Русские названия статусов
            status_names_ru = {
                'new': 'Новая',
                'in_progress': 'В работе',
                'completed': 'Выполнена',
                'cancelled': 'Отменена'
            }
            
            status_text = status_names_ru.get(new_status, new_status)

            text = f"📌 <b>Обновление статуса заявки</b>\n\n{status_emoji} Новый статус: <b>{status_text}</b>"
            if comment:
                text += f"\n\n💬 Комментарий: {comment}"

            if self.application:
                await self.application.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")

    async def send_status_notification(self, user_id: int, order_id: int, new_status: str):
        """Отправить уведомление клиенту об изменении статуса (для вызова из routes.py)"""
        try:
            status_texts = {
                'new': '🆕 Ваша заявка создана',
                'in_progress': '🔄 Ваша заявка взята в работу',
                'completed': '✅ Ваша заявка выполнена',
                'cancelled': '❌ Ваша заявка отменена'
            }
            
            text = f"{status_texts.get(new_status, '📌 Обновление статуса')}\n\n"
            text += f"📋 Номер заявки: #{order_id}\n"
            text += f"📞 Контакты: +7 (904) 363-36-36\n\n"
            text += "Спасибо, что выбрали <b>КаналТехСервис</b>! 😊"

            if self.application:
                await self.application.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")

    async def notify_admins_new_order(self, order_id, service_name, address, phone, comment):
        """Уведомление админов о новой заявке."""
        try:
            text = (
                f"🆕 <b>Новая заявка #{order_id}</b>\n\n"
                f"📋 Услуга: {service_name}\n"
                f"📍 Адрес: {address}\n"
                f"📞 Телефон: {phone}\n"
                f"💬 Комментарий: {comment if comment else 'нет'}"
            )
            
            if self.application:
                for admin_id in self.admin_ids:
                    try:
                        await self.application.bot.send_message(
                            chat_id=admin_id,
                            text=text,
                            parse_mode=ParseMode.HTML
                        )
                    except Exception as e:
                        logger.error(f"Ошибка уведомления админа {admin_id}: {e}")
        except Exception as e:
            logger.error(f"Ошибка уведомления админов: {e}")

    def setup_handlers(self):
        """Регистрация всех обработчиков."""
        # /start
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        
        # Кнопка меню
        self.application.add_handler(
            MessageHandler(filters.Regex("^☰ Меню$"), self.handle_menu_button)
        )
        
        # Админ кнопки
        admin_buttons = ["📋 Новые заявки", "⏳ В работе", "✅ Выполнены", "📊 Все заявки", 
                         "📈 Статистика", "👥 Пользователи", "📢 Рассылка", "⚙️ Настройки", "◀️ Выйти"]
        admin_pattern = "^(" + "|".join(admin_buttons) + ")$"
        self.application.add_handler(
            MessageHandler(filters.Regex(admin_pattern), self.handle_admin_text_buttons)
        )
        
        # Callbacks
        self.application.add_handler(
            CallbackQueryHandler(self.handle_callback_query)
        )
        
        # Текстовый ввод (адрес, телефон, комментарий)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^☰ Меню$"), self.handle_text_input)
        )
        
        logger.info("✅ Обработчики зарегистрированы")

    async def run(self):
        """Запуск бота."""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        # Сохраняем event loop для использования из других потоков
        self.loop = asyncio.get_event_loop()
        
        logger.info("Бот КаналТехСервис запущен")
        logger.info("Структура: ShveinyiHUB")
        logger.info("Услуги: Ассенизаторские")
        logger.info("Телефон: +7 (904) 363-36-36")
        logger.info("Режим: 24/7")
        
        async with self.application:
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=["message", "callback_query", "edited_message"]
            )
            
            # Keep running until interrupted
            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass
            finally:
                await self.application.updater.stop()
                await self.application.stop()
