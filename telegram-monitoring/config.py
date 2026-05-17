# Telegram Bot Configuration
import os

# Telegram Bot Token (получить из BotFather)
# Сохранить в GitHub Secrets как TELEGRAM_BOT_TOKEN
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Твой личный chat_id (для уведомлений)
# Получить через /getUpdates
YOUR_CHAT_ID = int(os.getenv("YOUR_CHAT_ID", "0"))

# Chat ID для мониторинга (группа, канал или чат)
# Может быть список для мониторинга нескольких чатов
MONITORED_CHATS = [
    # int(os.getenv("MONITORED_CHAT_ID_1", "0")),
    # Добавляй сюда chat_id'ы групп/каналов
]

# Расписание запуска (cron формат)
# "0 * * * *" - каждый час
# "*/30 * * * *" - каждые 30 минут
# "0 9 * * *" - каждый день в 9:00
SCHEDULE_CRON = "0 * * * *"

# Параметры мониторинга
MESSAGES_LIMIT = 20  # Сколько последних сообщений читать
TIMEOUT = 10  # Таймаут для API запросов (секунды)

# Ключевые слова для поиска (опционально)
KEYWORDS = [
    "идея",
    "видео",
    "тренд",
    "вирусное",
    "важное",
]

# Минимальное количество реакций для уведомления
MIN_REACTIONS = 2
