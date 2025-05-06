import json
import requests
import hashlib
import hmac
import time
import telebot
import re

zingmp3_data = {}
URL = "https://zingmp3.vn"
API_KEY = "X5BM3w8N7MKozC0B85o4KMlzLZKhV00y"
SECRET_KEY = "acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW"
VERSION = "1.11.11"

def get_hash256(string):
    return hashlib.sha256(string.encode()).hexdigest()

def get_hmac512(string, key):
    return hmac.new(key.encode(), string.encode(), hashlib.sha512).hexdigest()

def get_sig(path, params):
    param_string = ''.join(f"{key}={params[key]}" for key in sorted(params.keys()) if key in ["ctime", "id", "type", "page", "count", "version"])
    return get_hmac512(path + get_hash256(param_string), SECRET_KEY)

def get_cookie():
    response = requests.get(URL)
    return response.cookies.get_dict()

def request_zing_mp3(path, params):
    cookies = get_cookie()
    response = requests.get(f"{URL}{path}", params=params, cookies=cookies)
    return response.json()

def search_music(keyword):
    ctime = str(int(time.time()))
    path = "/api/v2/search"
    params = {
        "q": keyword,
        "type": "song",
        "count": 10,
        "ctime": ctime,
        "version": VERSION,
        "apiKey": API_KEY,
        "sig": get_sig(path, {
            "q": keyword,
            "type": "song",
            "count": 10,
            "ctime": ctime,
            "version": VERSION
        })
    }
    return request_zing_mp3(path, params)

def get_streaming_song(song_id):
    ctime = str(int(time.time()))
    path = "/api/v2/song/get/streaming"
    params = {
        "id": song_id,
        "ctime": ctime,
        "version": VERSION,
        "apiKey": API_KEY,
        "sig": get_sig(path, {
            "id": song_id,
            "ctime": ctime,
            "version": VERSION
        })
    }
    return request_zing_mp3(path, params)

def get_lyrics(song_id):
    try:
        response = requests.get(f"https://m.zingmp3.vn/xhr/lyrics/get-lyrics", params={"media_id": song_id})
        return response.json()
    except:
        return {"err": -1, "msg": "Failed to fetch lyrics"}

def zingmp3(message, bot):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "🚫 Vui lòng nhập tên bài hát muốn tìm kiếm.\nVí dụ: /zingmp3 Tên bài hát", parse_mode='HTML')
        return
    keyword = args[1].strip()
    search_result = search_music(keyword)
    if not search_result.get('data') or not search_result['data'].get('items'):
        bot.reply_to(message, "🚫 Không tìm thấy bài hát nào khớp với từ khóa.", parse_mode='HTML')
        return
    songs = search_result['data']['items']
    response_text = "<b>🎵 Kết quả tìm kiếm trên Zing MP3</b>\n\n"
    for i, song in enumerate(songs):
        response_text += f"<b>{i + 1}. {song['title']}</b>\n"
        response_text += f"👤 Nghệ sĩ: {song['artistsNames']}\n"
        response_text += f"🆔 ID: {song['encodeId']}\n\n"
    response_text += "<b>💡 Trả lời tin nhắn này bằng số từ 1-10 hoặc 1-10 lyric để chọn bài hát!</b>"
    sent = bot.reply_to(message, response_text, parse_mode='HTML')
    zingmp3_data[sent.message_id] = {
        "user_id": message.from_user.id,
        "songs": songs
    }

def init(bot):
    @bot.message_handler(func=lambda msg: msg.reply_to_message and msg.reply_to_message.message_id in zingmp3_data)
    def handle_zingmp3_selection(msg):
        reply_id = msg.reply_to_message.message_id
        if reply_id not in zingmp3_data:
            return
        user_id = msg.from_user.id
        data = zingmp3_data[reply_id]
        if user_id != data['user_id']:
            return
        text = msg.text.strip().lower()
        want_lyrics = text.endswith("lyric")
        try:
            index = int(text.split()[0]) - 1
            if index < 0 or index >= len(data["songs"]):
                bot.reply_to(msg, "🚫 Số không hợp lệ. Hãy nhập số từ 1-10.", parse_mode='HTML')
                return
        except (ValueError, IndexError):
            bot.reply_to(msg, "🚫 Vui lòng nhập số từ 1-10 (hoặc số + 'lyric').", parse_mode='HTML')
            return
        song = data["songs"][index]
        bot.delete_message(msg.chat.id, reply_id)
        bot.reply_to(msg, f"🧭 Đang tải: {song['title']}", parse_mode='HTML')
        streaming_data = get_streaming_song(song["encodeId"])
        if streaming_data.get('err') != 0 or not streaming_data.get('data'):
            bot.reply_to(msg, "🚫 Không thể tải bài hát này.", parse_mode='HTML')
            return
        audio_url = streaming_data['data'].get('320')
        quality = "320kbps"
        if audio_url == "VIP":
            audio_url = streaming_data['data'].get('128')
            quality = "128kbps"
        thumbnail_url = song.get('thumbnail')
        if not audio_url or not thumbnail_url:
            bot.reply_to(msg, "🚫 Không tìm thấy nguồn audio hoặc thumbnail.", parse_mode='HTML')
            return
        caption = f"<b>🎵 {song['title']}</b>\n"
        caption += f"👤 Nghệ sĩ: {song['artistsNames']}\n"
        caption += f"🎧 Nguồn: Zing MP3\n"
        caption += f"🔊 Chất lượng: {quality}\n"
        caption += f"🎉 Chúc bạn thưởng thức âm nhạc vui vẻ!"
        bot.send_photo(msg.chat.id, thumbnail_url, caption=caption, parse_mode='HTML')
        bot.send_audio(msg.chat.id, audio_url, title=song['title'], performer=song['artistsNames'])
        if want_lyrics:
            lyrics_data = get_lyrics(song["encodeId"])
            if lyrics_data.get('err') == 0 and lyrics_data.get('data') and len(lyrics_data['data']) > 0 and lyrics_data['data'][0].get('content'):
                lyrics = re.sub(r'<br\s*/?>', '\n', lyrics_data['data'][0]['content']).strip()
                bot.send_message(msg.chat.id, f"<b>📜 Lời bài hát: {song['title']}</b>\n\n{lyrics}", parse_mode='HTML')
            else:
                bot.send_message(msg.chat.id, "🚫 Không tìm thấy lời bài hát.", parse_mode='HTML')
        del zingmp3_data[reply_id]