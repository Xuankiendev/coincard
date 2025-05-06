import requests
import telebot
from urllib.parse import quote_plus

tiktok_data = []

def search_tiktok(chat_id, keyword, count=10):
    global tiktok_data
    try:
        url = f"https://www.tikwm.com/api/feed/search?keywords={quote_plus(keyword)}&count={count}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("code") == 0 and "data" in data and "videos" in data["data"]:
            chat_vxk = next((item for item in tiktok_data if item['chat_id'] == chat_id), None)
            if not chat_vxk:
                chat_vxk = {'chat_id': chat_id, 'videos': [], 'users': {}}
                tiktok_data.append(chat_vxk)
            videos = []
            for video in data["data"]["videos"]:
                videos.append({
                    "title": video["title"],
                    "author": video["author"]["nickname"],
                    "thumbnail": video["cover"],
                    "views": video["play_count"],
                    "likes": video["digg_count"],
                    "shares": video["share_count"],
                    "video_url": video["play"],
                    "duration": video["duration"]
                })
            chat_vxk['videos'] = videos
            return True
        return False
    except Exception as e:
        print(f"Lỗi lấy dữ liệu TikTok: {e}")
        return False

def tiktok(message, bot):
    chat_id = message.chat.id
    user_id = message.from_user.id
    content = message.text.replace('/tiktok', "").strip()
    parts = content.split("&&")
    keyword = parts[0].strip() if parts else ""
    limit = int(parts[1]) if len(parts) > 1 and parts[1].strip().isdigit() else 10
    if not keyword:
        bot.reply_to(message, "Vui lòng nhập từ khóa tìm kiếm\nVí dụ: /tiktok Nội dung cần tìm")
        return
    if not search_tiktok(chat_id, keyword, limit):
        bot.reply_to(message, f"Không tìm thấy video phù hợp với từ khóa: {keyword}")
        return
    chat_vxk = next((item for item in tiktok_data if item['chat_id'] == chat_id), None)
    videos = chat_vxk['videos'][:10]
    video_list = [f"{i+1}. {video['title']} - {video['author']}\n👀: {video['views']} | ❤️: {video['likes']} | 🔄: {video['shares']}" for i, video in enumerate(videos)]
    message_text = "<b>🔎 Kết quả tìm kiếm video TikTok:</b>\n\n" + "\n".join(video_list) + f"\n\n<b>💡 Trả lời tin nhắn này bằng số từ 1-{len(videos)} để chọn video!</b>"
    msg = bot.send_message(chat_id, message_text, reply_to_message_id=message.message_id, parse_mode='HTML')
    if user_id not in chat_vxk['users']:
        chat_vxk['users'][user_id] = {'active': False, 'message_id': None}
    chat_vxk['users'][user_id]['active'] = True
    chat_vxk['users'][user_id]['message_id'] = msg.message_id

def init(bot):
    @bot.message_handler(func=lambda message: message.chat.id in [entry['chat_id'] for entry in tiktok_data] and message.from_user.id in next((entry['users'] for entry in tiktok_data if entry['chat_id'] == message.chat.id), {}))
    def handle_tiktok_selection(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        chat_vxk = next((item for item in tiktok_data if item['chat_id'] == chat_id), None)
        if not chat_vxk or not chat_vxk['users'][user_id]['active']:
            return
        try:
            video_index = int(message.text) - 1
            if 0 <= video_index < len(chat_vxk['videos']):
                video = chat_vxk['videos'][video_index]
                video_url = video['video_url']
                thumbnail_url = video['thumbnail']
                response = requests.head(video_url)
                if 'Content-Length' in response.headers and int(response.headers['Content-Length']) > 50 * 1024 * 1024:
                    bot.reply_to(message, "Video quá lớn để gửi (>50MB)")
                    return
                bot.delete_message(chat_id, chat_vxk['users'][user_id]['message_id'])
                bot.send_photo(chat_id, thumbnail_url, caption=f"🧭 Đang tải video TikTok: {video['title']} - {video['author']}")
                caption = f"[ {message.from_user.full_name} ]\n🎬 Tiêu đề: {video['title']}\n👤 Tác giả: {video['author']}\n⏱️ Thời lượng: {video['duration']}s\n👁️ Lượt xem: {video['views']}\n❤️ Lượt thích: {video['likes']}\n📤 Lượt chia sẻ: {video['shares']}"
                bot.send_video(chat_id, video_url, caption=caption)
                chat_vxk['users'][user_id]['active'] = False
            else:
                bot.reply_to(message, f"🚫 Gõ số từ 1-{len(chat_vxk['videos'])}")
        except ValueError:
            bot.reply_to(message, f"🚫 Gõ số hợp lệ từ 1-{len(chat_vxk['videos'])}")
        except telebot.apihelper.ApiTelegramException as e:
            bot.reply_to(message, f"Không thể gửi video: {e}")
