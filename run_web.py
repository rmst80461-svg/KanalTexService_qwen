#!/usr/bin/env python3
"""
Запуск веб-админки для системы управления заявками "КаналТехСервис"
"""
import sys
import os

# Добавляем директорию проекта в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.app import app

if __name__ == "__main__":
    print("Запуск веб-админки 'КаналТехСервис'...")
    print("Админка будет доступна по адресу http://localhost:5000")
    print("Для завершения работы нажмите Ctrl+C")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nВеб-сервер остановлен пользователем")
    except Exception as e:
        print(f"Ошибка при работе веб-сервера: {e}")
        sys.exit(1)