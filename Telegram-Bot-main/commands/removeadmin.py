import json
import os

admin_file = 'assets/data/list_admin.json'

def removeadmin(message, bot):
    try:
        if not message.reply_to_message:
            bot.reply_to(message, "Reply tin nhắn của người cần xóa khỏi danh sách Quản trị viên.")
            return
        user_id = str(message.reply_to_message.from_user.id)
        full_name = str(message.reply_to_message.from_user.full_name)
        admin_data = {"2": [], "3": [], "4": []}
        if os.path.exists(admin_file):
            with open(admin_file, 'r') as f:
                admin_data = json.load(f)
        found_level = None
        for level in ["2", "3", "4"]:
            if user_id in admin_data.get(level, []):
                found_level = level
                break
        if not found_level:
            bot.reply_to(message, f"{full_name} với ID {user_id} không phải Quản trị viên.")
            return
        admin_data[found_level].remove(user_id)
        with open(admin_file, 'w') as f:
            json.dump(admin_data, f, indent=4, ensure_ascii=False)
        level_names = {"2": "Quản trị viên nhóm", "3": "Quản trị viên Bot", "4": "Quản trị viên cấp cao"}
        bot.reply_to(message, f"Đã xóa {full_name} với ID {user_id} khỏi danh sách {level_names[found_level]}.")
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")