from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import re
import time
from datetime import datetime
import threading

def load_group_settings():
    try:
        with open('assets/data/group_settings.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_group_settings(settings):
    os.makedirs('assets/data', exist_ok=True)
    with open('assets/data/group_settings.json', 'w') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

def schedule_autopr(bot, chat_id, time_str, content, media_path=None):
    def send_message():
        while True:
            now = datetime.now().strftime('%H:%M')
            if now == time_str:
                try:
                    send_content = content.replace('\\n', '\n')
                    if media_path:
                        ext = os.path.splitext(media_path)[1].lower()
                        if ext in ['.jpg', '.jpeg', '.png']:
                            with open(media_path, 'rb') as photo:
                                bot.send_photo(chat_id, photo, caption=send_content)
                        elif ext in ['.mp4', '.mov']:
                            with open(media_path, 'rb') as video:
                                bot.send_video(chat_id, video, caption=send_content)
                        elif ext in ['.mp3', '.ogg']:
                            with open(media_path, 'rb') as audio:
                                bot.send_audio(chat_id, audio, caption=send_content)
                    else:
                        bot.send_message(chat_id, send_content)
                except Exception as e:
                    bot.send_message(chat_id, "🚫 Lỗi khi gửi autoPR: " + str(e))
                time.sleep(60 - datetime.now().second)
            time.sleep(1)
    threading.Thread(target=send_message, daemon=True).start()

def schedule_interval_autopr(bot, chat_id, interval_seconds, content, media_path=None):
    def send_message():
        while True:
            try:
                send_content = content.replace('\\n', '\n')
                if media_path:
                    ext = os.path.splitext(media_path)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png']:
                        with open(media_path, 'rb') as photo:
                            bot.send_photo(chat_id, photo, caption=send_content)
                    elif ext in ['.mp4', '.mov']:
                        with open(media_path, 'rb') as video:
                            bot.send_video(chat_id, video, caption=send_content)
                    elif ext in ['.mp3', '.ogg']:
                        with open(media_path, 'rb') as audio:
                            bot.send_audio(chat_id, audio, caption=send_content)
                else:
                    bot.send_message(chat_id, send_content)
            except Exception as e:
                bot.send_message(chat_id, "🚫 Lỗi khi gửi autoPR: " + str(e))
            time.sleep(interval_seconds)
    threading.Thread(target=send_message, daemon=True).start()

def autopr(message, bot):
    chat_id = message.chat.id
    text = message.text
    reply_to = message.reply_to_message
    settings = load_group_settings()
    group_id = str(chat_id)
    if group_id not in settings:
        settings[group_id] = {
            "nameGroup": message.chat.title or "Unknown",
            "autoPR": []
        }
    if text.startswith('/autopr remove'):
        try:
            parts = text.split()
            if len(parts) < 3:
                bot.reply_to(message, "📌 Sử dụng: /autopr remove [index]\nVí dụ: /autopr remove 1")
                return
            index = int(parts[2]) - 1
            if 0 <= index < len(settings[group_id]["autoPR"]):
                settings[group_id]["autoPR"].pop(index)
                save_group_settings(settings)
                bot.reply_to(message, "✅ Đã xóa autoPR tại index " + str(index + 1))
            else:
                bot.reply_to(message, "🚫 Index không hợp lệ")
            return
        except:
            bot.reply_to(message, "📌 Sử dụng: /autopr remove [index]\nVí dụ: /autopr remove 1")
            return
    if text == '/autopr':
        if not settings[group_id]["autoPR"]:
            bot.reply_to(message, "📌 Sử dụng:\n1. /autopr [thời gian] | [nội dung]\nVí dụ: /autopr 00:00 | [nội dung]\n2. /autopr for [khoảng thời gian] | [nội dung]\nVí dụ: /autopr for 5p | [nội dung]")
        else:
            response = "👀 Danh sách cấu hình autoPR, gõ /autopr remove [index] để dừng cấu hình đó.\n\n"
            for i, pr in enumerate(settings[group_id]["autoPR"], 1):
                media = ""
                if pr.startswith("interval:"):
                    parts = pr.split(": ", 2)
                    interval = parts[1]
                    content = parts[2]
                    if "(đi kèm cache)" in content:
                        content, media = content.split(" (đi kèm cache): ")
                        media = "📎 Đi kèm: " + media
                    response += str(i) + ".\n🧭 Khoảng thời gian: " + interval + "\n📝 Nội dung: " + content + "\n" + media + "\n\n"
                else:
                    parts = pr.split(": ", 1)
                    time_str = parts[0]
                    content = parts[1]
                    if "(đi kèm cache)" in content:
                        content, media = content.split(" (đi kèm cache): ")
                        media = "📎 Đi kèm: " + media
                    response += str(i) + ".\n🧭 Thời gian: " + time_str + "\n📝 Nội dung: " + content + "\n" + media + "\n\n"
            bot.reply_to(message, response)
        return
    time_pattern = r'^/autopr\s+(\d{2}:\d{2})\s*\|\s*((?:.|\n)+)$'
    time_match = re.match(time_pattern, text, re.MULTILINE)
    interval_pattern = r'^/autopr\s+for\s+(\d+[sphd])\s*\|\s*((?:.|\n)+)$'
    interval_match = re.match(interval_pattern, text, re.MULTILINE)
    if not time_match and not interval_match:
        bot.reply_to(message, "📌 Sử dụng:\n1. /autopr [thời gian] | [nội dung]\nVí dụ: /autopr [thời gian] | [nội dung]\n2. /autopr for [khoảng thời gian] | [nội dung]\nVí dụ: /autopr for [thời gian] | [nội dung]")
        return
    media_path = None
    if reply_to and (reply_to.photo or reply_to.video or reply_to.audio):
        os.makedirs('assets/cache', exist_ok=True)
        file_id = None
        ext = '.jpg'
        if reply_to.photo:
            file_id = reply_to.photo[-1].file_id
            ext = '.jpg'
        elif reply_to.video:
            file_id = reply_to.video.file_id
            ext = '.mp4'
        elif reply_to.audio:
            file_id = reply_to.audio.file_id
            ext = '.mp3'
        file_info = bot.get_file(file_id)
        file_path = "assets/cache/" + str(chat_id) + "_" + datetime.now().strftime('%H%M%S') + ext
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        media_path = file_path
    if time_match:
        time_str, content = time_match.groups()
        content = content.strip().replace('\n', '\\n')
        try:
            datetime.strptime(time_str, '%H:%M')
        except ValueError:
            bot.reply_to(message, "🚫 Thời gian không hợp lệ, dùng định dạng HH:MM (ví dụ: 00:00)")
            return
        pr_entry = time_str + ": " + content
        if media_path:
            pr_entry += " (đi kèm cache): " + media_path
        settings[group_id]["autoPR"].append(pr_entry)
        save_group_settings(settings)
        schedule_autopr(bot, chat_id, time_str, content, media_path)
        caption_label = "Caption" if media_path else "Nội dung"
        group_name = message.chat.title if message.chat.title else "Unknown"
        bot.reply_to(message, "Cấu hình thành công cho nhóm " + group_name + ". ✅\n🧭 Thời gian: " + time_str + "\n📝 " + caption_label + ": " + content.replace('\\n', '\n') + "\n📎 Cache: " + (media_path if media_path else 'Không'))
    elif interval_match:
        interval_str, content = interval_match.groups()
        content = content.strip().replace('\n', '\\n')
        interval_match = re.match(r'^(\d+)([sphd])$', interval_str)
        if not interval_match:
            bot.reply_to(message, "🚫 Khoảng thời gian không hợp lệ, dùng định dạng như 5s, 5p, 2h, 1d")
            return
        value, unit = interval_match.groups()
        value = int(value)
        if unit == 's':
            interval_seconds = value
            interval_display = str(value) + " giây"
        elif unit == 'p':
            interval_seconds = value * 60
            interval_display = str(value) + " phút"
        elif unit == 'h':
            interval_seconds = value * 3600
            interval_display = str(value) + " giờ"
        else:
            interval_seconds = value * 86400
            interval_display = str(value) + " ngày"
        pr_entry = "interval: " + interval_display + ": " + content
        if media_path:
            pr_entry += " (đi kèm cache): " + media_path
        settings[group_id]["autoPR"].append(pr_entry)
        save_group_settings(settings)
        schedule_interval_autopr(bot, chat_id, interval_seconds, content, media_path)
        caption_label = "Caption" if media_path else "Nội dung"
        group_name = message.chat.title if message.chat.title else "Unknown"
        bot.reply_to(message, "Cấu hình thành công cho nhóm " + group_name + ". ✅\n🧭 Khoảng thời gian: " + interval_display + "\n📝 " + caption_label + ": " + content.replace('\\n', '\n') + "\n📎 Cache: " + (media_path if media_path else 'Không'))