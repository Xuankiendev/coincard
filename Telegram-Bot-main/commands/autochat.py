import requests
import telebot

autochat_data = {}

SIMSIMI_API_KEY = "GZyOSYF-1Pr5bDnMZ-ng2bNQVbkvtH1OeJyNBjoi"
SIMSIMI_API_URL = "https://wsapi.simsimi.com/190410/talk"

def autochat(message, bot):
    if message.chat.type not in ['group', 'supergroup'] or not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "<blockquote>Lệnh này chỉ hoạt động trong nhóm và cần reply tin nhắn người dùng.</blockquote>", parse_mode='HTML')
        return
    chat_id = str(message.chat.id)
    user_id = str(message.reply_to_message.from_user.id)
    full_name = message.reply_to_message.from_user.full_name
    autochat_data.setdefault(chat_id, {})
    if user_id in autochat_data[chat_id]:
        del autochat_data[chat_id][user_id]
        if not autochat_data[chat_id]:
            del autochat_data[chat_id]
        bot.reply_to(message, f"<blockquote>Đã dừng autochat cho {full_name}.</blockquote>", parse_mode='HTML')
    else:
        autochat_data[chat_id][user_id] = True
        bot.reply_to(message, f"<blockquote>Đã kích hoạt autochat cho {full_name}.</blockquote>", parse_mode='HTML')

def init(bot):
    @bot.message_handler(content_types=['text'], func=lambda msg: str(msg.chat.id) in autochat_data and str(msg.from_user.id) in autochat_data.get(str(msg.chat.id), {}) and msg.text and not msg.text.startswith('/'))
    def handle_autochat_message(msg):
        try:
            reply = f"{requests.post(SIMSIMI_API_URL, headers={'Content-Type': 'application/json', 'x-api-key': SIMSIMI_API_KEY}, json={'utext': msg.text, 'lang': 'vn', 'atext_bad_prob_max': 0.7}).json()['atext']}"
            bot.reply_to(msg, reply)
        except:
            bot.reply_to(msg, "Xin lỗi, tôi không thể trả lời lúc này.")