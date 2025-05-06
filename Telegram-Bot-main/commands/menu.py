import json

menu_data = {}

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

def menu(message, bot):
    commands_info = get_commands_info()
    categories = {}
    for cmd in commands_info:
        category = cmd['commandCategory']
        if category not in categories:
            categories[category] = []
        categories[category].append(cmd)
    category_list = list(categories.keys())
    text = "<b>📚 Danh sách lệnh của bot:</b>\n"
    for i, category in enumerate(category_list, start=1):
        command_count = len(categories[category])
        text += f"{i}. {category} - {command_count}\n"
    text += "\nTrả lời tin nhắn này với số thứ tự Category để xem lệnh."
    sent = bot.send_message(message.chat.id, text, parse_mode='HTML')
    menu_data[sent.message_id] = {
        "category_list": category_list,
        "categories": categories,
        "menu_msg_id": sent.message_id
    }

def init(bot):
    @bot.message_handler(func=lambda msg: msg.reply_to_message and msg.reply_to_message.message_id in menu_data)
    def handle_menu_reply(msg):
        data = menu_data.get(msg.reply_to_message.message_id)
        if not msg.text.isdigit():
            bot.reply_to(msg, "❓")
            return
        index = int(msg.text)
        if index < 1 or index > len(data['category_list']):
            bot.reply_to(msg, "Số bạn nhập không nằm trong danh sách Category lệnh.")
            return
        try:
            bot.delete_message(msg.chat.id, data['menu_msg_id'])
        except:
            pass
        selected_category = data['category_list'][index - 1]
        commands = data['categories'][selected_category]
        text = f"<b>📊 Danh mục: {selected_category}</b>\n"
        for cmd in commands:
            text += f"\n<b>/{cmd['name']}</b> - {cmd['description']}"
        bot.send_message(msg.chat.id, text, parse_mode='HTML')