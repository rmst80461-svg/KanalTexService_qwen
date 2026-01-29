"""
Telegram bot handler - полная интеграция всех модулей (образец: ShveinyiHUB)
Адаптировано для КаналТехСервис, г. Ярцево
"""
import os
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.enums import ParseMode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.database import Database

logger = logging.getLogger(__name__)

# Информация о компании
COMPANY_INFO = {
    "name": "КаналТехСервис",
    "city": "г. Ярцево",
    "address": "г. Ярцево, Смоленская область",
    "phone": "+7 (XXX) XXX-XX-XX",  # TODO: Заполнить реальный номер
    "whatsapp": "+7 (XXX) XXX-XX-XX",
    "hours": "Круглосуточно, 24/7"
}

class TelegramBot:
    def __init__(self, db: 'Database'):
        from app.config import BOT_TOKEN
        self.bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        self.db = db
        
        # Путь к логотипу
        self.logo_path = Path(__file__).parent.parent.parent / "assets" / "logo.jpg"
        
        # Регистрация handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Регистрация всех handlers по образцу ShveinyiHUB"""
        from app.bot.handlers.commands import CommandsHandler
        from app.bot.handlers.order_handler import OrderHandler, SELECT_CATEGORY, ENTER_DESCRIPTION, UPLOAD_PHOTO, CONFIRM_ORDER
        from app.bot.handlers.admin_handler import AdminHandler
        from app.bot.handlers.review_handler import ReviewHandler
        from app.bot.handlers.faq_handler import FAQHandler
        from app.bot.handlers.price_handler import PriceHandler
        from aiogram.fsm.context import FSMContext
        from aiogram.types import Update
        from telegram.ext import ConversationHandler
        
        # Инициализация handlers
        cmd_handler = CommandsHandler(self.db)
        order_handler = OrderHandler(self.db)
        admin_handler = AdminHandler(self.db)
        review_handler = ReviewHandler(self.db)
        faq_handler = FAQHandler(self.db)
        price_handler = PriceHandler(self.db)
        
        # === КОМАНДЫ ===
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(cmd_handler.help_command, Command("help"))
        self.dp.message.register(order_handler.start_order, Command("order"))
        self.dp.message.register(cmd_handler.status_command, Command("status"))
        self.dp.message.register(price_handler.services_command, Command("services"))
        self.dp.message.register(faq_handler.faq_command, Command("faq"))
        self.dp.message.register(cmd_handler.contact_command, Command("contact"))
        self.dp.message.register(cmd_handler.menu_command, Command("menu"))
        
        # Админ команды
        self.dp.message.register(admin_handler.admin_panel, Command("admin"))
        self.dp.message.register(admin_handler.show_stats, Command("stats"))
        self.dp.message.register(admin_handler.list_orders, Command("orders"))
        self.dp.message.register(admin_handler.list_users, Command("users"))
        self.dp.message.register(admin_handler.broadcast_start, Command("broadcast"))
        
        # === CALLBACK HANDLERS ===
        # Главное меню
        self.dp.callback_query.register(order_handler.start_order, F.data == "new_order")
        self.dp.callback_query.register(price_handler.show_services, F.data == "services")
        self.dp.callback_query.register(self.callback_check_status, F.data == "check_status")
        self.dp.callback_query.register(faq_handler.show_faq_menu, F.data == "faq")
        self.dp.callback_query.register(self.callback_contacts, F.data == "contacts")
        self.dp.callback_query.register(self.callback_back_menu, F.data == "back_menu")
        self.dp.callback_query.register(self.callback_contact_master, F.data == "contact_master")
        
        # Цены по категориям
        self.dp.callback_query.register(price_handler.show_category, F.data.startswith("price_"))
        
        # FAQ категории
        self.dp.callback_query.register(faq_handler.show_faq_item, F.data.startswith("faq_"))
        
        # Заказы - callback
        self.dp.callback_query.register(order_handler.select_category, F.data.startswith("cat_"))
        self.dp.callback_query.register(order_handler.finalize_order, F.data.in_(["confirm_yes", "confirm_no"]))
        self.dp.callback_query.register(order_handler.view_order_details, F.data.startswith("view_order_"))
        
        # Отзывы
        self.dp.callback_query.register(review_handler.start_review, F.data == "leave_review")
        self.dp.callback_query.register(review_handler.select_rating, F.data.startswith("rating_"))
        
        # Админ callbacks
        self.dp.callback_query.register(admin_handler.handle_admin_callback, F.data.startswith("admin_"))
        self.dp.callback_query.register(admin_handler.handle_order_status, F.data.startswith("order_"))
        self.dp.callback_query.register(admin_handler.handle_pagination, F.data.startswith("page_"))
        
        logger.info("✅ Все handlers зарегистрированы")
    
    async def cmd_start(self, message: Message):
        """Команда /start с логотипом (по образцу ShveinyiHUB)"""
        from app.bot.keyboards import Keyboards
        kb = Keyboards()
        
        user = message.from_user
        name = user.first_name or "друг"
        
        # Приветственный текст
        caption = (
            f"🚰 <b>{COMPANY_INFO['name']}</b>\n\n"
            f"Здравствуйте, {name}! 👋\n\n"
            f"Мы предоставляем профессиональные ассенизаторские услуги в {COMPANY_INFO['city']}.\n\n"
            f"Чем можем помочь?"
        )
        
        # Отправляем логотип если есть
        if self.logo_path.exists():
            try:
                with open(self.logo_path, "rb") as photo:
                    await message.answer_photo(
                        photo=photo,
                        caption=caption,
                        parse_mode=ParseMode.HTML
                    )
            except Exception as e:
                logger.warning(f"Не удалось отправить логотип: {e}")
                await message.answer(caption, parse_mode=ParseMode.HTML)
        else:
            await message.answer(caption, parse_mode=ParseMode.HTML)
        
        # Главное меню
        menu_text = f"🚰 <b>{COMPANY_INFO['name']} — Главное меню</b>"
        await message.answer(
            menu_text,
            reply_markup=kb.main_menu_inline(),
            parse_mode=ParseMode.HTML
        )
        
        # Сохраняем пользователя в БД
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        self.db.update_user_activity(user.id)
    
    async def callback_check_status(self, callback: CallbackQuery):
        """Проверка статуса заказов пользователя"""
        from app.bot.keyboards import Keyboards
        from app.utils.formatters import format_order_id
        
        kb = Keyboards()
        await callback.answer()
        
        user_id = callback.from_user.id
        orders = self.db.get_user_orders(user_id)
        
        if not orders:
            text = (
                "🔍 У вас нет активных заказов.\n\n"
                f"Позвоните нам: {COMPANY_INFO['phone']}"
            )
        else:
            text = "🔍 <b>Ваши заказы:</b>\n\n"
            status_map = {
                "new": "🆕 Новый",
                "accepted": "✅ Принят",
                "in_progress": "🔄 В работе",
                "completed": "✅ Выполнен",
                "cancelled": "❌ Отменён"
            }
            
            for order in orders[:5]:  # Показываем последние 5
                status = status_map.get(order['status'], order['status'])
                desc = order['description'] or order['service_type']
                formatted_id = format_order_id(order['order_id'], order['created_at'])
                text += f"<b>{formatted_id}</b> - {status}\n{desc}\n\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=kb.back_button(),
            parse_mode=ParseMode.HTML
        )
    
    async def callback_contacts(self, callback: CallbackQuery):
        """Показать контакты"""
        from app.bot.keyboards import Keyboards
        kb = Keyboards()
        await callback.answer()
        
        text = (
            f"📍 <b>Наши контакты:</b>\n\n"
            f"🏠 <b>Адрес:</b>\n{COMPANY_INFO['address']}\n\n"
            f"📞 <b>Телефон:</b>\n{COMPANY_INFO['phone']}\n\n"
            f"💬 <b>WhatsApp:</b>\n{COMPANY_INFO['whatsapp']}\n\n"
            f"⏰ <b>Режим работы:</b>\n{COMPANY_INFO['hours']}"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=kb.back_button(),
            parse_mode=ParseMode.HTML
        )
    
    async def callback_back_menu(self, callback: CallbackQuery):
        """Вернуться в главное меню"""
        from app.bot.keyboards import Keyboards
        kb = Keyboards()
        await callback.answer()
        
        text = f"🚰 <b>{COMPANY_INFO['name']} — Главное меню</b>"
        await callback.message.edit_text(
            text,
            reply_markup=kb.main_menu_inline(),
            parse_mode=ParseMode.HTML
        )
    
    async def callback_contact_master(self, callback: CallbackQuery):
        """Связаться с мастером"""
        from app.bot.keyboards import Keyboards
        kb = Keyboards()
        await callback.answer()
        
        text = (
            f"👨‍🔧 <b>Связаться с нами</b>\n\n"
            f"📞 <b>Позвоните:</b> {COMPANY_INFO['phone']}\n"
            f"💬 <b>WhatsApp:</b> {COMPANY_INFO['whatsapp']}\n\n"
            f"📍 <b>Адрес:</b>\n{COMPANY_INFO['address']}\n\n"
            f"⏰ {COMPANY_INFO['hours']}"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=kb.back_button(),
            parse_mode=ParseMode.HTML
        )
    
    async def send_status_notification(self, user_id: int, order_id: int, new_status: str, comment: str = None):
        """Отправка уведомления об изменении статуса заказа"""
        from app.utils.formatters import format_order_id
        from app.models.database import Database
        
        order = self.db.get_order(order_id)
        if not order:
            return
        
        status_text = {
            'new': '🆕 Новый',
            'accepted': '✅ Принят в работу',
            'in_progress': '🔄 Выполняется',
            'completed': '✅ Выполнен',
            'cancelled': '❌ Отменён'
        }.get(new_status, new_status)
        
        formatted_id = format_order_id(order_id, order['created_at'])
        
        message = (
            f"📢 <b>Обновление статуса заказа</b>\n\n"
            f"Заказ: <b>{formatted_id}</b>\n"
            f"Новый статус: {status_text}\n"
        )
        
        if comment:
            message += f"\n💬 Комментарий: {comment}"
        
        try:
            await self.bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
            logger.info(f"✅ Уведомление отправлено пользователю {user_id} о заказе {order_id}")
        except Exception as e:
            logger.error(f"❌ Не удалось отправить уведомление пользователю {user_id}: {e}")
    
    async def setup_bot_commands(self):
        """Установка команд бота в меню"""
        commands = [
            BotCommand(command="start", description="🏠 Главное меню"),
            BotCommand(command="order", description="➕ Оформить заказ"),
            BotCommand(command="status", description="🔍 Статус заказа"),
            BotCommand(command="services", description="📋 Услуги и цены"),
            BotCommand(command="faq", description="❓ Частые вопросы"),
            BotCommand(command="contact", description="📞 Контакты"),
            BotCommand(command="help", description="❓ Справка"),
        ]
        
        await self.bot.set_my_commands(commands)
        logger.info("✅ Команды бота установлены")
    
    async def run(self):
        """Запуск бота"""
        try:
            # Устанавливаем команды
            await self.setup_bot_commands()
            
            # Удаляем webhook если был
            await self.bot.delete_webhook(drop_pending_updates=True)
            
            logger.info("🚀 Бот запущен и готов к работе!")
            logger.info(f"📋 Компания: {COMPANY_INFO['name']}, {COMPANY_INFO['city']}")
            
            # Запускаем polling
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"❌ Ошибка при запуске бота: {e}")
            raise
        finally:
            await self.bot.session.close()
