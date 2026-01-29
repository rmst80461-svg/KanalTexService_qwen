"""
Главный обработчик Telegram бота КаналТехСервис (структура ShveinyiHUB)
"""
import logging
import os
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
    remove_keyboard
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
        self.logo_path = "assets/logo.jpg"

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
            f"👋 Привет, {user.first_name or 'друг'}! Меня зовут <b>Аква</b>, и я девушка-помощник из «<b>КаналТехСервис</b>». "
            f"Готова помочь вам с решением сантехнических вопросов легко и быстро!\n\n"
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
            "👋 Это Аква! Выбирайте, чем могу помочь 😊",
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu()
        )

    async def handle_text_input(self, update: Update, context):
        """Обработка текстового ввода для заказа."""
        text = update.message.text
        user_id = update.effective_user.id
        step = context.user_data.get('step')
        
        logger.info(f"Text input from {user_id}: '{text}', step: {step}")
        
        if step == 'enter_address':
            context.user_data['address'] = text
            context.user_data['step'] = 'enter_phone'
            await update.message.reply_text(
                "📞 Супер! Теперь напишите номер телефона для связи:",
                parse_mode=ParseMode.HTML
            )
        
        elif step == 'enter_phone':
            context.user_data['phone'] = text
            context.user_data['step'] = 'enter_comment'
            await update.message.reply_text(
                "💬 Почти готово! Хотите добавить комментарий? Если нет — напишите «нет»:",
                parse_mode=ParseMode.HTML
            )
        
        elif step == 'enter_comment':
            comment = text if text.lower() != 'нет' else ''
            
            service_name = context.user_data.get('service_name', 'Не указана')
            address = context.user_data.get('address', 'Не указан')
            phone = context.user_data.get('phone', 'Не указан')
            
            order_id = self.db.create_order(
                user_id=user_id,
                service_type=context.user_data.get('service_type', 'other'),
                address=address,
                phone=phone,
                comment=comment
            )
            
            context.user_data.clear()
            
            await update.message.reply_text(
                f"🎉 <b>Заявка #{order_id} оформлена!</b>\n\n"
                f"📋 Услуга: {service_name}\n"
                f"📍 Адрес: {address}\n"
                f"📞 Телефон: {phone}\n"
                f"💬 Комментарий: {comment if comment else '—'}\n\n"
                f"👷 Мастер свяжется с вами в ближайшее время!\n"
                f"📞 Горячая линия: +7 (910) 555-84-14\n\n"
                f"Спасибо, что выбрали <b>КаналТехСервис</b>! Рада была помочь! 😊",
                parse_mode=ParseMode.HTML,
                reply_markup=get_main_menu()
            )
            
            await self.notify_admins_new_order(order_id, service_name, address, phone, comment)
        
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
                    "📞 Телефон: <b>+7 (910) 555-84-14</b>\n"
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
                service_names = {
                    "septic": "🚚 Откачка септика",
                    "cleaning": "🚽 Прочистка канализации",
                    "canal_wash": "💧 Каналопромывка",
                    "sludge": "🔧 Илосос",
                    "video": "🔍 Видеодиагностика",
                    "flushing": "🧹 Промывка канализации",
                    "other": "❓ Другое"
                }
                
                if service == "other":
                    context.user_data['step'] = 'ai_chat'
                    await query.message.reply_text(
                        "👋 Привет! Я <b>Аква</b>.\n\n"
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
                        parse_mode=ParseMode.HTML
                    )
                    context.user_data['step'] = 'enter_address'

            # Показ цен по категориям
            elif data.startswith("price_"):
                await self.show_prices(query, data)

            # FAQ ответы
            elif data.startswith("faq_"):
                await self.show_faq_answer(query, data)

            # Админ callbacks
            elif data.startswith("admin_") or data.startswith("status_"):
                await self.handle_admin_callbacks(query, context, data)

        except Exception as e:
            logger.error(f"Ошибка обработки callback {data}: {e}", exc_info=True)
            try:
                await query.answer("Произошла ошибка", show_alert=True)
            except:
                pass

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
                "📞 Телефон: +7 (910) 555-84-14\n"
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
                "+7 (910) 555-84-14\n\n"
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

            text = f"📌 <b>Обновление статуса заявки</b>\n\n{status_emoji} Новый статус: <b>{new_status}</b>"
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
        
        logger.info("Бот КаналТехСервис запущен")
        logger.info("Структура: ShveinyiHUB")
        logger.info("Услуги: Ассенизаторские")
        logger.info("Телефон: +7 (910) 555-84-14")
        logger.info("Режим: 24/7")
        
        async with self.application:
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=["message", "callback_query", "edited_message"]
            )
            
            # Keep running until interrupted
            import asyncio
            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass
            finally:
                await self.application.updater.stop()
                await self.application.stop()
