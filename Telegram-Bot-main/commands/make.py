import requests
import random

def make(message, bot):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng cung cấp nội dung cần vẽ\nVí dụ: /make Nội dung cần vẽ")
        return
    prompt = args[1]
    chat_id = message.chat.id
    try:
        encoded_prompt = requests.utils.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={random.randint(1, 10000)}&nologo=true&model=flux"
        bot.send_photo(chat_id, image_url, reply_to_message_id=message.message_id)
    except Exception as e:
        bot.reply_to(message, f"Lỗi khi tạo ảnh: {str(e)}")