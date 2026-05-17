# 📱 Telegram Monitoring с GitHub Actions

Автоматический мониторинг Telegram чатов через GitHub Actions. Скрипт запускается по расписанию, анализирует сообщения и отправляет уведомления.

---

## 🚀 Быстрый старт

### 1. Добавь GitHub Secrets

Перейди в репозиторий → **Settings** → **Secrets and variables** → **Actions**

Добавь эти секреты:

| Секрет | Значение | Пример |
|--------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от BotFather | `8931863344:AAEGQigojiLiaKTWN1bQV5DC61R7CF9PjqE` |
| `YOUR_CHAT_ID` | Твой личный chat_id (для уведомлений) | `220023136` |
| `MONITORED_CHAT_ID_1` | chat_id группы для мониторинга | `-1001234567890` |

**Как добавить:**
1. Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `TELEGRAM_BOT_TOKEN`
4. Value: (вставь значение)
5. Add secret

---

### 2. Настрой config.py

Отредактируй `telegram-monitoring/config.py`:

```python
# Ключевые слова для поиска
KEYWORDS = [
    "идея",
    "видео",
    "тренд",
    "вирусное",
]

# Расписание (cron формат)
SCHEDULE_CRON = "0 * * * *"  # Каждый час

# Минимум реакций для уведомления
MIN_REACTIONS = 2
```

---

### 3. Запусти вручную

GitHub → Actions → **Telegram Monitor** → **Run workflow**

Если всё работает:
- ✅ Получишь уведомление в личку Telegram
- ✅ Логи будут в GitHub Actions

---

## 🕐 Расписание (cron формат)

```
"0 * * * *"       → каждый час в :00
"*/30 * * * *"    → каждые 30 минут
"0 9 * * *"       → каждый день в 9:00 (UTC)
"0 0 * * 1"       → каждый понедельник в 00:00
"0 */6 * * *"     → каждые 6 часов
```

⏰ **Важно:** GitHub Actions использует UTC. Если нужна твоя часовая зона, добавь смещение в скрипт.

---

## 📋 Мониторинг нескольких чатов

### 1. Добавь в config.py:
```python
MONITORED_CHATS = [
    int(os.getenv("MONITORED_CHAT_ID_1", "0")),
    int(os.getenv("MONITORED_CHAT_ID_2", "0")),
    int(os.getenv("MONITORED_CHAT_ID_3", "0")),
]
```

### 2. Добавь секреты в GitHub:
- `MONITORED_CHAT_ID_1` = `-1001234567890`
- `MONITORED_CHAT_ID_2` = `-1009876543210`
- `MONITORED_CHAT_ID_3` = `987654321`

### 3. Обнови workflow:
```yaml
env:
  TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
  YOUR_CHAT_ID: ${{ secrets.YOUR_CHAT_ID }}
  MONITORED_CHAT_ID_1: ${{ secrets.MONITORED_CHAT_ID_1 }}
  MONITORED_CHAT_ID_2: ${{ secrets.MONITORED_CHAT_ID_2 }}
  MONITORED_CHAT_ID_3: ${{ secrets.MONITORED_CHAT_ID_3 }}
```

---

## 🔧 Как it работает

1. **GitHub Actions запускает скрипт** по расписанию (или вручную)
2. **monitor.py читает** последние сообщения из чатов
3. **Анализирует:**
   - Ключевые слова из KEYWORDS
   - Количество реакций (👍, ❤️, и т.д.)
4. **Отправляет уведомление** в твой личный chat_id, если найдено что-то важное
5. **Логирует результаты** в GitHub Actions

---

## 🧪 Локальное тестирование

Если хочешь тестировать на своём компьютере:

```bash
cd telegram-monitoring

# Установи зависимости
pip install -r requirements.txt

# Установи переменные окружения
export TELEGRAM_BOT_TOKEN="8931863344:AAE..."
export YOUR_CHAT_ID="220023136"
export MONITORED_CHAT_ID_1="-1001234567890"

# Запусти скрипт
python monitor.py
```

---

## 📊 Логи и мониторинг

**Где смотреть логи:**
1. GitHub → Actions → **Telegram Monitor**
2. Выбери последний запуск
3. Раздел **Run Telegram Monitor** покажет все логи

**Что означают символы в логах:**
- ✅ — успешно
- ❌ — ошибка
- ⚠️ — внимание
- 📊 — информация
- 📌 — детали

---

## ❓ Частые ошибки

### "TELEGRAM_BOT_TOKEN не установлен"
→ Проверь GitHub Secrets, правильно ли добавлен `TELEGRAM_BOT_TOKEN`

### "YOUR_CHAT_ID не установлен"
→ Добавь `YOUR_CHAT_ID` в GitHub Secrets

### "Нет чатов для мониторинга"
→ Добавь `MONITORED_CHAT_ID_1` в GitHub Secrets и config.py

### "Нет обновлений" или "Нет сообщений из чата"
→ Убедись, что:
- Бот добавлен в чат как администратор
- Бот имеет право читать сообщения
- В чате есть новые сообщения после добавления бота

### Уведомления не приходят
→ Проверь:
- Личный чат с ботом открыт (отправил `/start`)
- `YOUR_CHAT_ID` правильный (последние 4 цифры совпадают с Telegram)

---

## 🔐 Безопасность

- ✅ Токен хранится в GitHub Secrets (не видно в логах)
- ✅ Исходный код открыт (можешь проверить, что делает скрипт)
- ✅ GitHub Actions работает в изолированной среде
- ⚠️ Не коммитьте токены в код! Используйте только Secrets.

---

## 📝 Примеры использования

### Мониторинг идей для видео
```python
KEYWORDS = ["идея", "видео", "тема", "скрипт"]
MIN_REACTIONS = 3
SCHEDULE_CRON = "0 * * * *"  # каждый час
```

### Отслеживание вопросов аудитории
```python
KEYWORDS = ["вопрос", "как", "почему", "что", "помощь"]
MIN_REACTIONS = 1
SCHEDULE_CRON = "*/30 * * * *"  # каждые 30 минут
```

### Еженедельный дайджест
```python
SCHEDULE_CRON = "0 9 * * 1"  # понедельник в 9:00 UTC
```

---

## 🚨 Дополнительные возможности

### Отправка уведомлений в формате
Отредактируй функцию `format_notification()` в `monitor.py` для кастомизации.

### Сохранение в Knowledge Base
Можно расширить скрипт, чтобы он сохранял важные сообщения в файлы.

### Интеграция с другими сервисами
Добавь отправку в Slack, Discord, Email и т.д.

---

**Всё работает? Отлично! 🎉**  
Мониторинг запущен и будет работать автоматически по расписанию.
