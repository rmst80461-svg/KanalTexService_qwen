#!/usr/bin/env python3
"""
Скрипт для генерации хеша пароля администратора
"""

from werkzeug.security import generate_password_hash
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_admin_password.py <password>")
        print("Example: python create_admin_password.py mysecretpassword")
        return
    
    password = sys.argv[1]
    password_hash = generate_password_hash(password)
    
    print(f"Password hash for '{password}':")
    print(password_hash)
    
    # Также выводим строку для вставки в .env файл
    print("\nAdd this to your .env file:")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")

if __name__ == "__main__":
    main()