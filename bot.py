import os
import asyncio
from flask import Flask
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update, InputFile
from dotenv import load_dotenv
from basicsr_test import enhance_image
from uuid import uuid4

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Remini Bot is Running!"

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Remini Bot!\n\n📸 Please send a photo you want to enhance using AI."
    )

# ✅ Photo handler
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    photo_file = await update.message.photo[-1].get_file()

    uid = str(uuid4())
    input_path = f"input_{uid}.jpg"
    output_path = f"enhanced_{uid}.jpg"

    await photo_file.download_to_drive(input_path)
    await update.message.reply_text("✨ Enhancing your photo... Please wait a moment.")

    try:
        enhance_image(input_path, output_path)
        with open(output_path, 'rb') as result_file:
            await update.message.reply_photo(result_file, caption="✅ Here is your enhanced photo!")

        # Send original and enhanced photo to log channel
        with open(input_path, 'rb') as orig, open(output_path, 'rb') as enh:
            await context.bot.send_media_group(
                chat_id=LOG_CHANNEL_ID,
                media=[
                    InputFile(orig, filename="original.jpg"),
                    InputFile(enh, filename="enhanced.jpg"),
                ]
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

# ✅ Start Flask in a thread
def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ✅ Async main function for bot
async def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    await application.run_polling()

# ✅ Main entry
if __name__ == '__main__':
    Thread(target=run_flask).start()
    asyncio.run(run_bot())
