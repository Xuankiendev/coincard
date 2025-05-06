import telebot
from deep_translator import GoogleTranslator
import json
import os

translator_data = {}
languages = {'1': 'en', '2': 'vi', '3': 'fr', '4': 'es', '5': 'zh-CN', '6': 'ja', '7': 'ko', '8': 'de'}
lang_names = {'1': 'Tiếng Anh', '2': 'Tiếng Việt', '3': 'Tiếng Pháp', '4': 'Tiếng Tây Ban Nha', '5': 'Tiếng Trung', '6': 'Tiếng Nhật', '7': 'Tiếng Hàn', '8': 'Tiếng Đức'}

def load_settings():
    if os.path.exists('assets/data/group_settings.json'):
        with open('assets/data/group_settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    os.makedirs('assets/data', exist_ok=True)
    with open('assets/data/group_settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def translator(message, bot):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "<blockquote>Lệnh này chỉ hoạt động trong nhóm.</blockquote>", parse_mode='HTML')
        return
    chat_id = str(message.chat.id)
    group_name = message.chat.title
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "<blockquote>Vui lòng dùng: /translator on hoặc /translator off</blockquote>", parse_mode='HTML')
        return
    settings = load_settings()
    settings.setdefault(chat_id, {'nameGroup': group_name, 'memberApprove': False, 'autoTranslator': {'enabled': False, 'lang': None}})
    action = args[1].lower()
    if action == 'on':
        lang_list = '\n'.join(f"{k}. {languages[k]} ({lang_names[k]})" for k in languages)
        sent_msg = bot.reply_to(message, f"<blockquote>Reply số thứ tự để chọn ngôn ngữ:\n{lang_list}</blockquote>", parse_mode='HTML')
        bot.register_next_step_handler(sent_msg, lambda msg: select_language(msg, bot, chat_id, group_name, sent_msg.message_id, settings))
    elif action == 'off':
        settings[chat_id]['autoTranslator'] = {'enabled': False, 'lang': None}
        save_settings(settings)
        translator_data[chat_id] = {'enabled': False, 'lang': None}
        bot.reply_to(message, f"<blockquote>Đã tắt translator cho nhóm {group_name}.</blockquote>", parse_mode='HTML')
    else:
        bot.reply_to(message, "<blockquote>Vui lòng dùng: /translator on hoặc /translator off</blockquote>", parse_mode='HTML')

def select_language(message, bot, chat_id, group_name, lang_msg_id, settings):
    if message.text in languages:
        settings[chat_id]['autoTranslator'] = {'enabled': True, 'lang': languages[message.text]}
        save_settings(settings)
        translator_data[chat_id] = {'enabled': True, 'lang': languages[message.text]}
        bot.reply_to(message, f"<blockquote>Đã bật translator sang {lang_names[message.text]} cho nhóm {group_name}.</blockquote>", parse_mode='HTML')
        bot.delete_message(chat_id, lang_msg_id)
    else:
        bot.reply_to(message, "<blockquote>Vui lòng chọn số thứ tự hợp lệ.</blockquote>", parse_mode='HTML')

def init(bot):
    @bot.message_handler(content_types=['text'], func=lambda msg: str(msg.chat.id) in translator_data and translator_data[str(msg.chat.id)]['enabled'] and msg.text and not msg.text.startswith('/'))
    def handle_translator_message(msg):
        chat_id = str(msg.chat.id)
        lang = translator_data[chat_id]['lang']
        try:
            translated = GoogleTranslator(source='auto', target=lang).translate(msg.text)
            bot.reply_to(msg, translated)
        except:
            bot.reply_to(msg, "Xin lỗi, không thể dịch lúc này.")