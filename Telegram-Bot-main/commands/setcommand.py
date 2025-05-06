import json
import os

def setcommand(message, bot):
    admin_file = 'assets/data/list_admin.json'
    commands_config_file = 'assets/commands.json'
    commands_dir = 'commands'

    def list_admin():
        try:
            with open(admin_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading list_admin.json: {e}")
            return []

    def load_commands_config():
        try:
            if os.path.exists(commands_config_file):
                with open(commands_config_file, 'r') as f:
                    return json.load(f)
                return {}
        except Exception as e:
            print(f"Error loading commands.json: {e}")
            return {}

    def save_commands_config(data):
        try:
            with open(commands_config_file, 'w') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving commands.json: {e}")

    def load_commands():
        commands = {}
        commands_config = load_commands_config()
        for filename in os.listdir(commands_dir):
            if filename.endswith('.py'):
                cmd_name = filename[:-3]
                if cmd_name in commands_config:
                    commands[cmd_name] = {'config': commands_config[cmd_name], 'enabled': commands_config[cmd_name].get('enabled', True)}
        return commands

    admin_id = list_admin()
    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng sử dụng:\n/setcommand [on/off] [tên lệnh] - Bật/tắt lệnh đó\n/setcommand cd [tên lệnh] [thời gian chờ mới]\n/setcommand p [tên lệnh] [quyền hạn]\n\n[+] 1 - Thành viên\n[+] 2 - Quản trị viên nhóm\n[+] 3 - Quản trị viên Bot\n[+] 4 - Quản trị viên cấp cao")
        return
    action = args[0].lower()
    cmd_name = args[1].lower()
    commands = load_commands()
    if cmd_name not in commands:
        bot.reply_to(message, f"Lệnh {cmd_name} không tồn tại.")
        return
    commands_config = load_commands_config()
    if cmd_name not in commands_config:
        bot.reply_to(message, f"Cấu hình cho lệnh {cmd_name} không tồn tại trong commands.json.")
        return
    if action == 'on':
        commands[cmd_name]['enabled'] = True
        commands_config[cmd_name]['enabled'] = True
        save_commands_config(commands_config)
        bot.reply_to(message, f"Đã bật lệnh {cmd_name}.")
    elif action == 'off':
        commands[cmd_name]['enabled'] = False
        commands_config[cmd_name]['enabled'] = False
        save_commands_config(commands_config)
        bot.reply_to(message, f"Đã tắt lệnh {cmd_name}.")
    elif action == 'cd':
        if len(args) < 3 or not args[2].isdigit():
            bot.reply_to(message, "Cú pháp: /setcommand cd [tên lệnh] [thời gian chờ]")
            return
        cooldown = int(args[2])
        commands[cmd_name]['config']['cooldowns'] = cooldown
        commands_config[cmd_name]['cooldowns'] = cooldown
        save_commands_config(commands_config)
        bot.reply_to(message, f"Đã đặt cooldown cho lệnh {cmd_name} thành {cooldown} giây.")
    elif action == 'p':
        if len(args) < 3 or not args[2].isdigit() or int(args[2]) not in [1, 2, 3, 4]:
            bot.reply_to(message, "Cú pháp: /setcommand p [tên lệnh] [1/2/3/4]\n1: Thành viên\n2: Quản trị viên nhóm\n3: Quản trị viên Bot\n4: Quản trị viên cấp cao")
            return
        permission = int(args[2])
        commands[cmd_name]['config']['hasPermssion'] = permission
        commands_config[cmd_name]['hasPermssion'] = permission
        save_commands_config(commands_config)
        bot.reply_to(message, f"Đã đặt quyền hạn cho {cmd_name} thành {permission}.")
    else:
        bot.reply_to(message, "Hành động không hợp lệ. Sử dụng: on/off/cd/permission")