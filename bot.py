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

        usage = data.get("usage", {})
        tokens_used = usage.get("tokens_used", 0)
        balance_usd = data.get("balance_usd", 0)
        total_spent = data.get("total_spent_usd", 0)
        per_model = data.get("per_model", {})

        lines = [
            "📊 Баланс ключа",
            "",
            f"Статус: {data.get('status', 'N/A')}",
            f"План: {data.get('plan', 'N/A')}",
            f"Баланс: ${balance_usd:,.2f}",
            f"Потрачено всего: ${total_spent:,.2f}",
            f"Токенов использовано: {tokens_used:,}",
        ]

        if per_model:
            lines.append("")
            lines.append("По моделям:")
            for model, stats in per_model.items():
                lines.append(
                    f"• {model}: in {stats.get('input_tokens', 0):,} / "
                    f"out {stats.get('output_tokens', 0):,} — "
                    f"${stats.get('spent_usd', 0):,.2f}"
                )

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
