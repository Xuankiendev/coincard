import requests
from datetime import datetime
from telebot import types
import json
import os
import telebot.util

def download(message, bot):
    args = message.text.split(' ', 2)
    if len(args) < 2:
        bot.reply_to(message, """<b><blockquote>Vui lòng cung cấp URL cần download\nVí dụ: /download [url] [chất lượng]</blockquote></b>

<b>Nền tảng hỗ trợ:</b> <i>Tiktok, Douyin, Capcut, Threads, Instagram, Facebook, Espn, Kuaishou, Pinterest, imdb, imgur, ifunny, Izlesene, Reddit, Youtube, Twitter, Vimeo, Snapchat, Bilibili, Dailymotion, Sharechat, Linkedin, Tumblr, Hipi, Telegram, Getstickerpack, Bitchute, Febspot, 9GAG, oke.ru, Rumble, Streamable, Ted, SohuTv, Xvideos, Xnxx, Xiaohongshu, Weibo, Miaopai, Meipai, Xiaoying, National Video, Yingke, Soundcloud, Mixcloud, Spotify, Zingmp3, Bandcamp.</i>

<b>Lưu ý</b>: <i>Đây là ghi chú của Api, không download được xin đừng bảo Bot lỗi. 🙏</i>""", parse_mode='HTML')
        return
    url = args[1]
    quality = args[2].lower() if len(args) >= 3 else None
    if not url.startswith(('http://', 'https://')):
        bot.reply_to(message, "🚫 URL không hợp lệ. Vui lòng cung cấp URL bắt đầu bằng http:// hoặc https://")
        return
    try:
        config_file = 'config.json'
        if not os.path.exists(config_file):
            bot.reply_to(message, "🚫 Không tìm thấy file config.json.")
            return
        with open(config_file, 'r') as f:
            config = json.load(f)
        apikey = config.get('apikey_hungdev', '')
        if not apikey:
            bot.reply_to(message, "🚫 Không tìm thấy apikey_hungdev trong config.json.")
            return
        api_url = f"https://api.hungdev.id.vn/medias/down-aio?url={url}&apikey={apikey}"
        response = requests.get(api_url)
        data = response.json()
        if not data.get('success', False):
            bot.reply_to(message, "🚫 Không thể tải nội dung từ URL được cung cấp.")
            return
        data = data['data']
        source = data.get('source', '')
        unique_id = data.get('unique_id', '')
        author = telebot.util.escape(data.get('author', '')) if data.get('author') else ''
        title = telebot.util.escape(data.get('title', 'No title'))
        duration = data.get('duration', 0)
        if duration > 300:
            duration = duration / 1000
        medias = data.get('medias', [])
        video_url = None
        audio_url = None
        images = []
        audio_duration = 0
        for media in medias:
            if media['type'] == 'video':
                video_url = media['url']
            elif media['type'] == 'audio':
                audio_url = media['url']
                audio_duration = media.get('duration', 0)
            elif media['type'] == 'image':
                images.append(media['url'])
        caption_parts = [f"🎥 Title: {title}"]
        if author and unique_id and source:
            caption_parts.append(f"👤 Tác giả: {author} (@{telebot.util.escape(unique_id)})")
        if source:
            caption_parts.append(f"🌍 Nguồn: {source.capitalize()}")
        if duration > 0:
            caption_parts.append(f"🎮 Độ Dài Video: {int(duration)} giây")
        elif audio_duration > 0:
            caption_parts.append(f"🎶 Độ Dài Nhạc: {audio_duration} giây")
        caption_parts.append(f"🗓️ Ngày Tải: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        caption = "\n".join(caption_parts)
        audio_caption = f"🎵 Nhạc nền: {title}\n👤 Tác giả: {author}\n⏱️ Độ dài nhạc: {audio_duration} giây" if audio_url else ""
        if quality == 'audio':
            if audio_url:
                audio_response = requests.get(audio_url, stream=True)
                audio_path = f"audio_{message.from_user.id}.mp3"
                with open(audio_path, 'wb') as f:
                    for chunk in audio_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                with open(audio_path, 'rb') as audio_file:
                    bot.send_audio(message.chat.id, audio_file, title=title, performer=author, caption=audio_caption)
                os.remove(audio_path)
            else:
                bot.reply_to(message, "🚫 Không có chất lượng audio trong nội dung này.")
            return
        if quality == 'video':
            if video_url:
                response = requests.head(video_url)
                size = int(response.headers.get('content-length', 0)) / 1048576
                if size > 20:
                    bot.reply_to(message, f"{caption}\n🚫 Video quá lớn để gửi trực tiếp.")
                else:
                    bot.send_video(message.chat.id, video_url, caption=caption, reply_to_message_id=message.message_id)
            else:
                bot.reply_to(message, "🚫 Không có chất lượng video trong nội dung này.")
            return
        if quality == 'image':
            if images:
                if len(images) == 1:
                    bot.send_photo(message.chat.id, images[0], caption=caption, reply_to_message_id=message.message_id)
                else:
                    media_groups = [images[i:i+10] for i in range(0, len(images), 10)]
                    for i, group in enumerate(media_groups):
                        media = [types.InputMediaPhoto(url, caption=caption if i == 0 else None) for url in group]
                        bot.send_media_group(message.chat.id, media, reply_to_message_id=message.message_id)
                    bot.send_message(message.chat.id, caption)
            else:
                bot.reply_to(message, "🚫 Không có chất lượng hình ảnh trong nội dung này.")
            return
        if video_url and duration > 0:
            response = requests.head(video_url)
            size = int(response.headers.get('content-length', 0)) / 1048576
            if size > 20:
                bot.reply_to(message, f"{caption}\n🚫 Video quá lớn để gửi trực tiếp.")
            else:
                bot.send_video(message.chat.id, video_url, caption=caption, reply_to_message_id=message.message_id)
        elif images:
            if len(images) == 1:
                bot.send_photo(message.chat.id, images[0], caption=caption, reply_to_message_id=message.message_id)
                if audio_url:
                    audio_response = requests.get(audio_url, stream=True)
                    audio_path = f"audio_{message.from_user.id}.mp3"
                    with open(audio_path, 'wb') as f:
                        for chunk in audio_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    with open(audio_path, 'rb') as audio_file:
                        bot.send_audio(message.chat.id, audio_file, title=title, performer=author, caption=audio_caption)
                    os.remove(audio_path)
            else:
                media_groups = [images[i:i+10] for i in range(0, len(images), 10)]
                for i, group in enumerate(media_groups):
                    media = [types.InputMediaPhoto(url, caption=caption if i == 0 else None) for url in group]
                    bot.send_media_group(message.chat.id, media, reply_to_message_id=message.message_id)
                bot.send_message(message.chat.id, caption)
                if audio_url:
                    audio_response = requests.get(audio_url, stream=True)
                    audio_path = f"audio_{message.from_user.id}.mp3"
                    with open(audio_path, 'wb') as f:
                        for chunk in audio_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    with open(audio_path, 'rb') as audio_file:
                        bot.send_audio(message.chat.id, audio_file, title=title, performer=author, caption=audio_caption)
                    os.remove(audio_path)
        else:
            bot.reply_to(message, "🚫 Không tìm thấy dữ liệu video hoặc ảnh từ URL được cung cấp.")
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")
