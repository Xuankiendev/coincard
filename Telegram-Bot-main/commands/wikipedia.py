import wikipediaapi
import telebot

wiki_data = {}
wiki = wikipediaapi.Wikipedia(user_agent='MyTelegramBot/1.0 (https://example.com/contact)', language='vi')

def search_wikipedia(keyword):
    return list(wiki.page(keyword).links.keys())[:10]

def get_summary(title):
    try:
        page = wiki.page(title)
        if page.exists():
            return page.summary[:1000]
        return None
    except:
        return None

def wikipedia(message, bot):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "🚫 Vui lòng nhập từ khóa cần tìm kiếm.\nVí dụ: /wikipedia Từ khóa", parse_mode='HTML')
        return
    keyword = args[1].strip()
    search_results = search_wikipedia(keyword)
    if not search_results:
        bot.reply_to(message, "🚫 Không tìm thấy bài viết nào khớp với từ khóa.", parse_mode='HTML')
        return
    response_text = "<b>📚 Kết quả tìm kiếm trên Wikipedia</b>\n\n"
    for i, title in enumerate(search_results[:10]):
        response_text += f"<b>{i + 1}. {title}</b>\n"
    response_text += "\n<b>💡 Trả lời tin nhắn này bằng số từ 1-10 để chọn bài viết!</b>"
    sent = bot.reply_to(message, response_text, parse_mode='HTML')
    wiki_data[sent.message_id] = {
        "user_id": message.from_user.id,
        "results": search_results
    }

def init(bot):
    @bot.message_handler(func=lambda msg: msg.reply_to_message and msg.reply_to_message.message_id in wiki_data)
    def handle_wikipedia_selection(msg):
        reply_id = msg.reply_to_message.message_id
        if reply_id not in wiki_data:
            return
        user_id = msg.from_user.id
        data = wiki_data[reply_id]
        if user_id != data['user_id']:
            return
        text = msg.text.strip()
        try:
            index = int(text) - 1
            if index < 0 or index >= len(data["results"]):
                bot.reply_to(msg, "🚫 Số không hợp lệ. Hãy nhập số từ 1-10.", parse_mode='HTML')
                return
        except:
            bot.reply_to(msg, "🚫 Vui lòng nhập số từ 1-10.", parse_mode='HTML')
            return
        title = data["results"][index]
        bot.delete_message(msg.chat.id, reply_id)
        bot.reply_to(msg, f"🧭 Đang tải: {title}", parse_mode='HTML')
        summary = get_summary(title)
        if not summary:
            bot.reply_to(msg, "🚫 Không thể lấy nội dung bài viết.", parse_mode='HTML')
            return
        bot.send_message(msg.chat.id, f"<b>📚 {title}</b>\n\n{summary}", parse_mode='HTML')
        del wiki_data[reply_id]