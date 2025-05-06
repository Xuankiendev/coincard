import telebot
import json
import os
import importlib.util
import sys
from colorama import Fore, init
import time
import threading
from logging_utils import Logging
import subprocess

init(autoreset=True)
logger = Logging()
token = '7687550929:AAEBNhw-76nKtpKYJ71Z6VV5eGOVsuZ4iBc'
bot = telebot.TeleBot(token)
admin_id = []
commands_dir = 'commands'
commands_config_file = 'assets/commands.json'
admin_file = 'assets/data/list_admin.json'
group_settings_file = 'assets/data/group_settings.json'
cooldowns = {}
cooldown_lock = threading.Lock()

if not os.path.exists(commands_dir):
    os.makedirs(commands_dir)

if not os.path.exists('assets/data'):
    os.makedirs('assets/data')

if not os.path.exists(admin_file):
    with open(admin_file, 'w') as f:
        json.dump({
            "2": [],
            "3": [],
            "4": ["6601930239"]
        }, f)

def list_admin():
    try:
        with open(admin_file, 'r') as f:
            return json.load(f)
    except:
        return {"2": [], "3": [], "4": []}

def save_admin(admin_data):
    try:
        with open(admin_file, 'w') as f:
            json.dump(admin_data, f, indent=4, ensure_ascii=False)
    except:
        pass

admin_id = list_admin()

def load_group_settings():
    try:
        with open(group_settings_file, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_group_settings(settings):
    try:
        with open(group_settings_file, 'w') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except:
        pass

def load_commands_config():
    try:
        if os.path.exists(commands_config_file):
            with open(commands_config_file, 'r') as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_commands_config(data):
    try:
        with open(commands_config_file, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except:
        pass

def load_commands():
    commands = {}
    loaded_dirs = []
    if os.path.exists(commands_dir):
        loaded_dirs.append(commands_dir)
    if os.path.exists('assets'):
        loaded_dirs.append('assets')
    logger.success(f"Load thành công các folder: {', '.join(loaded_dirs)}")
    commands_config = load_commands_config()
    loaded_commands = []
    for filename in os.listdir(commands_dir):
        if filename.endswith('.py'):
            file_key = filename[:-3]
            if file_key in commands_config:
                try:
                    file_path = os.path.join(commands_dir, filename)
                    spec = importlib.util.spec_from_file_location(file_key, file_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[file_key] = module
                    spec.loader.exec_module(module)
                    cmd_name = commands_config[file_key]['name']
                    if hasattr(module, cmd_name):
                        commands[file_key] = {
                            'module': module,
                            'config': commands_config[file_key],
                            'enabled': commands_config[file_key].get('enabled', True)
                        }
                        if hasattr(module, 'init'):
                            try:
                                getattr(module, 'init')(bot)
                            except:
                                pass
                        loaded_commands.append(cmd_name)
                    else:
                        logger.error(f"Lỗi khi load lệnh {cmd_name}: Không tìm thấy hàm {cmd_name} trong {filename}")
                except Exception as e:
                    logger.error(f"Lỗi khi load lệnh {file_key}: {e}")
            else:
                logger.warning(f"Bỏ qua {filename}, lý do: Không tìm thấy trong commands.json")
    logger.success(f"Load thành công các lệnh")
    return commands

commands = load_commands()

def execute_command(cmd, target_cmd, message):
    try:
        user_id = str(message.from_user.id)
        admin_data = list_admin()
        user_permission = 1
        if message.chat.type in ['group', 'supergroup']:
            try:
                chat_member = bot.get_chat_member(message.chat.id, user_id)
                if chat_member.status in ['administrator', 'creator']:
                    user_permission = 2
                group_settings = load_group_settings()
                chat_id = str(message.chat.id)
                if chat_id in group_settings and user_id in group_settings[chat_id].get('adminList', []):
                    user_permission = 2
            except:
                pass
        if user_id in admin_data.get("3", []):
            user_permission = 3
        if user_id in admin_data.get("4", []):
            user_permission = 4
        permission = cmd['config']['hasPermssion']
        group_settings = load_group_settings()
        chat_id = str(message.chat.id)
        bot_status = group_settings.get(chat_id, {}).get('botStatus', 'on')
        if bot_status == 'off' and user_permission < 2:
            return
        if user_permission < permission:
            if permission == 4:
                bot.reply_to(message, "Chỉ quản trị viên cấp cao có thể sử dụng lệnh này.")
            elif permission == 3:
                bot.reply_to(message, "Chỉ admin bot có thể sử dụng lệnh này.")
            elif permission == 2:
                bot.reply_to(message, "Lệnh này chỉ dành cho quản trị viên nhóm hoặc admin bot.")
            else:
                bot.reply_to(message, "Bạn không có quyền sử dụng lệnh này.")
            return
        if user_permission < 4:
            if not cmd['enabled']:
                bot.reply_to(message, f"Lệnh {target_cmd} hiện đang bị tắt.")
                return
            cooldown意味 = f"{user_id}_{target_cmd}"
            current_time = time.time()
            cooldown_duration = cmd['config'].get('cooldowns', 0)
            with cooldown_lock:
                if cooldown_key in cooldowns:
                    last_used = cooldowns[cooldown_key]
                    time_passed = current_time - last_used
                    if time_passed < cooldown_duration:
                        remaining_time = int(cooldown_duration - time_passed)
                        try:
                            bot.set_message_reaction(
                                chat_id=message.chat.id,
                                message_id=message.message_id,
                                reaction=[telebot.types.ReactionTypeEmoji(emoji="🗿")]
                            )
                        except:
                            pass
                        return
                cooldowns[cooldown_key] = current_time
        getattr(cmd['module'], cmd['config']['name'])(message, bot)
    except Exception as e:
        logger.error(f"Lỗi khi thực thi lệnh {target_cmd}: {e}")
        try:
            bot.reply_to(message, f"Lỗi khi thực thi lệnh {target_cmd}: {str(e)}")
        except:
            pass

@bot.message_handler(func=lambda message: hasattr(message, 'text') and message.text.startswith('/'))
def handle_commands(message):
    try:
        user_id = str(message.from_user.id)
        admin_data = list_admin()
        group_settings = load_group_settings()
        chat_id = str(message.chat.id)
        user_permission = 1
        if message.chat.type in ['group', 'supergroup']:
            try:
                chat_member = bot.get_chat_member(message.chat.id, user_id)
                if chat_member.status in ['administrator', 'creator']:
                    user_permission = 2
                if chat_id in group_settings and user_id in group_settings[chat_id].get('adminList', []):
                    user_permission = 2
            except:
                pass
        if user_id in admin_data.get("3", []):
            user_permission = 3
        if user_id in admin_data.get("4", []):
            user_permission = 4
        bot_status = group_settings.get(chat_id, {}).get('botStatus', 'on')
        if message.chat.type in ['group', 'supergroup']:
            if bot_status == 'off' and user_permission < 2:
                return
        elif message.chat.type == 'private' and user_permission < 3:
            group_info = []
            for group_id in group_settings:
                if group_settings[group_id].get('botStatus', 'on') == 'on':
                    try:
                        chat = bot.get_chat(group_id)
                        if chat.username:
                            group_info.append(f"@{chat.username}")
                        else:
                            group_info.append(f"https://t.me/c/{group_id[4:]}")
                    except:
                        pass
            bot.reply_to(message, f"Bot chỉ hoạt động với những người là Quản trị viên Bot hoặc Quản trị viên cấp cao, bạn cũng có thể tham gia các nhóm dưới đây:\n\n{', '.join(group_info) if group_info else 'Không có nhóm nào'}\n\nVì đây là những nhóm mà bot được bật và có thể hoạt động!")
            return
        cmd_name = message.text.split()[0][1:].lower()
        commands_config = load_commands_config()
        target_cmd = None
        for cmd in commands_config:
            if cmd_name == commands_config[cmd]['name'] or cmd_name in commands_config[cmd].get('alias', []):
                target_cmd = cmd
                break
        if target_cmd in commands:
            cmd = commands[target_cmd]
            if bot_status == 'on' or user_permission >= 2:
                thread = threading.Thread(target=execute_command, args=(cmd, cmd_name, message))
                thread.start()
            else:
                bot.reply_to(message, "Bot hiện đang tắt, chỉ quản trị viên nhóm hoặc cao hơn mới có thể sử dụng lệnh.")
        else:
            bot.reply_to(message, f"Không tìm thấy lệnh '/{cmd_name}', sử dụng '/help' để biết các lệnh có trong hệ thống.")
    except Exception as e:
        logger.error(f"Lỗi khi xử lý lệnh {message.text}: {e}")
        try:
            bot.reply_to(message, "Có lỗi xảy ra, vui lòng thử lại sau.")
        except:
            pass

COLORS = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

def banner():
    text = '''
██╗░░░██╗██╗░░██╗██╗░░██╗██╗██╗░░░██╗███████╗
██║░░░██║╚██╗██╔╝██║░██╔╝██║██║░░░██║██╔════╝
╚██╗░██╔╝░╚███╔╝░█████═╝░██║██║░░░██║█████╗░░
░╚████╔╝░░██╔██╗░██╔═██╗░██║██║░░░██║██╔══╝░░
░░╚██╔╝░░██╔╝╚██╗██║░╚██╗██║╚██████╔╝███████╗
░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░╚═════╝░╚══════╝
'''
    for i, char in enumerate(text):
        color = COLORS[i % len(COLORS)]
        print(color + char, end='')

if __name__ == "__main__":
    banner()
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            logger.error(f"Lỗi khi xử lí/đọc tin nhắn: {e}")
            time.sleep(5)