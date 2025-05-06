import json
import os
import telebot

group_settings = "assets/data/group_settings.json"

def approve(message, bot):
    try:
        chat = message.chat
        if chat.type not in ['group', 'supergroup']:
            bot.reply_to(message, "🚫 Lệnh này chỉ hoạt động trong nhóm.")
            return
        chat_id = str(chat.id)
        settings = {}
        if os.path.exists(group_settings):
            with open(group_settings, 'r') as f:
                settings = json.load(f)
        group_settings_data = settings.get(chat_id, {"nameGroup": chat.title, "memberApprove": False})
        group_settings_data["nameGroup"] = chat.title
        group_settings_data["memberApprove"] = not group_settings_data["memberApprove"]
        settings[chat_id] = group_settings_data
        os.makedirs(os.path.dirname(group_settings), exist_ok=True)
        with open(group_settings, 'w') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        status = "bật" if group_settings_data["memberApprove"] else "tắt"
        bot.reply_to(message, f"✅ Tự động duyệt thành viên đã được {status} cho nhóm {chat.title}.")
    except Exception as e:
        print(f"Lỗi: {e}")
        bot.reply_to(message, "🚫 Đã xảy ra lỗi khi xử lý lệnh.")

def init(bot):
    @bot.message_handler(content_types=['chat_member'])
    def handle_join_request(message):
        try:
            if not hasattr(message, 'chat_member') or message.chat_member.new_chat_member.status != 'kicked':
                return
            chat_id = str(message.chat.id)
            user_id = message.chat_member.from_user.id
            settings = {}
            if os.path.exists(group_settings):
                with open(group_settings, 'r') as f:
                    settings = json.load(f)
            group_settings_data = settings.get(chat_id, {"memberApprove": False})
            if group_settings_data.get("memberApprove", False):
                bot.approve_chat_join_request(chat_id, user_id)
        except Exception as e:
            print(f"Lỗi: {e}")