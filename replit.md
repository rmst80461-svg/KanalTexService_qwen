# KanalTechService Bot

## Overview
KanalTechService (КаналТехСервис) is a Telegram bot and web admin panel for a sanitary and sewage services company based in Yartsevo, Smolensk region, Russia.

## Features
- Telegram bot for customer service (order placement, pricing info, FAQ, contacts)
- Flask web admin panel for managing orders
- SQLite database for storing users, orders, and reviews

## Project Structure
```
├── main.py                 # Main entry point
├── app/
│   ├── bot/               # Telegram bot handlers and keyboards
│   ├── config/            # Configuration module
│   ├── models/            # Database models
│   ├── utils/             # Utility functions (prices)
│   └── web/               # Flask web routes
├── templates/             # HTML templates for web panel
└── assets/                # Static assets (logo)
```

## Running the Application
The application runs on port 5000 and serves:
- Web admin panel via Flask
- Telegram bot (when BOT_TOKEN is configured)

## Required Environment Variables/Secrets
- `BOT_TOKEN` - Telegram bot token from @BotFather (required for bot functionality)
- `ADMIN_IDS` - Comma-separated Telegram user IDs for admin access
- `FLASK_SECRET_KEY` - Secret key for Flask sessions
- `ADMIN_PASSWORD` - Password for web admin panel (default: admin123)

## Optional Environment Variables
- `COMPANY_NAME` - Company name (default: КаналТехСервис)
- `COMPANY_PHONE` - Company phone number
- `COMPANY_EMAIL` - Company email
- `COMPANY_CITY` - Company city (default: Ярцево)
- `LOG_LEVEL` - Logging level (default: INFO)

## Database
Uses SQLite (botdata.db) with tables:
- users - Telegram users
- orders - Service orders
- reviews - Customer reviews

## Deployment
For production deployment, use gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port "app.web.routes:create_app(None, None)"
```

## Web Admin Panel Features
- Session-based password authentication with login/logout
- Stats dashboard with order counts by status
- Table of orders with filtering by status
- Change order status (В работу, Отменить)
- Delete orders via API
- Responsive modern design

## Telegram Admin Panel Features
- View orders by status (new, in progress, completed, cancelled)
- Change order status with inline buttons
- Forward orders to executors by Telegram ID
- Delete orders
- View client order history
- Broadcast messages to all users
- Settings panel with executor and price info

## Bot Features
- AI assistant "Аква" (female voice) guides customers
- Service selection and order placement
- Order confirmation with address, phone, optional comment
- Status notifications to customers

## Recent Changes (Jan 2026)
- Added web admin panel with password authentication
- Login page at /login, logout at /logout
- API routes with authorization: /api/orders, /api/orders/:id/status, /api/orders/:id
- Added full Telegram admin panel with order management
- Broadcast messaging to all users
- Order deletion functionality
- Client order history viewing
- Settings panel for executors and prices
- Executor forwarding system with "Take to work" button
- Configured for Replit environment
- Flask runs on port 5000
- Application works in web-only mode if BOT_TOKEN is not provided
