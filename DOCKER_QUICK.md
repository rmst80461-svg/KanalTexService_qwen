# ⚡ Docker для BotHost за 1 минуту

## 📦 Что создалось

```
✅ Dockerfile        → Контейнер с Flask + Telegram ботом на порту 5000
✅ .dockerignore     → Исключает ненужные файлы
✅ requirements.txt  → Все зависимости уже есть
✅ .env              → Конфигурация
```

---

## 🚀 За 3 шага запуститься на BotHost

### 1. Git Push
```bash
git add .
git commit -m "Add Docker"
git push origin main
```

### 2. BotHost
- Откройте панель BotHost
- Нажмите **Deploy** или **Rebuild**
- Дождитесь сборки (5-10 минут)

### 3. Проверьте
```
https://your-project.bothost.ru:5000

Логин: admin
Пароль: 12345
```

---

## 🔧 Конфигурация BotHost

**Environment Variables (опционально, если нет `.env`):**
```
BOT_TOKEN=8039974939:AAF...
ADMIN_IDS=12345
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$2b$12$...
ENVIRONMENT=production
PORT=5000
```

---

## 📊 Структура Docker образа

```
🐳 Docker Image (300-400 MB)
  ├─ Python 3.11 slim ✓
  ├─ Requirements (Flask, aiogram, etc) ✓
  ├─ App code (main.py, app/) ✓
  ├─ Логи и данные /app/logs, /app/data ✓
  └─ Health check + автоперезапуск ✓
```

---

## ✅ Признаки что всё работает

**Логи BotHost:**
```
📄 Loading .env from project root: /app/.env
✓ BOT_TOKEN loaded (starts with: 8039974939:AA...)
✓ Telegram bot initialized successfully
🚀 Ready to start!
```

**Web админка:**
- https://your-project.bothost.ru:5000 ✓
- Логин/пароль работают ✓
- Бот отвечает в Telegram ✓

---

## 🐛 Если не работает

1. **Посмотрите логи BotHost** → там будут детали ошибок
2. **Проверьте .env** → токен скопирован полностью?
3. **Restart в панели BotHost** → иногда помогает
4. **См. TROUBLESHOOTING.md** → детальное решение

---

**Подробнее:** `DOCKER_BOTHOST.md`
