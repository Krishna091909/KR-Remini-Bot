import os
from flask import Flask
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update, InputFile
from dotenv import load_dotenv
from basicsr_test import enhance_image  # make sure this file exists
from uuid import uuid4

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Remini Bot is Running!"

# ✅ /start command handler
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

        # Log both original and enhanced images to the log channel
        with open(input_path, 'rb') as orig, open(output_path, 'rb') as enh:
            await context.bot.send_media_group(
                chat_id=LOG_CHANNEL_ID,
                media=[
                    InputFile(orig, filename="original.jpg"),
                    InputFile(enh, filename="enhanced.jpg"),
                ]
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Oops! Something went wrong: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))  # ✅ Start command
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))  # ✅ Photo handler
    application.run_polling()

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    run_flask()
