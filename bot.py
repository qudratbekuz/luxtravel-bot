import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
MOFA_URL = "https://visa.mofa.gov.sa/visaservices/searchvisa"  # Bu yerni to'ldirishimiz kerak

logging.basicConfig(level=logging.INFO)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum!\nSaudiya vizangizni tekshirish uchun quyidagi tartibda yuboring:\n\n"
                                    "1. Pasport raqami\n2. Millat (UZB)\n3. CAPTCHA kod (keyin rasmni yuboramiz)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {}

    stage = len(user_data[chat_id])

    if stage == 0:
        user_data[chat_id]['passport_number'] = text
        await update.message.reply_text("🌍 Millatingiz kodini yuboring (masalan: UZB):")
    elif stage == 1:
        user_data[chat_id]['nationality'] = text
        await update.message.reply_text("🔐 CAPTCHA kodi (keyin rasmni yuboramiz):")
    elif stage == 2:
        user_data[chat_id]['captcha'] = text
        await update.message.reply_text("✅ Ma'lumotlaringiz qabul qilindi. Tekshiruvga yuboriladi.")
        # Now, we'll send the information to MOFA and check the visa status.
        await check_visa_status(update, context)

async def check_visa_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    passport_number = user_data[chat_id].get('passport_number')
    nationality = user_data[chat_id].get('nationality')
    captcha = user_data[chat_id].get('captcha')

    # Send the data to the MOFA site
    data = {
        'FirstValue': passport_number,
        'SecondValue': '',
        'Nationality': nationality,
        'Captcha': captcha,
    }

    response = requests.post(MOFA_URL, data=data)
    # Handle the response (assuming a simple success/failure check here)
    if response.status_code == 200:
        # Parse the response if it contains information on the visa status
        await update.message.reply_text(f"Viza holati: muvaffaqiyatli tekshirildi!")
    else:
        await update.message.reply_text(f"Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()
