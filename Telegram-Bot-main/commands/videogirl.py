import random

def videogirl(message, bot):
    try:
        with open('assets/vdgirl.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if not lines:
            bot.reply_to(message, "Không có video nào trong danh sách!")
            return
        with open('assets/z_thinh_girl.txt', 'r', encoding='utf-8') as thinh_file:
            thinh_lines = thinh_file.readlines()
        thinh = "Không có câu thính nào!" if not thinh_lines else random.choice(thinh_lines).strip()
        video_url = random.choice(lines).strip()
        full_name = message.from_user.full_name
        bot.send_video(message.chat.id, video_url, caption=f"[ {full_name} ]\n{thinh}")
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {str(e)}")