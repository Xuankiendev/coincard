from telebot import types

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

def unmute(message, bot):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif args:
        if args[0].startswith('@'):
            user_id = get_user_id(message, [args[0]], bot)
    if not user_id:
        bot.reply_to(message, "Không tìm thấy người dùng. Hãy dùng @mention hoặc reply tin nhắn.")
        return
    try:
        bot.restrict_chat_member(
            message.chat.id,
            user_id,
            permissions=types.ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )
        bot.reply_to(message, "Đã unmute người dùng.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi khi unmute: {str(e)}")
