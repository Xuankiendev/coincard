import json

def get_commands_info():
    commands_info = []
    try:
        with open('assets/commands.json', 'r', encoding='utf-8') as f:
            commands_data = json.load(f)
            for command_name, command_data in commands_data.items():
                commands_info.append(command_data)
    except json.JSONDecodeError:
        print("Lỗi khi phân tích cú pháp JSON!")
    
    return commands_info

def help(message, bot):
    args = message.text.split()
    page = 1
    if len(args) > 1 and args[1].isdigit():
        page = int(args[1])
    
    commands_info = get_commands_info()
    total_pages = (len(commands_info) + 4) // 5
    start = (page - 1) * 5
    end = start + 5
    page_commands = commands_info[start:end]
    
    if not page_commands:
        bot.reply_to(message, f"<blockquote>Không có trang này, tổng số trang hiện có: {total_pages}</blockquote>", parse_mode='HTML')
        return
    
    help_text = f"<blockquote><b>🗒️  Trang {page}/{total_pages}</b></blockquote>\n"
    for command in page_commands:
        help_text += f"\n<blockquote>📊 Lệnh: <b>/{command['name']}</b>\n"
        help_text += f"📝 Mô tả: <b>{command['description']}</b>\n"
        help_text += f"🏷️ Thể loại: <b>{command['commandCategory']}</b>\n"
        help_text += f"📋 Cách sử dụng: <b>{command['usages']}</b>\n"
        help_text += f"🧭 Thời gian chờ: <b>{command['cooldowns']} giây</b>\n"
        help_text += f"👤 Quyền hạn: <b>{get_permission_level(command['hasPermssion'])}</b></blockquote>\n"
        help_text += "-" * 40 + "\n"
    bot.reply_to(message, help_text, parse_mode='HTML')

def get_permission_level(permission):
    if permission == 1:
        return "Thành viên"
    elif permission == 2:
        return "Quản trị viên nhóm"
    elif permission == 3:
        return "Quản trị viên Bot"
    elif permission == 4:
        return "Quản trị viên cấp cao"