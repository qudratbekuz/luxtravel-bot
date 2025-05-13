import os
import logging
import requests
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
MOFA_URL = "https://visa.mofa.gov.sa/visaservices/searchvisa"  # URLni tekshirish

logging.basicConfig(level=logging.INFO)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum!\nSaudiya vizangizni tekshirish uchun quyidagi tartibda yuboring:\n\n"
                                    "1. Pasport seriyasini\n2. Millat (masalan: UZB)\n3. CAPTCHA kod (keyin rasmni yuboramiz)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {}

    stage = len(user_data[chat_id])

    if stage == 0:
        user_data[chat_id]['passport_series'] = text
        await update.message.reply_text("🌍 Millatingiz kodini yuboring (masalan: UZB):")
    elif stage == 1:
        user_data[chat_id]['nationality'] = text
        # Real CAPTCHA rasmni olish
        captcha_image_url = get_captcha_image()
        # Rasmni yuborish
        await update.message.reply_photo(photo=captcha_image_url)
        await update.message.reply_text("🔐 CAPTCHA kodi (rasmdagi raqamni yozing):")
    elif stage == 2:
        user_data[chat_id]['captcha'] = text
        await update.message.reply_text("✅ Ma'lumotlaringiz qabul qilindi. Tekshiruvga yuboriladi.")
        await check_visa_status(update, context)

async def check_visa_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    passport_series = user_data[chat_id].get('passport_series')
    nationality = user_data[chat_id].get('nationality')
    captcha = user_data[chat_id].get('captcha')

    # Send the data to the MOFA site
    data = {
        'FirstValue': passport_series,
        'SecondValue': '',
        'Nationality': nationality,
        'Captcha': captcha,
    }

    response = requests.post(MOFA_URL, data=data)
    
    if response.status_code == 200:
        # Assuming response contains information on the visa status
        visa_status = response.text  # You will need to parse the actual response
        await update.message.reply_text(f"Viza holati: {visa_status}")  # Send the visa status to the user
    else:
        await update.message.reply_text(f"Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

def get_captcha_image():
    # Real CAPTCHA olish
    # Placeholder rasm URL - uni MOFA saytiga so'rov yuborib olish kerak
    # Buni haqiqiy CAPTCHA olish bilan almashtiring
    captcha_url = "https://visa.mofa.gov.sa/captcha"  # Bu URLni haqiqiy CAPTCHA olish uchun almashtiring
    response = requests.get(captcha_url, stream=True)
    if response.status_code == 200:
        return InputFile(response.raw)  # Bu rasmni yuborish uchun foydalanamiz
    else:
        return "https://via.placeholder.com/150"  # Noto'g'ri rasm bo'lsa, placeholder rasm yuboriladi

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()
