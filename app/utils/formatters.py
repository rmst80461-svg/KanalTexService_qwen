"""Утилиты для форматирования данных в боте КаналТехСервис."""
from datetime import datetime
from typing import Optional


def format_order_id(order_id: int) -> str:
    """Форматирование ID заказа с ведущими нулями.
    
    Args:
        order_id: ID заказа
    
    Returns:
        Отформатированный ID (например: #0042)
    """
    return f"#{order_id:04d}"


def format_price(price: float) -> str:
    """Форматирование цены.
    
    Args:
        price: Цена
    
    Returns:
        Отформатированная цена (например: 2 500 руб.)
    """
    if price == 0:
        return "Бесплатно"
    return f"{price:,.0f} руб.".replace(',', ' ')


def format_datetime(dt: datetime) -> str:
    """Форматирование даты и времени.
    
    Args:
        dt: Объект datetime
    
    Returns:
        Отформатированная дата (например: 29.01.2026 12:30)
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt
    
    return dt.strftime("%d.%m.%Y %H:%M")


def format_phone(phone: Optional[str]) -> str:
    """Форматирование номера телефона.
    
    Args:
        phone: Номер телефона
    
    Returns:
        Отформатированный номер (например: +7 (900) 123-45-67)
    """
    if not phone:
        return "не указан"
    
    # Убираем все символы кроме цифр
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) == 11 and digits[0] == '7':
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    elif len(digits) == 10:
        return f"+7 ({digits[0:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"
    
    return phone


def get_status_emoji(status: str) -> str:
    """Получить эмодзи для статуса заказа.
    
    Args:
        status: Статус заказа
    
    Returns:
        Эмодзи статуса
    """
    emoji_map = {
        'new': '🆕',
        'accepted': '✅',
        'in_progress': '🔧',
        'completed': '✔️',
        'cancelled': '❌'
    }
    return emoji_map.get(status, '❓')


def get_status_text(status: str) -> str:
    """Получить текстовое описание статуса.
    
    Args:
        status: Статус заказа
    
    Returns:
        Текст статуса
    """
    text_map = {
        'new': 'Новый',
        'accepted': 'Принят',
        'in_progress': 'Выполняется',
        'completed': 'Завершен',
        'cancelled': 'Отменен'
    }
    return text_map.get(status, 'Неизвестно')


def truncate_text(text: str, max_length: int = 100) -> str:
    """Обрезать текст до указанной длины.
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
    
    Returns:
        Обрезанный текст с многоточием
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
