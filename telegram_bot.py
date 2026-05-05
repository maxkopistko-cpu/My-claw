import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from openai import AsyncOpenAI
import httpx

# ====== ENV ======
TELEGRAM_BOT_TOKEN = os.getenv("8705054879:AAH81L8suewyJ6zNxli4qhWDXN4oEdsp9bg")
OPENAI_API_KEY = os.getenv("key_AiJGnGapvxHPPc3K")
GEMINI_API_KEY = os.getenv("AIzaSyAis43SYhCyg0QsP-eLX-4IBvfifpFbrqg")

# ====== Clients ======
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ====== CONFIG ======
MODEL_OPENAI = "gpt-4o-mini"
MODEL_GEMINI = "gemini-1.5-flash"

# ====== CORE ======
async def ask_openai(prompt):
    try:
        resp = await openai_client.chat.completions.create(
            model=MODEL_OPENAI,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
    except Exception as e:
        return None

async def ask_gemini(prompt):
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_GEMINI}:generateContent?key={GEMINI_API_KEY}"
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            r = await client.post(url, json=data, timeout=30)
            result = r.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None

async def run_agent(prompt):
    # 1️⃣ пробуємо OpenAI
    res = await ask_openai(prompt)
    if res:
        return res

    # 2️⃣ fallback на Gemini
    res = await ask_gemini(prompt)
    if res:
        return res

    return "⚠️ Обидві моделі не відповіли. Перевір ключі."

# ====== TELEGRAM ======
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    await update.message.chat.send_action("typing")

    response = await run_agent(user_message)

    await update.message.reply_text(response)

# ====== RUN ======
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🚀 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
