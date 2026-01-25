#!/usr/bin/env python3
"""
Запуск Telegram-бота для системы управления заявками "КаналТехСервис"
"""
import asyncio
import sys
import os

# Добавляем директорию проекта в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.main import main

if __name__ == "__main__":
    print("Запуск Telegram-бота 'КаналТехСервис'...")
    print("Для завершения работы нажмите Ctrl+C")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"Ошибка при работе бота: {e}")
        sys.exit(1)