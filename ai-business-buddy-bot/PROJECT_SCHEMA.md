# Схема проекта AI Business Buddy Bot

## Архитектура проекта

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI Business Buddy Bot                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Telegram Bot   │    │  Temporal       │
│   (main.py)     │◄──►│   (bot.py)      │◄──►│   Worker        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Handlers      │    │   Workflows     │    │   Activities    │
│ (handlers.py)   │    │(user_onboarding)│    │ (llm/db/msg)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   LangChain     │    │   External      │
│   (MongoDB)     │    │   (LLM Chain)   │    │   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Детальная схема связей

### 1. Точка входа - FastAPI приложение (`main.py`)
```
main.py
├── Запускает FastAPI сервер
├── Настраивает webhook для Telegram
├── Подключает роутер handlers
└── Обрабатывает входящие webhook'и от Telegram
```

### 2. Telegram интеграция
```
telegram/
├── bot.py - Создает экземпляр бота и диспетчера
└── handlers.py - Обработчики сообщений
    ├── /start - Начало опроса
    └── handle_text_message - Обработка ответов пользователя
```

### 3. Temporal Workflow Engine
```
temporal_client/
└── client.py
    ├── start_user_workflow() - Запуск workflow для пользователя
    └── get_temporal_client() - Получение клиента Temporal

workflows/
└── user_onboarding.py - Основной workflow опроса
    ├── run() - Основная логика опроса
    └── submit_answer() - Сигнал для получения ответа
```

### 4. Activities (Активности)
```
workflows/activities/
├── llm.py - Работа с AI
│   ├── generate_welcome_message() - Приветственное сообщение
│   ├── detect_language() - Определение языка
│   └── get_next_question() - Генерация следующего вопроса
├── messaging.py - Отправка сообщений
│   └── send_message() - Отправка в Telegram
└── db.py - Работа с базой данных
    ├── save_answer() - Сохранение ответа
    ├── set_user_language() - Установка языка
    ├── save_user_email() - Сохранение email
    └── mark_survey_complete() - Завершение опроса
```

### 5. База данных
```
database/
└── mongo.py
    ├── Подключение к MongoDB
    └── Коллекция users_collection
```

### 6. LangChain интеграция
```
langchain/
└── llm_chain.py
    ├── Настройка LLM (OpenAI GPT-4)
    ├── Промпт шаблон
    └── get_conversation_chain() - Цепочка с историей
```

### 7. Worker процесс
```
worker.py
├── Подключение к Temporal
├── Регистрация workflow и activities
└── Запуск worker'а для обработки задач
```

## Поток данных

### 1. Начало опроса (/start)
```
Пользователь → Telegram → handlers.py → 
start_user_workflow() → UserOnboardingWorkflow.run() → 
generate_welcome_message() → send_message() → Пользователь
```

### 2. Обработка ответа
```
Пользователь → Telegram → handlers.py → 
submit_answer() → UserOnboardingWorkflow → 
get_next_question() → send_message() → Пользователь
```

### 3. Сохранение данных
```
UserOnboardingWorkflow → save_answer() → MongoDB
UserOnboardingWorkflow → set_user_language() → MongoDB
UserOnboardingWorkflow → save_user_email() → MongoDB
```

## Ключевые технологии

- **FastAPI** - Web framework для API
- **aiogram** - Telegram Bot API библиотека
- **Temporal** - Workflow engine для оркестрации процессов
- **MongoDB** - База данных
- **LangChain** - Интеграция с LLM
- **OpenAI GPT-4** - AI модель
- **PyMongo** - MongoDB драйвер

## Переменные окружения

- `TELEGRAM_BOT_TOKEN` - Токен Telegram бота
- `TEMPORAL_ADDRESS` - Адрес Temporal сервера
- `MONGO_URI` - URI подключения к MongoDB
- `OPENAI_API_KEY` - API ключ OpenAI
- `WEBHOOK_URL` - URL для webhook'а

## Запуск проекта

1. **FastAPI сервер**: `python -m app.main`
2. **Temporal Worker**: `python -m app.worker`
3. **Temporal сервер**: Должен быть запущен отдельно
4. **MongoDB**: Должна быть запущена 