import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

BOT_TOKEN = "ضع_التوكن_هنا"

app = Client("my_bot_downloader", bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("👋 أهلاً بك! أرسل لي رابط أي فيديو من انستغرام، تيك توك، أو يوتيوب وسأجهز لك خيارات التحميل فوراً.")

@app.on_message(filters.text & ~filters.command("start"))
def get_video(client, message):
    url = message.text.strip()
    if not url.startswith("http"):
        message.reply_text("❌ الرجاء إرسال رابط صحيح يبدأ بـ http أو https")
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 تحميل فيديو", callback_data=f"video|{url}"),
            InlineKeyboardButton("🎵 تحميل صوت MP3", callback_data=f"audio|{url}")
        ]
    ])
    message.reply_text("⚡ اختر ما تريد تحميله:", reply_markup=keyboard)

@app.on_callback_query()
def download_callback(client, callback_query: CallbackQuery):
    data = callback_query.data
    action, url = data.split("|", 1)
    msg = callback_query.message
    
    msg.edit_text("⏳ جاري التحميل، يرجى الانتظار...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'file.%(ext)s',
    }
    
    if action == "audio":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'file.%(ext)s',
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        msg.edit_text("📤 جاري الرفع إليك...")
        
        if action == "audio":
            msg.reply_audio(audio=filename)
        else:
            msg.reply_video(video=filename)

        if os.path.exists(filename):
            os.remove(filename)
        msg.delete()

    except Exception as e:
        msg.edit_text(f"❌ حدث خطأ أثناء التحميل: تأكد من صحة الرابط.")

app.run()
