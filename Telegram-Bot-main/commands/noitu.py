from urllib.parse import quote_plus
import requests

noitu_games = {}

def get_noitu_response(word):
    api_url = f"https://noitu.pro/answer?word={quote_plus(word)}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if data["success"] and "nextWord" in data and "chuan" in data["nextWord"]:
            return data["nextWord"]["chuan"]
        return None
    except:
        return None

def check_word(word):
    api_url = f"https://noitu.pro/answer?word={quote_plus(word)}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if data["error"] == False and data["success"] == False:
            return "sai"
        if data["error"] == False and data["success"] == True:
            return "đúng"
        return "lỗi"
    except:
        return "lỗi"

def noitu(message, bot):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng sử dụng: /noitu join hoặc /noitu leave ℹ️")
        return
    action = args[1].lower()
    chat_id = message.chat.id
    user_id = message.from_user.id
    if action == "join":
        if chat_id not in noitu_games:
            noitu_games[chat_id] = {'players': [], 'last_word': None, 'turn_index': 0, 'fails': {}, 'bot_started': False}
        if user_id not in noitu_games[chat_id]['players']:
            noitu_games[chat_id]['players'].append(user_id)
            noitu_games[chat_id]['fails'][user_id] = 0
            username = message.from_user.username or message.from_user.first_name
            bot.reply_to(message, f"👤 @{username} đã tham gia phòng chơi nối từ!")
            if len(noitu_games[chat_id]['players']) == 1:
                bot.reply_to(message, "🚨 Bạn là người đầu tiên tham gia phòng, gõ từ đầu tiên để bắt đầu trò chơi nhé!")
        else:
            bot.reply_to(message, "✅ Bạn đã ở trong phòng này rồi!")
    elif action == "leave":
        if chat_id in noitu_games and user_id in noitu_games[chat_id]['players']:
            noitu_games[chat_id]['players'].remove(user_id)
            del noitu_games[chat_id]['fails'][user_id]
            if noitu_games[chat_id]['turn_index'] >= len(noitu_games[chat_id]['players']):
                noitu_games[chat_id]['turn_index'] = 0
            bot.reply_to(message, f"@{message.from_user.username} đã rời trò chơi! 🚨")
            if not noitu_games[chat_id]['players']:
                del noitu_games[chat_id]
        else:
            bot.reply_to(message, "🚫 Bạn chưa tham gia trò chơi!")

def init(bot):
    @bot.message_handler(func=lambda message: message.chat.id in noitu_games and message.from_user.id in noitu_games[message.chat.id]['players'])
    def noitu_game(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        if message.text.startswith('/'):
            return
        game = noitu_games[chat_id]
        if not game['last_word']:
            word = message.text.strip()
            if len(word.split()) != 2:
                bot.reply_to(message, "🚫 Bạn phải nhập đúng 2 từ để bắt đầu trò chơi!")
                return
            user_tail = word.split()[1]
            result = check_word(word)
            if result != "đúng":
                game['fails'][user_id] += 1
                if game['fails'][user_id] >= 3:
                    username = message.from_user.username or message.from_user.first_name
                    bot.reply_to(message, f"🚫 @{username} đã nhập sai 3 lần và bị loại khỏi phòng!")
                    game['players'].remove(user_id)
                    del game['fails'][user_id]
                    if not game['players']:
                        del noitu_games[chat_id]
                    return
                bot.reply_to(message, f"Từ này không có trong từ điển! 🚫\nBạn còn {3 - game['fails'][user_id]} lượt thử lại trước khi bị loại!")
                return
            response = get_noitu_response(word)
            if len(noitu_games[chat_id]['players']) == 1 and response and response.split()[0] != user_tail:
                username = message.from_user.username or message.from_user.first_name
                bot.reply_to(message, "BUG cái con cặc !!!")
                game['players'].remove(user_id)
                del game['fails'][user_id]
                del noitu_games[chat_id]
                return
            game['last_word'] = word
            game['turn_index'] = 0
            bot.reply_to(message, f"✅ Trò chơi bắt đầu với từ: {word}")
            if not response:
                bot.reply_to(message, f"🤖 Bot thua vì không nối được từ bắt đầu bằng '{user_tail}'!\n👤 Bạn thắng!\n🚨 Dùng /noitu join để chơi lại nhé!")
                del noitu_games[chat_id]
                return
            bot_head = response.split()[0]
            if bot_head != user_tail:
                bot.reply_to(message, f"🤖 Bot thua vì không nối được từ bắt đầu bằng '{user_tail}'!\n👤 Bạn thắng!\n🚨 Dùng /noitu join để chơi lại nhé!")
                del noitu_games[chat_id]
                return
            game['last_word'] = response
            bot.reply_to(message, f"🤖 Bot nối: {response}\n🆎 Từ tiếp theo phải bắt đầu bằng: {response.split()[-1]}")
            game['turn_index'] = 1 % len(game['players'])
            next_player = game['players'][game['turn_index']]
            next_username = bot.get_chat_member(chat_id, next_player).user.username or bot.get_chat_member(chat_id, next_player).user.first_name
            bot.reply_to(message, f"👤 Lượt tiếp theo: @{next_username}")
            return
        current_player = game['players'][game['turn_index']]
        if user_id != current_player:
            current_username = bot.get_chat_member(chat_id, current_player).user.username or bot.get_chat_member(chat_id, current_player).user.first_name
            bot.reply_to(message, f"🚨 Hiện tại đang là lượt của người dùng: @{current_username}")
            return
        word = message.text.strip()
        if len(word.split()) != 2:
            bot.reply_to(message, "🚫 Bạn phải nhập đúng 2 từ để tiếp tục trò chơi!")
            return
        last_tail = game['last_word'].split()[-1]
        current_head = word.split()[0]
        if last_tail != current_head:
            game['fails'][user_id] += 1
            if game['fails'][user_id] >= 3:
                username = message.from_user.username or message.from_user.first_name
                bot.reply_to(message, f"🚫 @{username} đã nhập sai 3 lần và bị loại khỏi phòng!")
                game['players'].remove(user_id)
                del game['fails'][user_id]
                if game['turn_index'] >= len(game['players']):
                    game['turn_index'] = 0
                if not game['players']:
                    del noitu_games[chat_id]
                else:
                    next_player = game['players'][game['turn_index']]
                    next_username = bot.get_chat_member(chat_id, next_player).user.username or bot.get_chat_member(chat_id, next_player).user.first_name
                    bot.reply_to(message, f"👤 Lượt tiếp theo: @{next_username}")
                return
            bot.reply_to(message, f"Từ của bạn phải bắt đầu bằng '{last_tail}' nhé! 🚨\nBạn còn {3 - game['fails'][user_id]} lượt thử lại trước khi bị loại!")
            return
        result = check_word(word)
        if result != "đúng":
            game['fails'][user_id] += 1
            if game['fails'][user_id] >= 3:
                username = message.from_user.username or message.from_user.first_name
                bot.reply_to(message, f"🚫 @{username} đã nhập sai 3 lần và bị loại khỏi phòng!")
                game['players'].remove(user_id)
                del game['fails'][user_id]
                if game['turn_index'] >= len(game['players']):
                    game['turn_index'] = 0
                if not game['players']:
                    del noitu_games[chat_id]
                else:
                    next_player = game['players'][game['turn_index']]
                    next_username = bot.get_chat_member(chat_id, next_player).user.username or bot.get_chat_member(chat_id, next_player).user.first_name
                    bot.reply_to(message, f"👤 Lượt tiếp theo: @{next_username}")
                return
            bot.reply_to(message, f"Từ này không có trong từ điển! 🚫\nBạn còn {3 - game['fails'][user_id]} lượt thử lại trước khi bị loại!")
            return
        game['fails'][user_id] = 0
        user_tail = word.split()[1]
        response = get_noitu_response(word)
        if not response:
            bot.reply_to(message, f"🤖 Bot thua vì không nối được từ bắt đầu bằng '{user_tail}'!\n👤 Bạn thắng!\n🚨 Dùng /noitu join để chơi lại nhé!")
            del noitu_games[chat_id]
            return
        bot_head = response.split()[0]
        if bot_head != user_tail:
            bot.reply_to(message, f"🤖 Bot thua vì không nối được từ bắt đầu bằng '{user_tail}'!\n👤 Bạn thắng!\n🚨 Dùng /noitu join để chơi lại nhé!")
            del noitu_games[chat_id]
            return
        game['last_word'] = response
        game['turn_index'] = (game['turn_index'] + 1) % len(game['players'])
        next_player = game['players'][game['turn_index']]
        next_username = bot.get_chat_member(chat_id, next_player).user.username or bot.get_chat_member(chat_id, next_player).user.first_name
        bot.reply_to(message, f"🤖 Bot nối: {response}\n🆎 Từ tiếp theo phải bắt đầu bằng: {response.split()[-1]}\n👤 Lượt tiếp theo: @{next_username}")