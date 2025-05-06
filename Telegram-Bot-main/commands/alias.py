import json
import os

def alias(message, bot):
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
    commands_config = load_commands_config()
    if not args:
        alias_list = []
        for cmd in commands_config:
            aliases = commands_config[cmd].get('alias', [])
            if aliases:
                alias_list.append(f"{cmd}: {', '.join([f'/{alias}' for alias in aliases])}")
        if alias_list:
            bot.reply_to(message, "Danh sách alias cho các lệnh:\n" + "\n".join(alias_list))
        else:
            bot.reply_to(message, "Vui lòng sử dụng:\n/alias add [tên lệnh gốc] [tên alias]\n/alias remove [tên lệnh gốc] [tên alias]")
        return
    if len(args) < 3 or args[0].lower() not in ['add', 'remove']:
        bot.reply_to(message, "Cú pháp: /alias [add/remove] [tên lệnh gốc] [tên alias]")
        return
    action, cmd_name, alias_name = args[0].lower(), args[1].lower(), args[2].lower()
    commands = load_commands()
    if cmd_name not in commands:
        bot.reply_to(message, f"Lệnh {cmd_name} không tồn tại.")
        return
    if cmd_name not in commands_config:
        bot.reply_to(message, f"Cấu hình cho lệnh {cmd_name} không tồn tại trong commands.json.")
        return
    if action == 'add':
        for cmd in commands_config:
            if alias_name == cmd or alias_name in commands_config[cmd].get('alias', []):
                bot.reply_to(message, f"Alias {alias_name} đã được sử dụng.")
                return
        if 'alias' not in commands_config[cmd_name]:
            commands_config[cmd_name]['alias'] = []
        commands_config[cmd_name]['alias'].append(alias_name)
        commands[cmd_name]['config']['alias'] = commands_config[cmd_name]['alias']
        save_commands_config(commands_config)
        bot.reply_to(message, f"Đã thêm alias {alias_name} cho lệnh {cmd_name}.")
    elif action == 'remove':
        if 'alias' not in commands_config[cmd_name] or alias_name not in commands_config[cmd_name]['alias']:
            bot.reply_to(message, f"Alias {alias_name} không tồn tại cho lệnh {cmd_name}.")
        else:
            commands_config[cmd_name]['alias'].remove(alias_name)
            commands[cmd_name]['config']['alias'] = commands_config[cmd_name]['alias']
            save_commands_config(commands_config)
            bot.reply_to(message, f"Đã xóa alias {alias_name} khỏi lệnh {cmd_name}.")