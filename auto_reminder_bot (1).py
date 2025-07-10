import logging
import pandas as pd
from datetime import datetime, timedelta
from telegram import Bot
from telegram.error import TelegramError
import asyncio
import os

# Telegram bot token
TELEGRAM_TOKEN = "7750047008:AAF6MpNIoxQNlsBAGfC7h9ggWraRYYwsf30"
CHAT_ID = "@power_1n"  # або numeric ID

# Шлях до Excel-файлу
EXCEL_FILE = "AUTO IT ASSICURAZIONE E REVISIONE.xlsx"

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Дні, коли потрібно нагадувати
REMINDER_DAYS = [30, 15, 7, 1]

async def send_reminders():
    try:
        bot = Bot(token=TELEGRAM_TOKEN)

        df = pd.read_excel(EXCEL_FILE)
        today = datetime.today().date()

        messages = []

        for _, row in df.iterrows():
            modello = str(row.get("Modello", "N/D"))
            targa = str(row.get("Targa", "N/D"))
            proprietario = str(row.get("Proprietario", "N/D"))

            for field, label in [("Revisione scade", "Техогляд"), ("Assicurazione", "Страхування")]:
                date_str = row.get(field)
                if pd.isnull(date_str):
                    continue
                
                try:
                    if isinstance(date_str, str):
                        date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
                    else:
                        date_obj = pd.to_datetime(date_str).date()
                except Exception as e:
                    logger.warning(f"Неправильна дата у полі '{field}': {date_str}")
                    continue

                days_left = (date_obj - today).days
                if days_left in REMINDER_DAYS:
                    messages.append(f"\ud83d\ude97 <b>{modello} ({targa})</b>\n\u26a1 {label} закінчується через <b>{days_left} дн.</b> ({date_obj.strftime('%d.%m.%Y')})\n\ud83d\udc64 Власник: {proprietario}")

        if messages:
            for msg in messages:
                await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
        else:
            logger.info("Сьогодні немає нагадувань.")

    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(send_reminders())
