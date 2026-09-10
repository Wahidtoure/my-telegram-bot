import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

# ضع هنا التوكن الخاص بك الذي أخذته من BotFather بين العلامتين
BOT_TOKEN = "ضع_التوكن_هنا"

app = Client("fast_downloader_bot", bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start_command(client, message):
    message.reply_text(
        "👋 أهلاً بك في بوت التحميل السريع!\n\n"
        "🔗 أرسل لي الآن أي رابط فيديو من (يوتيوب، انستغرام، تيك توك، فيسبوك...) وسأعطيك خيارات التحميل بالجودات المختلفة أو كصوت MP3."
    )

@app.on_message(filters.text & ~filters.command(["start"]))
def send_choices(client, message):
    url = message.text.strip()
    if not url.startswith("http"):
        message.reply_text("❌ الرجاء إرسال رابط صحيح يبدأ بـ http أو https")
        return

    # إنشاء أزرار تفاعلية تظهر للمستخدم لاختيار الجودة أو الصوت
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 فيديو عالي (High)", callback_data=f"high|{url}"),
            InlineKeyboardButton("🎬 فيديو متوسط (Medium)", callback_data=f"medium|{url}")
        ],
        [
            InlineKeyboardButton("🎵 صوت فقط (MP3)", callback_data=f"audio|{url}")
        ]
    ])
    
    message.reply_text("⚡ اختر نوع التحميل المناسب لك:", reply_markup=keyboard)

@app.on_callback_query()
def handle_download(client, callback_query: CallbackQuery):
    data = callback_query.data
    action, url = data.split("|", 1)
    
    message = callback_query.message
    message.edit_text("⏳ جاري المعالجة والتحميل، يرجى الانتظار قليلاً...")

    ydl_opts = {}
    
    if action == "high":
        ydl_opts = {
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'outtmpl': 'video.%(ext)s',
        }
    elif action == "medium":
        ydl_opts = {
            'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
            'outtmpl': 'video.%(ext)s',
        }
    elif action == "audio":
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'audio.%(ext)s',
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if action == "audio":
                filename = os.path.splitext(filename)[0] + ".mp3"

        message.edit_text("📤 جاري رفع الملف إليك...")
        
        if action == "audio":
            message.reply_audio(audio=filename, caption="✨ تم استخراج الصوت بنجاح عبر بوتك الخاص!")
        else:
            message.reply_video(video=filename, caption="✨ تم تحميل الفيديو بنجاح عبر بوتك الخاص!")

        if os.path.exists(filename):
            os.remove(filename)
            
        message.delete()

    except Exception as e:
        message.edit_text(f"❌ حدث خطأ أثناء التحميل:\nتأكد أن الرابط صالح أو أن حجم الملف ليس ضخماً جداً.\nالخطأ: {str(e)}")

print("البوت يعمل بكفاءة وسرعة...")
app.run()
