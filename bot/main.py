import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
import re
import os
from dotenv import load_dotenv

from database.database import Database
from keyboards import get_location_keyboard, get_service_keyboard

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# FSM состояния
class RequestForm(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_address = State()
    waiting_for_service = State()
    waiting_for_phone = State()


# Получение токена бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не установлен BOT_TOKEN в .env файле")


class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self.db = Database()
        
        # Регистрация хендлеров
        self.register_handlers()
    
    def register_handlers(self):
        """Регистрация хендлеров"""
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message(Command("help"))(self.cmd_help)
        self.dp.message(Command("status"))(self.cmd_status)
        self.dp.message(F.text == "Новая заявка")(self.process_new_request_command)
        
        # FSM handlers
        self.dp.message(RequestForm.waiting_for_full_name)(self.process_full_name)
        self.dp.message(RequestForm.waiting_for_address)(self.process_address)
        self.dp.message(RequestForm.waiting_for_service)(self.process_service)
        self.dp.message(RequestForm.waiting_for_phone)(self.process_phone)
    
    async def cmd_start(self, message: Message, state: FSMContext):
        """Обработка команды /start"""
        await state.clear()
        welcome_text = (
            f"Добро пожаловать в систему подачи заявок <b>КаналТехСервис</b>, г. Ярцево!\n\n"
            f"С помощью этого бота вы можете подать заявку на ассенизаторские услуги.\n\n"
            f"Для начала работы нажмите кнопку <b>Новая заявка</b> или введите /help для справки."
        )
        
        # Отправляем сообщение с кнопкой
        keyboard = get_location_keyboard()
        await message.answer(welcome_text, reply_markup=keyboard)
    
    async def cmd_help(self, message: Message, state: FSMContext):
        """Обработка команды /help"""
        await state.clear()
        help_text = (
            "<b>КаналТехСервис, г. Ярцево</b>\n\n"
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/status - Проверить статус вашей последней заявки\n\n"
            "Чтобы подать новую заявку, нажмите кнопку <b>Новая заявка</b>"
        )
        await message.answer(help_text)
    
    async def cmd_status(self, message: Message):
        """Обработка команды /status"""
        user_id = message.from_user.id
        
        # Получаем последнюю заявку пользователя
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, status, comment, created_at FROM requests WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            request_id, status, comment, created_at = result
            status_text = f"Ваша последняя заявка №{request_id}:\n"
            status_text += f"<b>Статус:</b> {status}\n"
            status_text += f"<b>Дата создания:</b> {created_at}\n"
            
            if comment:
                status_text += f"<b>Комментарий:</b> {comment}"
            
            await message.answer(status_text)
        else:
            await message.answer("У вас пока нет заявок в системе.")
    
    async def process_new_request_command(self, message: Message, state: FSMContext):
        """Начало процесса подачи новой заявки"""
        user_id = message.from_user.id
        
        # Проверяем, не было ли заявки от пользователя за последние 24 часа
        if self.db.get_user_last_request_within_24h(user_id):
            await message.answer(
                "Вы уже подавали заявку за последние 24 часа. "
                "Подождите до истечения этого периода перед подачей новой заявки."
            )
            return
        
        await state.set_state(RequestForm.waiting_for_full_name)
        await message.answer(
            "Введите ваше полное имя (ФИО):",
            reply_markup=get_location_keyboard()  # Используем клавиатуру с местоположением как заглушку
        )
    
    async def process_full_name(self, message: Message, state: FSMContext):
        """Обработка введенного ФИО"""
        full_name = message.text.strip()
        
        if len(full_name.split()) < 2:
            await message.answer("Пожалуйста, введите полное имя (ФИО):")
            return
        
        await state.update_data(full_name=full_name)
        await state.set_state(RequestForm.waiting_for_address)
        
        await message.answer(
            "Выберите адрес выполнения работ:",
            reply_markup=get_location_keyboard()
        )
    
    async def process_address(self, message: Message, state: FSMContext):
        """Обработка выбранного адреса"""
        address = message.text.strip()
        
        # Валидация адреса
        valid_addresses = ["Ярцево", "Дачный посёлок", "п. Солнечный", "Другое"]
        if address not in valid_addresses:
            await message.answer(
                "Пожалуйста, выберите адрес из предложенных вариантов:"
            )
            return
        
        await state.update_data(address=address)
        await state.set_state(RequestForm.waiting_for_service)
        
        await message.answer(
            "Выберите тип услуги:",
            reply_markup=get_service_keyboard()
        )
    
    async def process_service(self, message: Message, state: FSMContext):
        """Обработка выбранного типа услуги"""
        service_type = message.text.strip()
        
        # Валидация типа услуги
        valid_services = ["Ассенизаторские услуги", "Вызов сантехника", "Прочистка труб", "Установка сантехники"]
        if service_type not in valid_services:
            await message.answer(
                "Пожалуйста, выберите тип услуги из предложенных вариантов:"
            )
            return
        
        await state.update_data(service_type=service_type)
        await state.set_state(RequestForm.waiting_for_phone)
        
        await message.answer(
            "Введите ваш номер телефона в формате +7XXXXXXXXXX:",
            reply_markup=get_location_keyboard()  # Убираем клавиатуру после выбора услуги
        )
    
    async def process_phone(self, message: Message, state: FSMContext):
        """Обработка введенного номера телефона"""
        phone = message.text.strip()
        
        # Проверяем формат номера телефона
        phone_pattern = r'^\+7\d{10}$'
        if not re.match(phone_pattern, phone):
            await message.answer(
                "Неверный формат номера телефона. Введите номер в формате +7XXXXXXXXXX:"
            )
            return
        
        # Получаем данные из состояния
        data = await state.get_data()
        user_id = message.from_user.id
        full_name = data['full_name']
        address = data['address']
        service_type = data['service_type']
        
        # Создаем заявку в базе данных
        request_id = self.db.create_request(user_id, full_name, address, service_type, phone)
        
        # Очищаем состояние
        await state.clear()
        
        # Отправляем подтверждение
        success_message = (
            f"Спасибо, <b>{full_name}</b>! Ваша заявка №{request_id} принята.\n\n"
            f"Адрес: {address}\n"
            f"Услуга: {service_type}\n"
            f"Телефон: {phone}\n\n"
            f"С вами свяжется наш специалист для уточнения деталей.\n\n"
            f"Компания <b>КаналТехСервис</b>, г. Ярцево"
        )
        
        await message.answer(success_message)
    
    async def send_status_update(self, user_id, request_id, new_status, comment=None):
        """Отправка обновления статуса пользователю"""
        try:
            status_message = f"Статус вашей заявки №{request_id} обновлен: <b>{new_status}</b>"
            if comment:
                status_message += f"\nКомментарий: {comment}"
            
            await self.bot.send_message(user_id, status_message)
        except Exception as e:
            logging.error(f"Ошибка при отправке обновления статуса пользователю {user_id}: {e}")
    
    async def run(self):
        """Запуск бота"""
        await self.dp.start_polling(self.bot)


async def main():
    bot_instance = TelegramBot()
    await bot_instance.run()


if __name__ == "__main__":
    asyncio.run(main())