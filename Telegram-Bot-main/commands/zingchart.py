import requests
import telebot

zingchart_data = []

def fetch_zing_chart(chat_id):
    global zingchart_data
    try:
        response = requests.get('https://mp3.zing.vn/xhr/chart-realtime')
        data  data = response.json()
        if data.get('err') == 0:
            chat_vxk = next((item for item in zingchart_data if item['chat_id'] == chat_id), None)
            if not chat_vxk:
                chat_vxk = {'chat_id': chat_id, 'chart_data': [], 'users': {}}
                zingchart_data.append(chat_vxk)
            chat_vxk['chart_data'] = data['data']['song']
            return True
        return False
    except Exception as e:
        print(f"Lỗi lấy dữ liệu Zing MP3: {e}")
        return False

def get_audio_source(code):
    try:
        url = f'https://m.zingmp3.vn/xhr/media/get-source?type=audio&key={code}'
        response = requests.get(url).json()
        if response.get('err') == 0:
            return response['data']['source']['128']
        return None
    except Exception as e:
        print(f"Lỗi lấy nguồn audio: {e}")
        return None

def zingchart(message, bot):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not fetch_zing_chart(chat_id):
        bot.reply_to(message, "🚫 Lỗi lấy dữ liệu Zing MP3")
        return
    chat_vxk = next((item for item in zingchart_data if item['chat_id'] == chat_id), None)
    songs = chat_vxk['chart_data'][:10]
    song_list = [f"{i+1}. {song['name']} - {song['artists_names']}" for i, song in enumerate(songs)]
    message_text = "<b>🎵 Kết quả tìm kiếm Top BXH ZingMP3:</b>\n\n" + "\n".join(song_list) + "\n\n<b>💡 Trả lời tin nhắn này bằng số từ 1-10 để chọn bài hát!</b>"
    msg = bot.send_message(chat_id, message_text, reply_to_message_id=message.message_id, parse_mode='HTML')
    if user_id not in chat_vxk['users']:
        chat_vxk['users'][user_id] = {'active': False, 'message_id': None}
    chat_vxk['users'][user_id]['active'] = True
    chat_vxk['users'][user_id]['message_id'] = msg.message_id

def init(bot):
    @bot.message_handler(func=lambda message: message.chat.id in [entry['chat_id'] for entry in zingchart_data] and message.from_user.id in next((entry['users'] for entry in zingchart_data if entry['chat_id'] == message.chat.id), {}))
    def handle_song_selection(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        chat_vxk = next((item for item in zingchart_data if item['chat_id'] == chat_id), None)
        if not chat_vxk or not chat_vxk['users'][user_id]['active']:
            return
        try:
            song_index = int(message.text) - 1
            if 0 <= song_index <= 9:
                song = chat_vxk['chart_data'][song_index]
                code = song['code']
                thumbnail_url = song['thumbnail']
                audio_url = get_audio_source(code)
                bot.delete_message(chat_id, chat_vxk['users'][user_id]['message_id'])
                bot.send_message(chat_id, f"🧭 Đang tải: {song['name']} - {song['artists_names']}")
                if audio_url:
                    bot.send_photo(chat_id, thumbnail_url, caption=f"-> Zing MP3 <-\nChúc bạn nghe nhạc vui vẻ.\n\n🎵 Music: {song['name']}\n👤 Artists: {song['artists_names']}\n📊 #Top{song_index + 1}_ZingMP3 \n\nCùng nhau thưởng thức bài hát hot top {song_index + 1} trên nền tảng nhạc Việt ZingMP3 nào!!!")
                    bot.send_audio(chat_id, audio_url)
                    chat_vxk['users'][user_id]['active'] = False
                else:
                    bot.reply_to(message, "🚫 Không tìm thấy nguồn audio")
            else:
                bot.reply_to(message, "🚫️ Gõ số từ 1-10")
        except ValueError:
            bot.reply_to(message, "🚫️ Gõ số hợp lệ từ 1-10")
