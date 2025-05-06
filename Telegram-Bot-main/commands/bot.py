import json
import os

def bot(message, bot):
    chat_id = str(message.chat.id)
    group_settings_file = 'assets/data/group_settings.json'
    try:
        with open(group_settings_file, 'r') as f:
            group_settings = json.load(f)
    except:
        bot.reply_to(message, "Lỗi khi đọc file cấu hình")
        return
    args = message.text.split()
    current_status = group_settings[chat_id].get('botStatus', 'on')
    if len(args) == 1:
        new_status = 'off' if current_status == 'on' else 'on'
    elif len(args) == 2 and args[1].lower() in ['on', 'off']:
        new_status = args[1].lower()
    else:
        bot.reply_to(message, "Sử dụng: /bot hoặc /bot on|off")
        return
    group_settings[chat_id]['botStatus'] = new_status
    try:
        with open(group_settings_file, 'w') as f:
            json.dump(group_settings, f, indent=4, ensure_ascii=False)
        bot.reply_to(message, f"Bot đã được {'bật' if new_status == 'on' else 'tắt'}")
    except:
        bot.reply_to(message, "Lỗi khi lưu trạng thái bot")