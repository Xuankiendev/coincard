import json
import os

admin_file = 'assets/data/list_admin.json'

def addadmin(message, bot):
    try:
        if not message.reply_to_message:
            bot.reply_to(message, "Reply tin nhắn của người cần phong làm Quản trị viên.")
            return
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit() or int(args[1]) not in [2, 3, 4]:
            bot.reply_to(message, "Cú pháp: /addadmin [2/3/4]\n\n2: Quản trị viên nhóm\n3: Quản trị viên Bot\n4: Quản trị viên cấp cao\n\nLưu ý: '1 - Thành viên' nên không tính.")
            return
        permission_level = args[1]
        user_id = str(message.reply_to_message.from_user.id)
        full_name = str(message.reply_to_message.from_user.full_name)
        admin_data = {"2": [], "3": [], "4": []}
        if os.path.exists(admin_file):
            with open(admin_file, 'r') as f:
                admin_data = json.load(f)
        if user_id in admin_data.get(permission_level, []):
            bot.reply_to(message, f"{full_name} với ID {user_id} đã là Quản trị viên cấp {permission_level}.")
            return
        previous_level = None
        for level in ["2", "3", "4"]:
            if level != permission_level and user_id in admin_data.get(level, []):
                admin_data[level].remove(user_id)
                previous_level = level
                break
        admin_data[permission_level].append(user_id)
        with open(admin_file, 'w') as f:
            json.dump(admin_data, f, indent=4, ensure_ascii=False)
        level_names = {"2": "Quản trị viên nhóm", "3": "Quản trị viên Bot", "4": "Quản trị viên cấp cao"}
        if previous_level:
            bot.reply_to(message, f"Đã thăng cấp {full_name} với ID {user_id} từ {level_names[previous_level]} lên {level_names[permission_level]}.")
        else:
            bot.reply_to(message, f"Đã thêm {full_name} với ID {user_id} vào danh sách {level_names[permission_level]}.")
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")