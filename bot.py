import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8778052231:AAFIvi8T4FUKQBrUkc45wQbZGB-X0BeGvI4")
GNGN_API_URL = "https://api.east-api-3.org/v1/key/info"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне API-ключ (начинается с sk-) — покажу баланс."
    )


async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_key = update.message.text.strip()

    if not api_key.startswith("sk-"):
        await update.message.reply_text("Отправь валидный API-ключ (начинается с sk-)")
        return

    try:
        response = requests.get(
            GNGN_API_URL,
            headers={"x-api-key": api_key},
            timeout=10,
        )
        data = response.json()

        if "error" in data:
            await update.message.reply_text(f"Ошибка: {data.get('error')}")
            return

        credits_balance = data.get("credits_balance", 0)
        credits_consumed = data.get("credits_consumed", 0)
        input_tokens = data.get("input_tokens", 0)
        output_tokens = data.get("output_tokens", 0)
        balance_usd = credits_balance
        spent_usd = credits_consumed

        lines = [
            "📊 Баланс ключа",
            "",
            f"Статус: {data.get('status', 'N/A')}",
            f"Владелец: {data.get('name', 'N/A')}",
            f"Баланс: ${balance_usd:,.2f}",
            f"Потрачено: ${spent_usd:,.4f}",
            f"Input токенов: {input_tokens:,}",
            f"Output токенов: {output_tokens:,}",
            f"Запросов: {data.get('requests_total', 0):,}",
        ]

        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"Ошибка при получении баланса: {e}")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_balance))
    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
