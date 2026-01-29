# 🚀 Полная инструкция для BotHost

**Проект:** КаналТехСервис Bot  
**Дата:** 29 января 2026  
**Статус:** ✅ Готов к деплою (18/18 пунктов выполнено)

---

## 📁 ШАГ 1: НАСТРОЙКА BOTHOST

### 1.1 Открыть BotHost Panel

1. Перейти на **https://bothost.ru**
2. Войти в личный кабинет
3. Найти ваш проект или создать новый

### 1.2 Конектировать GitHub Repository

```
Сеттингс (Settings) → GitHub → Connect Repository

Repository URL: https://github.com/rmst80461-svg/KanalTexService_qwen.git
Branch: main
```

---

## 📧 ШАГ 2: НАСТРОЙКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ

### 2.1 Environment Variables (Settings → Environment Variables)

**Обязательные:**

```
KLUCH              ZNAЧENIE
===========================================
BOT_TOKEN          [YOUR_BOT_TOKEN]
ADMIN_IDS          123456789
PORT               5000
```

**Опциональные:**

```
DATABASE_URL       sqlite:///botdata.db
FLASK_SECRET_KEY   [AUTO_GENERATED]
LOG_LEVEL          INFO
```

### 2.2 Получить BOT_TOKEN

1. Открыть Telegram
2. Появить @BotFather
3. Написать **/mybots**
4. Выбрать КаналТехСервис Bot
5. **API Token** → Копировать токен
6. Пастить в BotHost: **Environment Variables** → **BOT_TOKEN**

### 2.3 Получить свое ПОЛЬЗОВАТЕЛМ ADMIN ID

1. Открыть Telegram
2. Появить @userinfobot
3. Написать **/start**
4. Копировать ваше **User ID**
5. Пастить в BotHost: **ADMIN_IDS = YOUR_USER_ID**

---

## 👩‍💻 ШАГ 3: НАстОЙКА ПРИЛОЖЕНИЯ

### 3.1 Procfile (BotHost использует этот файл)

**Проверить наличие:**

```bash
cat Procfile
```

**Ожидаемые содержимое:**

```
web: python main.py
```

### 3.2 requirements.txt

**Обязательные библиотеки:**

```bash
python-telegram-bot[all]>=20.0
Flask>=2.0.0
Flask-CORS>=3.0.10
python-dotenv>=0.19.0
requests>=2.28.0
```

---

## 🚀 ШАГ 4: ЗАПУСК НА BOTHOST

### 4.1 Нажать Кнопку ПСтарта

```
Settings → Deployment → Start / Deploy
```

### 4.2 Потребовать Restart

```
Dashboard → Restart Button
```

### 4.3 Отслеживать Логи

```
Settings → Logs
```

---

## ✅ ШАГ 5: ПРОВЕРКА

### 5.1 ПОПровать БОТ В TELEGRAM

1. Открыть Telegram
2. Найти ваш бот: **@KanalTexService_bot** (или ваше имя)
3. Нажать **/start**

### 5.2 Ожидаемые Результаты

```
✅ Сообщение с логотипом (если assets/logo.jpg есть)
✅ Приветственное сообщение
✅ Кнопка "☰ Меню" внизу
✅ Главное меню инлайн кнопок
```

### 5.3 Проверить Основные Функции

**Нанжать кнопки:**

- 📋 Услуги → Выбор категорий ✅
- ➕ Новая заявка → Меню услуг ✅
- 🔍 Статус ✅
- ❓ FAQ → Все вопросы доступны ✅
- 📍 Контакты ✅

---

## 🛠 ОПЦИОНАЛЬНО: ГОСОДНОе НАВЕДЕНИЕ

### Добавить Логотип

1. Сохранить Логотип КаналТехСервис
2. Переименовать в `logo.jpg`
3. Сохранить в папке `assets/`
4. Коммит и пуш в GitHub
5. BotHost автоматически тянет и рестартит

---

## 💡 ОткарОвКА ОШИБОК

### Ошибка: "Unauthorized (401)"

✅ **Решение:**
1. Проверить BOT_TOKEN в Environment Variables
2. Проверить активен ли бот у @BotFather
3. Нажать **Restart**

### Ошибка: "Кнопки не работают"

✅ **Решение:**
1. Проверить Логи (Settings → Logs)
2. Поискать ErrorHTTP 404 или 500
3. Гарантированные, что Procfile содержит: `web: python main.py`

### Ошибка: "Логотип не отображается"

✅ **Решение:**
1. Добавить `assets/logo.jpg`
2. Нажать **Deploy** дожидаться выполнения
3. Нажать **Restart**

---

## 📁 УПОЛНОВУОЧНАЯ ПОРОВКА

### Структура Проекта

```
KanalTexService_qwen/
├── main.py                     ✅ Entry point
├── Procfile                    ✅ BotHost конфигурация
├── requirements.txt            ✅ Не забывать зависимости
├── .env.example               ✅ Шаблон настроек
├── .env                       ✅ НЕ КОММИТИТЬ! Только BotHost
├── assets/
│   ├── logo.jpg                 ✅ Логотип КаналТехСервис
│   └── .gitkeep
├── app/
│   ├── bot/                     ✅ Модуль телеграм бота
│   ├── models/                 ✅ Модели базы данных
│   ├── utils/                  ✅ Утилиты
│   ├── config/                 ✅ Конфигурация
│   ├── web/                    ✅ Flask веб-приложение
│   └── __init__.py
├── COMPLETION_REPORT.md       ✅ Отчет о выполнении
└── BOTHOST_DEPLOYMENT.md      ✅ Эта инструкция
```

---

## 📄 ПОЛЕЗНЫЕ ЛИНКИ

- 🛠 **BotHost Panel:** https://bothost.ru
- 🚫 **@BotFather:** https://t.me/botfather
- 📧 **User Info Bot:** https://t.me/userinfobot
- 📚 **Telegram Bot API:** https://core.telegram.org/bots/api

---

## 🌈 КОНТАКТЫ КАНАЛ ТЕХ СЕРВИС

📞 **Поддержка:** +7 (910) 555-84-14  
📧 **Email:** info@kanalteh.ru  
🏠 **Адрес:** г. Ярцево, Смоленская область  
⏰ **Режим:** 24/7  

---

## ✅ ГОТОВО!

После выполнения этих шагов ваш бот КаналТехСервис должен быть активен и готов к работе!

🚀 **Успехов!**
