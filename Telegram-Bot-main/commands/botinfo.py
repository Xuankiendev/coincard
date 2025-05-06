from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

def botinfo(message, bot):
    chat_id = message.chat.id
    try:
        bot_info = bot.get_me()
        with open('assets/data/group_settings.json', 'r') as f:
            group_settings = json.load(f)
        chat_id_str = str(chat_id)
        settings_info = ""
        if chat_id_str in group_settings:
            settings = group_settings[chat_id_str]
            bot_status = "Bật" if settings.get("botStatus", "on") == "on" else "Tắt"
            auto_translator = "Bật" if settings.get("autoTranslator", {}).get("enabled", False) else "Tắt"
            member_approve = "Bật" if settings.get("memberApprove", False) else "Tắt"
            auto_pr = "Bật" if settings.get("autoPR", []) else "Tắt"
            settings_info = (
                f"📊 <b>Cấu hình nhóm:</b>\n"
                f"   - 💬 Tương tác với thành viên: {bot_status}\n"
                f"   - ⛔ Tự động dịch: {auto_translator}\n"
                f"   - 👥 Phê duyệt thành viên: {member_approve}\n"
                f"   - 🔞 Tự động gửi tin nhắn quảng cáo: {auto_pr}\n"
            )
        else:
            settings_info = "⚙ <b>Cấu hình nhóm:</b> Tất cả cấu hình đang tắt\n"
        caption = (
            f"<b>{bot_info.first_name}</b>\n\n"
            f"🆔 <b>ID:</b> {bot_info.id}\n"
            f"📛 <b>Name:</b> {bot_info.first_name}\n"
            f"📝 <b>Username:</b> @{bot_info.username}\n"
            f"👤 <b>Admin:</b> Vũ Xuân Kiên (@xkprj)\n\n"
            f"{settings_info}\n"
            "<i><span class=\"tg-spoiler\">I am a utility bot created by Vũ Xuân Kiên, an admin in the V X K Community Service team. "
            "Share me with your friends to experience together!</span></i>\n\n"
            "<b>📌 Lưu ý:</b> Bot sẽ không hoạt động nếu không được kích hoạt bởi Admin. "
            "Liên hệ Admin để yêu cầu sử dụng/thuê Bot."
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(
                text="➕ Add Bot To Group",
                url=f"https://t.me/{bot_info.username}?startgroup=botstart"
            ),
            InlineKeyboardButton(
                text="☎ Contact Admin",
                url="https://kiendev.netlify.app/"
            )
        )
        user_photos = bot.get_user_profile_photos(bot_info.id, limit=1)
        if user_photos.total_count > 0:
            photo = user_photos.photos[0][-1]
            bot.send_photo(
                chat_id=chat_id,
                photo=photo.file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )
    except Exception as e:
        error_message = f"🚫  Lỗi khi lấy/gửi thông tin Bot: {str(e)}"
        bot.reply_to(
            message=message,
            text=error_message,
            parse_mode="HTML"
        )