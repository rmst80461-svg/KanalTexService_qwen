"""
Главный обработчик бота КаналТехСервис (структура как в ShveinyiHUB).
Адаптировано под ассенизаторские услуги с интеграцией всех handlers.
"""
import asyncio
import logging
import os
from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
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
    get_admin_main_menu,
    get_admin_order_detail_keyboard,
    get_admin_orders_submenu,
    get_contact_keyboard,
    get_location_keyboard,
    get_confirmation_keyboard,
    remove_keyboard
)

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler заявки
SELECT_SERVICE, ENTER_ADDRESS, ENTER_PHONE, ENTER_DESCRIPTION, CONFIRM_ORDER = range(5)


class TelegramBot:
    """Класс Telegram бота для КаналТехСервис."""

    def __init__(self, db: 'Database'):
        from app.config import BOT_TOKEN, ADMIN_IDS
        self.token = BOT_TOKEN
        self.db = db
        self.admin_ids = ADMIN_IDS if ADMIN_IDS else []
        self.application = None
        self.logo_path = "assets/logo.jpg"  # Путь к логотипу

    async def cmd_start(self, update: Update, context):
        """Команда /start - показывает главное меню с логотипом."""
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
            f"🚚 Добро пожаловать в <b>КаналТехСервис</b>, г. Ярцево!\n\n"
            f"Мы предоставляем профессиональные ассенизаторские и сантехнические услуги.\n\n"
            f"<b>Наши услуги:</b>\n"
            f"• Откачка септиков и выгребных ям\n"
            f"• Прочистка канализации\n"
            f"• Сантехнические работы\n"
            f"• Установка септиков\n"
            f"• Видеодиагностика труб\n\n"
            f"Выберите нужный пункт меню:"
        )

        # Проверяем, является ли пользователь админом
        if user_id in self.admin_ids:
            welcome_text += "\n\n👑 <b>Режим администратора активен</b>"
            reply_markup = get_admin_main_menu()
        else:
            reply_markup = get_persistent_menu()

        # Отправляем логотип, если файл существует
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

        # Если не админ, показываем inline меню
        if user_id not in self.admin_ids:
            await update.message.reply_text(
                "Выберите действие:",
                reply_markup=get_main_menu()
            )

    async def handle_menu_button(self, update: Update, context):
        """Обработка кнопки ☰ Меню."""
        await update.message.reply_text(
            "Главное меню КаналТехСервис:",
            reply_markup=get_main_menu()
        )

    async def handle_callback_query(self, update: Update, context):
        """Обработка callback запросов."""
        query = update.callback_query
        await query.answer()

        data = query.data

        # Главное меню
        if data == "back_menu":
            await query.edit_message_text(
                "Главное меню КаналТехСервис:",
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
            await query.message.reply_text(
                "Выберите услугу:",
                reply_markup=get_services_menu()
            )

        # Начало оформления заявки
        elif data.startswith("service_"):
            service_type = data.replace("service_", "")
            context.user_data['service_type'] = service_type
            await query.message.reply_text(
                "📍 Отправьте адрес выполнения работ:",
                reply_markup=get_location_keyboard()
            )
            return SELECT_SERVICE

        # Проверка статуса
        elif data == "check_status":
            user_id = update.effective_user.id
            orders = self.db.get_user_orders(user_id)
            if orders:
                text = "<b>Ваши заявки:</b>\n\n"
                for order in orders[:5]:
                    status_emoji = {
                        'new': '🆕',
                        'in_progress': '🔄',
                        'completed': '✅',
                        'cancelled': '❌'
                    }.get(order.get('status', 'new'), '❓')
                    text += f"{status_emoji} Заявка #{order['order_id']:04d} - {order['status']}\n"
                await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=get_back_button())
            else:
                await query.edit_message_text(
                    "У вас пока нет заявок.",
                    reply_markup=get_back_button()
                )

        # FAQ
        elif data == "faq":
            await query.edit_message_text(
                "❓ <b>Часто задаваемые вопросы:</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=get_faq_menu()
            )

        # Конкретные FAQ
        elif data.startswith("faq_"):
            await self.show_faq_answer(query, data)

        # Контакты
        elif data == "contacts":
            contacts_text = (
                "📍 <b>КаналТехСервис</b>\n\n"
                "📞 Телефон: +7 (XXX) XXX-XX-XX\n"
                "📧 Email: info@kanalteh.ru\n"
                "🌐 Сайт: kanalteh.ru\n\n"
                "⏰ Режим работы: 24/7\n"
                "📍 Адрес: г. Ярцево, Смоленская область"
            )
            await query.edit_message_text(
                contacts_text,
                parse_mode=ParseMode.HTML,
                reply_markup=get_back_button()
            )

        # Цены по категориям
        elif data.startswith("price_"):
            await self.show_prices(query, data)

        # Админ функции
        elif data.startswith("admin_") or data.startswith("status_"):
            await self.handle_admin_callbacks(query, context)

    async def show_prices(self, query, category_data):
        """Показать цены по категории."""
        category = category_data.replace("price_", "")
        
        prices_data = {
            "septic": "🚚 <b>Откачка септика:</b>\n• До 5м³ - 2500₽\n• До 10м³ - 4500₽\n• Свыше 10м³ - от 6000₽",
            "cleaning": "🚽 <b>Прочистка канализации:</b>\n• Механическая - от 1500₽\n• Гидродинамическая - от 3000₽\n• Устранение засора - от 1000₽",
            "plumbing": "🔧 <b>Сантехнические работы:</b>\n• Вызов мастера - 500₽\n• Замена смесителя - от 800₽\n• Установка унитаза - от 1500₽",
            "installation": "💧 <b>Установка септика:</b>\n• Консультация - бесплатно\n• Установка под ключ - от 45000₽\n• Монтаж дренажа - от 15000₽",
            "diagnostics": "🔍 <b>Диагностика труб:</b>\n• Видеоинспекция - от 3000₽\n• Составление акта - 500₽\n• Выезд специалиста - 1000₽",
            "repair": "🛠 <b>Ремонт канализации:</b>\n• Замена участка трубы - от 2000₽\n• Герметизация стыков - от 800₽\n• Ремонт колодца - от 5000₽"
        }

        text = prices_data.get(category, "Информация о ценах временно недоступна.")
        text += "\n\n💡 <i>Точную стоимость уточняйте при заказе.</i>"

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_back_button()
        )

    async def show_faq_answer(self, query, faq_data):
        """Показать ответ на FAQ."""
        faq_type = faq_data.replace("faq_", "")
        
        faq_answers = {
            "services": "<b>Наши услуги:</b>\n• Откачка септиков\n• Прочистка канализации\n• Сантехнические работы\n• Установка септиков\n• Видеодиагностика\n• Ремонт канализации",
            "prices": "Цены зависят от объема работ и сложности. Базовые расценки:\n• Откачка септика от 2500₽\n• Прочистка от 1500₽\n• Вызов сантехника от 500₽",
            "timing": "⏰ Сроки выполнения:\n• Экстренный выезд - 1-2 часа\n• Плановые работы - в день заявки\n• Установка септика - 2-3 дня",
            "location": "📍 Мы работаем в г. Ярцево и прилегающих районах.\n⏰ Режим работы: 24/7\n☎️ Телефон: +7 (XXX) XXX-XX-XX",
            "payment": "💳 Принимаем:\n• Наличные\n• Карты\n• Безналичный расчет\n\n✅ Гарантия на работы - 6 месяцев",
            "order": "📝 Как заказать:\n1. Нажмите 'Создать заявку'\n2. Выберите услугу\n3. Укажите адрес\n4. Подтвердите заявку\n\nМы свяжемся с вами в течение 30 минут!",
            "zones": "🗺 Зоны обслуживания:\n• г. Ярцево\n• Ярцевский район\n• Дачные поселки\n• п. Солнечный\n\nВыезд за город - по договоренности",
            "other": "Не нашли ответ на вопрос?\n\n☎️ Позвоните нам: +7 (XXX) XXX-XX-XX\n📧 Напишите: info@kanalteh.ru"
        }

        text = faq_answers.get(faq_type, "Информация временно недоступна.")
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_back_button()
        )

    async def handle_admin_callbacks(self, query, context):
        """Обработка админских callback'ов."""
        # TODO: Реализовать полноценную админ-панель
        await query.answer("Админ-функции в разработке")

    async def send_notification(self, user_id: int, order_id: int, new_status: str, comment: str = None):
        """Отправка уведомления об изменении статуса."""
        try:
            status_text = {
                'new': '🆕 Новая',
                'in_progress': '🔄 В работе',
                'completed': '✅ Выполнена',
                'cancelled': '❌ Отменена'
            }.get(new_status, new_status)

            text = f"Статус вашей заявки #{order_id:04d} изменен на: {status_text}"
            if comment:
                text += f"\n\n💬 Комментарий: {comment}"

            await self.application.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")

    def setup_handlers(self):
        """Регистрация обработчиков."""
        # Команды
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        
        # Кнопка меню
        self.application.add_handler(
            MessageHandler(filters.Regex("^☰ Меню$"), self.handle_menu_button)
        )
        
        # Callback'и
        self.application.add_handler(
            CallbackQueryHandler(self.handle_callback_query)
        )

    async def run(self):
        """Запуск бота."""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        logger.info("🚀 Бот КаналТехСервис запущен")
        await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
