import json
import os

admin_file = 'assets/data/list_admin.json'
group_settings_file = 'assets/data/group_settings.json'

def listadmin(message, bot):
    try:
        chat_admins = bot.get_chat_administrators(message.chat.id)
        admin_data = load_admin()
        group_settings = load_group_settings()
        chat_id = str(message.chat.id)
        indirect_admins = group_settings.get(chat_id, {}).get('adminList', [])
        chat_admin_ids = [str(admin.user.id) for admin in chat_admins]
        chat_admin_ids.extend([admin_id for admin_id in indirect_admins if admin_id not in chat_admin_ids])
        chat_admin_names = []
        for i, admin in enumerate(chat_admins, 1):
            name = admin.user.full_name or admin.user.username or str(admin.user.id)
            chat_admin_names.append(f"{i}. {name}")
        for i, admin_id in enumerate(indirect_admins, len(chat_admin_names) + 1):
            for admin in chat_admins:
                if str(admin.user.id) == admin_id:
                    name = admin.user.full_name or admin.user.username or admin_id
                    chat_admin_names.append(f"{i}. {name}")
                    break
            else:
                chat_admin_names.append(f"{i}. {admin_id} (ID)")
        bot_admins = admin_data.get("3", [])
        senior_admins = admin_data.get("4", [])
        bot_admin_ids = [admin_id for admin_id in bot_admins if admin_id in chat_admin_ids]
        bot_admin_names = []
        for admin_id in bot_admin_ids:
            for admin in chat_admins:
                if str(admin.user.id) == admin_id:
                    name = admin.user.full_name or admin.user.username or admin_id
                    bot_admin_names.append(f"{len(bot_admin_names) + 1}. {name}")
                    break
            else:
                try:
                    user = bot.get_chat_member(message.chat.id, admin_id).user
                    name = user.full_name or user.username or admin_id
                    bot_admin_names.append(f"{len(bot_admin_names) + 1}. {name}")
                except:
                    bot_admin_names.append(f"{len(bot_admin_names) + 1}. {admin_id} (ID)")
        senior_admin_ids = [admin_id for admin_id in senior_admins if admin_id in chat_admin_ids]
        senior_admin_names = []
        for admin_id in senior_admin_ids:
            for admin in chat_admins:
                if str(admin.user.id) == admin_id:
                    name = admin.user.full_name or admin.user.username or admin_id
                    senior_admin_names.append(f"{len(senior_admin_names) + 1}. {name}")
                    break
            else:
                try:
                    user = bot.get_chat_member(message.chat.id, admin_id).user
                    name = user.full_name or user.username or admin_id
                    senior_admin_names.append(f"{len(senior_admin_names) + 1}. {name}")
                except:
                    senior_admin_names.append(f"{len(senior_admin_names) + 1}. {admin_id} (ID)")
        chat_title = bot.get_chat(message.chat.id).title or "Nhóm này"
        response = [f"Danh sách quản trị viên của nhóm {chat_title}:"]
        response.extend(chat_admin_names)
        if bot_admin_names:
            response.append("\nDanh sách quản trị viên Bot trong nhóm này:")
            response.extend(bot_admin_names)
        if senior_admin_names:
            response.append("\nDanh sách quản trị viên cấp cao trong nhóm này:")
            response.extend(senior_admin_names)
        bot.reply_to(message, "\n".join(response))
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")

def load_admin():
    try:
        with open(admin_file, 'r') as f:
            return json.load(f)
    except:
        return {"2": [], "3": [], "4": []}

def load_group_settings():
    try:
        with open(group_settings_file, 'r') as f:
            return json.load(f)
    except:
        return {}