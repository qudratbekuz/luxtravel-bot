import os
import logging
import requests
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Environment variables for bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
MOFA_URL = "https://visa.mofa.gov.sa/visaservices/searchvisa"  # URLni tekshirish

logging.basicConfig(level=logging.INFO)

user_data = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Va Rahmatulloh\nSaudiya vizangizni tekshirish uchun quyidagi tartibda yuboring:\n\n"
        "1. Pasport seriyasini\n2. Millat (masalan: UZB)\n3. CAPTCHA kodi (keyin rasmni yuboramiz)"
    )

# Handle user messages (step-by-step)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {}

    stage = len(user_data[chat_id])

    # Step 1: Passport series
    if stage == 0:
        user_data[chat_id]['passport_series'] = text
        await update.message.reply_text("🌍 Millatingiz kodini yuboring (masalan: UZB):")

    # Step 2: Nationality
    elif stage == 1:
        user_data[chat_id]['nationality'] = text
        # Get and send CAPTCHA image
        captcha_image_url = get_captcha_image()
        await update.message.reply_photo(photo=captcha_image_url)
        await update.message.reply_text("🔐 CAPTCHA kodi (rasmdagi raqamni yozing):")

    # Step 3: CAPTCHA
    elif stage == 2:
        user_data[chat_id]['captcha'] = text
        await update.message.reply_text("✅ Ma'lumotlaringiz qabul qilindi. Tekshiruvga yuboriladi.")
        # Send data to MOFA site and check visa status
        await check_visa_status(update, context)

# Check visa status by sending data to MOFA site
async def check_visa_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    passport_series = user_data[chat_id].get('passport_series')
    nationality = user_data[chat_id].get('nationality')
    captcha = user_data[chat_id].get('captcha')

    # Prepare data to send to MOFA
    data = {
        'FirstValue': passport_series,
        'SecondValue': '',
        'Nationality': nationality,
        'Captcha': captcha,
    }

    # Send request to MOFA
    response = requests.post(MOFA_URL, data=data)
    
    if response.status_code == 200:
        # Process and send the visa status to the user
        visa_status = response.text  # You will need to parse the actual response if needed
        await update.message.reply_text(f"Viza holati: {visa_status}")
    else:
        await update.message.reply_text(f"Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# Function to get the CAPTCHA image (Placeholder for now)
def get_captcha_image():
    # Placeholder: Replace with real CAPTCHA fetching logic
    captcha_url = "https://visa.mofa.gov.sa/captcha"  # Actual URL for CAPTCHA image
    response = requests.get(captcha_url, stream=True)
    if response.status_code == 200:
        return InputFile(response.raw)  # Return the CAPTCHA image for Telegram
    else:
        return "https://via.placeholder.com/150"  # If CAPTCHA image fetch fails, use a placeholder

# Main function to run the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()
