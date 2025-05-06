import requests
from datetime import datetime
from telebot import types
import json
import os

def tiktokdownload(message, bot):
    args = message.text.split(' ', 1)
    if len(args) < 2:
        bot.reply_to(message, "<blockquote>Vui lòng cung cấp URL TikTok. Ví dụ: /tiktokdownload https://vt.tiktok.com/xxx</blockquote>", parse_mode='HTML')
        return
    url = args[1]
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url)
        data = response.json()
        if data['code'] != 0:
            bot.reply_to(message, "🚫 Không thể tải video từ URL được cung cấp.")
            return
        data = data['data']
        title = data['title']
        username = data['author']['unique_id']
        nickname = data['author']['nickname']
        region = data['region']
        duration = data['duration']
        duration_music = data['music_info']['duration']
        size = data['size'] / 1048576 if data['size'] > 0 else None
        created_time = datetime.fromtimestamp(data['create_time']).strftime('%Y-%m-%d %H:%M:%S')
        play_count = data['play_count']
        digg_count = data['digg_count']
        comment_count = data['comment_count']
        share_count = data['share_count']
        download_count = data['download_count']
        collect_count = data['collect_count']
        video_url = data.get('play', '')
        music_url = data['music_info']['play']
        music_title = data['music_info']['title']
        music_author = data['music_info']['author']
        music_duration = data['music_info']['duration']
        images = data.get('images', [])
        caption = f"🎥 <strong>{title}</strong>\n\n" \
                  f"<blockquote>👤 Tác giả: <a href='https://www.tiktok.com/@{username}'>{nickname}</a>\n" \
                  f"🌍 Khu Vực: {region}\n" \
                  f"{('🎮 Độ Dài Video: ' + str(duration) + ' giây' if duration > 0 else '🎶 Độ Dài Nhạc: ' + str(duration_music) + ' giây')}\n" \
                  f"{('🗂️ Dung Lượng: ' + str(round(size, 2)) + ' MB' if size else '')}\n" \
                  f"🗓️ Ngày Đăng: {created_time}\n" \
                  "---------------------------------------\n" \
                  f"▶️ Views: {play_count}\n" \
                  f"❤️ Likes: {digg_count} tim\n" \
                  f"💬 Comments: {comment_count}\n" \
                  f"🔄 Shares: {share_count}\n" \
                  f"⬇️ Downloads: {download_count}\n" \
                  f"📥 Favorites: {collect_count}</blockquote>"
        audio_caption = f"<blockquote>🎵 Nhạc nền: {music_title}\n👤 Tác giả: {music_author}\n⏱️ Độ dài nhạc: {music_duration} giây</blockquote>"
        if video_url and duration > 0:
            if size and size > 20:
                bot.reply_to(message, f"{caption}\n🚫 Video quá lớn để gửi trực tiếp.", parse_mode='HTML')
            else:
                bot.send_video(message.chat.id, video_url, caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')
            bot.send_audio(message.chat.id, music_url, title=f"{data['title']}", performer=f"{data['music_info']['author']}", caption=audio_caption, parse_mode='HTML')
        elif images:
            if len(images) == 1:
                bot.send_photo(message.chat.id, images[0], caption=caption, reply_to_message_id=message.message_id, parse_mode='HTML')
            else:
                media_groups = [images[i:i+10] for i in range(0, len(images), 10)]
                for i, group in enumerate(media_groups):
                    media = [types.InputMediaPhoto(url, caption=caption if i == 0 else None, parse_mode='HTML') for url in group]
                    bot.send_media_group(message.chat.id, media, reply_to_message_id=message.message_id)
            bot.send_audio(message.chat.id, music_url, title=f"{data['title']}", performer=f"{data['music_info']['author']}", caption=audio_caption, parse_mode='HTML')
        else:
            bot.reply_to(message, "🚫 Không tìm thấy dữ liệu video hoặc ảnh từ URL được cung cấp.")
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")