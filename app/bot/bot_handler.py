"""
Telegram bot handler module
"""
import asyncio
import logging
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.database import Database


class RequestForm(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_address = State()
    waiting_for_service = State()
    waiting_for_phone = State()


class TelegramBot:
    def __init__(self, db: 'Database'):
        from app.config import BOT_TOKEN
        self.bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self.db = db
        
        # Register handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register handlers"""
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
        """Handle /start command"""
        await state.clear()
        welcome_text = (
            f"Добро пожаловать в систему подачи заявок <b>КаналТехСервис</b>, г. Ярцево!\n\n"
            f"С помощью этого бота вы можете подать заявку на ассенизаторские услуги.\n\n"
            f"Для начала работы нажмите кнопку <b>Новая заявка</b> или введите /help для справки."
        )
        
        # Keyboard with "New Request" button
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Новая заявка")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(welcome_text, reply_markup=keyboard)
    
    async def cmd_help(self, message: Message, state: FSMContext):
        """Handle /help command"""
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
        """Handle /status command"""
        user_id = message.from_user.id
        
        # Get user's latest request using the database class
        # We'll fetch all requests and filter by user_id to use our existing methods
        all_requests = self.db.get_all_requests()
        user_requests = [req for req in all_requests if req[1] == user_id]  # Filter by user_id (index 1)
        
        if user_requests:
            # Get the most recent request
            latest_request = user_requests[0]  # Since they're ordered by date DESC
            request_id, _, _, _, _, _, status, comment, created_at = latest_request
            
            status_text = f"Ваша последняя заявка №{request_id}:\n"
            status_text += f"<b>Статус:</b> {status}\n"
            status_text += f"<b>Дата создания:</b> {created_at}\n"
            
            if comment:
                status_text += f"<b>Комментарий:</b> {comment}"
            
            await message.answer(status_text)
        else:
            await message.answer("У вас пока нет заявок в системе.")
    
    async def process_new_request_command(self, message: Message, state: FSMContext):
        """Start new request process"""
        user_id = message.from_user.id
        
        # Check if user has submitted a request within the last 24 hours
        if self.db.get_user_last_request_within_24h(user_id):
            await message.answer(
                "Вы уже подавали заявку за последние 24 часа. "
                "Подождите до истечения этого периода перед подачей новой заявки."
            )
            return
        
        await state.set_state(RequestForm.waiting_for_full_name)
        await message.answer(
            "Введите ваше полное имя (ФИО):"
        )
    
    async def process_full_name(self, message: Message, state: FSMContext):
        """Process entered full name"""
        full_name = message.text.strip()
        
        if len(full_name.split()) < 2:
            await message.answer("Пожалуйста, введите полное имя (ФИО):")
            return
        
        await state.update_data(full_name=full_name)
        await state.set_state(RequestForm.waiting_for_address)
        
        # Keyboard with address options
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Ярцево"),
                    KeyboardButton(text="Дачный посёлок")
                ],
                [
                    KeyboardButton(text="п. Солнечный"),
                    KeyboardButton(text="Другое")
                ]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            "Выберите адрес выполнения работ:",
            reply_markup=keyboard
        )
    
    async def process_address(self, message: Message, state: FSMContext):
        """Process selected address"""
        address = message.text.strip()
        
        # Validate address
        valid_addresses = ["Ярцево", "Дачный посёлок", "п. Солнечный", "Другое"]
        if address not in valid_addresses:
            await message.answer(
                "Пожалуйста, выберите адрес из предложенных вариантов:"
            )
            return
        
        await state.update_data(address=address)
        await state.set_state(RequestForm.waiting_for_service)
        
        # Keyboard with service options
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Ассенизаторские услуги"),
                    KeyboardButton(text="Вызов сантехника")
                ],
                [
                    KeyboardButton(text="Прочистка труб"),
                    KeyboardButton(text="Установка сантехники")
                ]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            "Выберите тип услуги:",
            reply_markup=keyboard
        )
    
    async def process_service(self, message: Message, state: FSMContext):
        """Process selected service type"""
        service_type = message.text.strip()
        
        # Validate service type
        valid_services = ["Ассенизаторские услуги", "Вызов сантехника", "Прочистка труб", "Установка сантехники"]
        if service_type not in valid_services:
            await message.answer(
                "Пожалуйста, выберите тип услуги из предложенных вариантов:"
            )
            return
        
        await state.update_data(service_type=service_type)
        await state.set_state(RequestForm.waiting_for_phone)
        
        # Remove keyboard after service selection
        await message.answer(
            "Введите ваш номер телефона в формате +7XXXXXXXXXX:",
            reply_markup=ReplyKeyboardRemove()
        )
    
    async def process_phone(self, message: Message, state: FSMContext):
        """Process entered phone number"""
        phone = message.text.strip()
        
        # Check phone number format
        phone_pattern = r'^\+7\d{10}$'
        if not re.match(phone_pattern, phone):
            await message.answer(
                "Неверный формат номера телефона. Введите номер в формате +7XXXXXXXXXX:"
            )
            return
        
        # Get data from state
        data = await state.get_data()
        user_id = message.from_user.id
        full_name = data['full_name']
        address = data['address']
        service_type = data['service_type']
        
        # Create request in database
        request_id = self.db.create_request(user_id, full_name, address, service_type, phone)
        
        # Clear state
        await state.clear()
        
        # Send confirmation
        success_message = (
            f"Спасибо, <b>{full_name}</b>! Ваша заявка №{request_id} принята.\n\n"
            f"Адрес: {address}\n"
            f"Услуга: {service_type}\n"
            f"Телефон: {phone}\n\n"
            f"С вами свяжется наш специалист для уточнения деталей.\n\n"
            f"Компания <b>КаналТехСервис</b>, г. Ярцево"
        )
        
        await message.answer(success_message)
    
    async def send_status_update(self, user_id: int, request_id: int, new_status: str, comment: str = None):
        """Send status update to user"""
        try:
            status_message = f"Статус вашей заявки №{request_id} обновлен: <b>{new_status}</b>"
            if comment:
                status_message += f"\nКомментарий: {comment}"
            
            await self.bot.send_message(user_id, status_message)
        except Exception as e:
            logging.error(f"Error sending status update to user {user_id}: {e}")
    
    async def run(self):
        """Run the bot"""
        await self.dp.start_polling(self.bot)