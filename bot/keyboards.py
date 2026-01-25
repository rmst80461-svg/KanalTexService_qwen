from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_location_keyboard():
    """Клавиатура для выбора адреса"""
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
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_service_keyboard():
    """Клавиатура для выбора типа услуги"""
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
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard