import time
import random
import telebot

start_time = time.time()

def uptime(message, bot):
    try:
        current_time = time.time()
        uptime_seconds = int(current_time - start_time)
        days = uptime_seconds // (24 * 3600)
        uptime_seconds %= (24 * 3600)
        hours = uptime_seconds // 3600
        uptime_seconds %= 3600
        minutes = uptime_seconds // 60
        seconds = uptime_seconds % 60
        caption = f"🧭 Bot đã làm việc cho nhóm {message.chat.title} trong {days} ngày, {hours} giờ, {minutes} phút, {seconds} giây."
        with open("assets/vdgirl.txt", "r", encoding="utf-8") as f:
            video_links = [line.strip() for line in f if line.strip()]
        if not video_links:
            bot.reply_to(message, "🚫 Không tìm thấy video nào trong file.")
            return
        video_url = random.choice(video_links)
        bot.send_video(message.chat.id, video_url, caption=caption, reply_to_message_id=message.message_id)
    except Exception as e:
        print(f"Lỗi: {e}")
        bot.reply_to(message, "🚫 Đã xảy ra lỗi khi xử lý lệnh.")