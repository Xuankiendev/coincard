import telebot, threading, time, requests
from urllib.parse import urlparse

API_KEY = "a76f7a6409973bc34447f0bae64a1445"
SERVICE_ID_TYM = 1889
ADMIN_ID = 7534950201

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def send_buff_once(link, quantity, service_id):
    data = {
        "key": API_KEY,
        "action": "add",
        "service": service_id,
        "link": link,
        "quantity": quantity
    }
    try:
        response = requests.post("https://smmaz.net/api/v2", data=data)
        response.raise_for_status()
        return True
    except:
        return False

def send_buff_repeat(link, quantity, service_id, chat_id):
    try:
        for _ in range(2):
            if not send_buff_once(link, quantity, service_id):
                bot.send_message(chat_id, "Co loi khi buff tym, thu lai sau.")
                return
            time.sleep(600)
        bot.send_message(chat_id, f"Đa buff lai tym cho {link}.")
    except Exception as e:
        bot.send_message(chat_id, f"Co loi xay ra: {e}")

def tymvip(message, bot):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Ban khong co quyen dung lenh nay.")
        return
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.send_message(message.chat.id, "Sai cu phap: /tymvip <link> <so luong>")
            return
        link = args[1]
        quantity = int(args[2])
        if not is_valid_url(link):
            bot.send_message(message.chat.id, "Link khong hop le.")
            return
        if quantity <= 0:
            bot.send_message(message.chat.id, "So luong phai lon hon 0.")
            return
        threading.Thread(target=send_buff_repeat, args=(link, quantity, SERVICE_ID_TYM, message.chat.id), daemon=True).start()
        bot.send_message(message.chat.id, f"Đa gui buff tym VIP cho {link} x{quantity}, se tu buff lai sau 10 phut.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Co loi xay ra: {e}")