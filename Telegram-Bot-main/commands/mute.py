import re
import time
from datetime import timedelta
from telebot import types

def parse_duration(duration_str):
    if not duration_str:
        return None
    match = re.match(r'^(\d+)([dhms])$', duration_str)
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    if unit == 'd':
        return timedelta(days=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    elif unit == 's':
        return timedelta(seconds=value)
    return None

def get_user_id(message, args, bot):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id
    if args and args[0].startswith('@'):
        username = args[0][1:]
        try:
            member = bot.get_chat_member(message.chat.id, username)
            return member.user.id
        except:
            return None
    return None

def mute(message, bot):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    duration = None
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        if args:
            duration = parse_duration(args[0])
    elif args:
        if re.match(r'^\d+[dhms]$', args[0]) and len(args) > 1 and args[1].startswith('@'):
            duration = parse_duration(args[0])
            user_id = get_user_id(message, [args[1]], bot)
        elif args[0].startswith('@'):
            user_id = get_user_id(message, [args[0]], bot)
    if not user_id:
        bot.reply_to(message, "Không tìm thấy người dùng. Hãy dùng @mention hoặc reply tin nhắn.")
        return
    until_date = int(time.time() + duration.total_seconds()) if duration else 0
    try:
        bot.restrict_chat_member(
            message.chat.id,
            user_id,
            permissions=types.ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            ),
            until_date=until_date
        )
        duration_str = f"trong {args[0]}" if duration else "vĩnh viễn"
        bot.reply_to(message, f"Đã mute người dùng {duration_str}.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi khi mute: {str(e)}")