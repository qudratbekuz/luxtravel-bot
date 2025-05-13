import os
import logging
import youtube_dl
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Set logging
logging.basicConfig(level=logging.INFO)

# Function to download video from YouTube
def download_youtube_video(url):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # Save to 'downloads' directory with video title
        'format': 'bestvideo+bestaudio/best',  # Best video and audio
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
    return filename

# Function to download video from Instagram
def download_instagram_video(url):
    L = instaloader.Instaloader()
    post = instaloader.Post.from_url(L.context, url)
    filename = f"downloads/{post.shortcode}.mp4"
    post.download(filename)
    return filename

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! \nIltimos, video linkini yuboring (YouTube yoki Instagram):")

# Handler for message (video link)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_url = update.message.text.strip()

    if "youtube" in video_url:
        await update.message.reply_text("YouTube video yuklanmoqda...")
        video_file = download_youtube_video(video_url)
        with open(video_file, 'rb') as video:
            await update.message.reply_video(video)
        os.remove(video_file)  # Remove the file after sending

    elif "instagram" in video_url:
        await update.message.reply_text("Instagram video yuklanmoqda...")
        video_file = download_instagram_video(video_url)
        with open(video_file, 'rb') as video:
            await update.message.reply_video(video)
        os.remove(video_file)  # Remove the file after sending

    else:
        await update.message.reply_text("Iltimos, faqat YouTube yoki Instagram video linklarini yuboring.")

# Main function to start the bot
if __name__ == '__main__':
    bot_token = os.getenv("BOT_TOKEN")  # Enter your bot token
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()
