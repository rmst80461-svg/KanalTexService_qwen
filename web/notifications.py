import asyncio
import logging
from aiogram import Bot
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Получение токена бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def send_status_update_to_user(user_id, request_id, new_status, comment=None):
    """Отправка обновления статуса пользователю через бота"""
    if not BOT_TOKEN:
        logging.error("Не установлен BOT_TOKEN в .env файле")
        return False
    
    try:
        bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
        
        status_message = f"Статус вашей заявки №{request_id} обновлен: <b>{new_status}</b>"
        if comment:
            status_message += f"\nКомментарий: {comment}"
        
        await bot.send_message(user_id, status_message)
        await bot.session.close()
        return True
    except Exception as e:
        logging.error(f"Ошибка при отправке обновления статуса пользователю {user_id}: {e}")
        return False

def send_status_update_sync(user_id, request_id, new_status, comment=None):
    """Синхронная версия функции для отправки обновления статуса"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(send_status_update_to_user(user_id, request_id, new_status, comment))
        loop.close()
        return result
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомления: {e}")
        return False