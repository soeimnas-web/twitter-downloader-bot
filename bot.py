import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# التوكن الخاص بك
TOKEN = "8744869024:AAFsqmaKcVv92dRqppVr9L9aM5L7BA0hM9Y"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك! أرسل لي أي رابط فيديو من تويتر (X)، وسأقوم بتحميله مع الوصف فوراً."
    )

async def download_twitter_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not ("twitter.com" in url or "x.com" in url):
        return

    status_message = await update.message.reply_text("⏳ جاري معالجة الرابط والتحميل...")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    loop = asyncio.get_running_loop()

    try:
        def process_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                description = info.get('description', 'لا يوجد وصف.')
                return file_path, description

        file_path, description = await loop.run_in_executor(None, process_download)

        if os.path.exists(file_path):
            await status_message.edit_text("⬆️ جاري رفع الفيديو إلى تلجرام...")
            
            with open(file_path, 'rb') as video_file:
                caption_text = description[:1000] if description else ""
                await update.message.reply_video(
                    video=video_file,
                    caption=f"📝 **الوصف:**\n{caption_text}",
                    parse_mode="Markdown"
                )
            
            os.remove(file_path)
            await status_message.delete()
        else:
            await status_message.edit_text("❌ حدث خطأ أثناء العثور على الملف المحمل.")

    except Exception as e:
        await status_message.edit_text("❌ تعذر تحميل الفيديو. تأكد من صحة الرابط أو جرب لاحقاً.")

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_twitter_video))

    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
