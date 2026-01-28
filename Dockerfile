# Multi-stage build для оптимизации размера образа
FROM python:3.11-slim as builder

WORKDIR /build

# Установить системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копировать requirements и установить зависимости
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ========== FINAL STAGE ==========
FROM python:3.11-slim

WORKDIR /app

# Установить runtime зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копировать Python dependencies из builder
COPY --from=builder /root/.local /root/.local

# Убедиться что pip использует локальные пакеты
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Копировать весь проект
COPY . .

# Создать необходимые директории
RUN mkdir -p /app/logs /app/data && chmod 755 /app/logs /app/data

# Health check для BotHost
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Запустить приложение
CMD ["python", "main.py"]
