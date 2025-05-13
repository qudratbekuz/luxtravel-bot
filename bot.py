import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum!\nSaudiya vizangizni tekshirish uchun quyidagi tartibda yuboring:\n\n"
                                    "1. Viza raqami\n2. Pasport raqami\n3. Millat (UZB)\n4. CAPTCHA kod (keyin qo‘shamiz)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {}

    stage = len(user_data[chat_id])

    if stage == 0:
        user_data[chat_id]['visa_number'] = text
        await update.message.reply_text("✅ Pasport raqamingizni yuboring:")
    elif stage == 1:
        user_data[chat_id]['passport_number'] = text
        await update.message.reply_text("🌍 Millatingiz kodini yuboring (masalan: UZB):")
    elif stage == 2:
        user_data[chat_id]['nationality'] = text
        await update.message.reply_text("🔐 CAPTCHA kodi (keyingi bosqichda rasm bilan bo‘ladi)")
    else:
        await update.message.reply_text("✅ Rahmat. Ma'lumotlar qabul qilindi. Keyingi bosqichga o‘tamiz.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()
