#!/usr/bin/env python3
"""
Telegram Monitoring Script
Читает сообщения из чатов и отправляет уведомления
"""

import requests
import json
from datetime import datetime
from config import (
    BOT_TOKEN,
    YOUR_CHAT_ID,
    MONITORED_CHATS,
    MESSAGES_LIMIT,
    TIMEOUT,
    KEYWORDS,
    MIN_REACTIONS,
)


class TelegramMonitor:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id, text):
        """Отправить сообщение в Telegram"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            }
            response = requests.post(url, json=data, timeout=TIMEOUT)
            response.raise_for_status()
            print(f"✅ Сообщение отправлено в чат {chat_id}")
            return True
        except Exception as e:
            print(f"❌ Ошибка при отправке сообщения: {e}")
            return False

    def get_updates(self):
        """Получить последние обновления"""
        try:
            url = f"{self.api_url}/getUpdates"
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if data.get("ok"):
                return data.get("result", [])
            return []
        except Exception as e:
            print(f"❌ Ошибка при получении обновлений: {e}")
            return []

    def get_chat_info(self, chat_id):
        """Получить информацию о чате"""
        try:
            url = f"{self.api_url}/getChat"
            data = {"chat_id": chat_id}
            response = requests.post(url, json=data, timeout=TIMEOUT)
            response.raise_for_status()
            result = response.json()
            if result.get("ok"):
                return result.get("result")
            return None
        except Exception as e:
            print(f"❌ Ошибка при получении информации о чате: {e}")
            return None

    def analyze_messages(self, chat_id):
        """Анализировать сообщения в чате"""
        print(f"\n📊 Анализирую чат {chat_id}...")

        updates = self.get_updates()
        if not updates:
            print("⚠️ Нет обновлений")
            return None

        # Фильтруем сообщения из нужного чата
        chat_messages = [
            u["message"]
            for u in updates
            if u.get("message") and u["message"].get("chat", {}).get("id") == chat_id
        ]

        if not chat_messages:
            print(f"⚠️ Нет сообщений из чата {chat_id}")
            return None

        # Берём последние N сообщений
        recent_messages = sorted(
            chat_messages, key=lambda m: m.get("date", 0), reverse=True
        )[:MESSAGES_LIMIT]

        print(f"📌 Найдено {len(recent_messages)} последних сообщений")

        # Анализируем
        important_messages = []
        for msg in recent_messages:
            text = msg.get("text", "").lower()
            from_user = msg.get("from", {})
            reactions = msg.get("reaction_count", 0)

            # Проверяем ключевые слова или реакции
            has_keywords = any(kw in text for kw in KEYWORDS)
            has_reactions = reactions >= MIN_REACTIONS

            if has_keywords or has_reactions:
                important_messages.append(
                    {
                        "text": msg.get("text", ""),
                        "from": from_user.get("first_name", "Unknown"),
                        "date": datetime.fromtimestamp(msg.get("date")).strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "reactions": reactions,
                        "has_keywords": has_keywords,
                    }
                )

        return important_messages

    def format_notification(self, chat_id, messages):
        """Форматировать уведомление"""
        if not messages:
            return None

        chat_info = self.get_chat_info(chat_id)
        chat_name = (
            chat_info.get("title") if chat_info else f"Чат {chat_id}"
        )

        notification = f"<b>📢 Важные сообщения из '{chat_name}':</b>\n\n"

        for i, msg in enumerate(messages[:5], 1):  # Максимум 5 сообщений
            notification += f"<b>{i}.</b> "
            notification += f"<code>{msg['date']}</code> "
            notification += f"({msg['from']})\n"

            text_preview = msg["text"][:100]
            if len(msg["text"]) > 100:
                text_preview += "..."

            notification += f"{text_preview}\n"

            if msg["reactions"] > 0:
                notification += f"👍 Реакций: {msg['reactions']}\n"

            if msg["has_keywords"]:
                notification += "⭐ Содержит ключевые слова\n"

            notification += "\n"

        return notification

    def run(self):
        """Запустить мониторинг"""
        print("\n" + "=" * 50)
        print(f"⏱️  Запуск мониторинга: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        if not BOT_TOKEN:
            print("❌ ОШИБКА: TELEGRAM_BOT_TOKEN не установлен!")
            return False

        if not YOUR_CHAT_ID or YOUR_CHAT_ID == 0:
            print("❌ ОШИБКА: YOUR_CHAT_ID не установлен!")
            return False

        if not MONITORED_CHATS:
            print("⚠️  ВНИМАНИЕ: Нет чатов для мониторинга (MONITORED_CHATS пуст)")
            return False

        success_count = 0

        for chat_id in MONITORED_CHATS:
            try:
                messages = self.analyze_messages(chat_id)

                if messages:
                    notification = self.format_notification(chat_id, messages)
                    if notification:
                        self.send_message(YOUR_CHAT_ID, notification)
                        success_count += 1
                else:
                    print(f"ℹ️  Нет новых важных сообщений в чате {chat_id}")

            except Exception as e:
                print(f"❌ Ошибка при обработке чата {chat_id}: {e}")

        print("\n" + "=" * 50)
        print(f"✅ Завершено. Обработано чатов: {len(MONITORED_CHATS)}")
        print(f"📬 Отправлено уведомлений: {success_count}")
        print("=" * 50 + "\n")

        return True


if __name__ == "__main__":
    monitor = TelegramMonitor(BOT_TOKEN)
    monitor.run()
