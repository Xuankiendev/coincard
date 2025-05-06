import telebot, threading, time, requests
from urllib.parse import urlparse

API_KEY = "a76f7a6409973bc34447f0bae64a1445"
SERVICE_ID_TYM = 1889
MAX_BUFF_TYM = 10

bufftym_data = {}
user_data_lock = threading.Lock()

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
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
        res = requests.post("https://smmaz.net/api/v2", data=data)
        res.raise_for_status()
        return True
    except:
        return False

def bufftym(message, bot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    try:
        args = message.text.split(maxsplit=2)
        link = args[1]
        quantity = int(args[2])
    except:
        bot.reply_to(message, "Sai cú pháp: /bufftym <link> <số lượng>")
        return
    if not is_valid_url(link):
        bot.reply_to(message, "Link không hợp lệ.")
        return
    if quantity <= 0:
        bot.reply_to(message, "Số lượng phải lớn hơn 0.")
        return
    if quantity > MAX_BUFF_TYM:
        bot.reply_to(message, f"Số lượng tối đa là {MAX_BUFF_TYM} tym.")
        return
    current_time = time.time()
    with user_data_lock:
        data = bufftym_data.get(user_id, {"last": 0, "count": 0, "links": []})
        if current_time - data["last"] < 600:
            wait = int(600 - (current_time - data["last"]))
            bot.reply_to(message, f"Bạn cần đợi {wait} giây nữa mới được buff tiếp.")
            return
        if data["count"] >= MAX_BUFF_TYM:
            bot.reply_to(message, f"Bạn đã đạt giới hạn {MAX_BUFF_TYM} link khác nhau.")
            return
        if link in data["links"]:
            bot.reply_to(message, "Bạn đã buff link này trước đó. Vui lòng dùng link khác.")
            return
        success = send_buff_once(link, quantity, SERVICE_ID_TYM)
        if success:
            data["last"] = current_time
            data["count"] += 1
            data["links"].append(link)
            bufftym_data[user_id] = data
            bot.reply_to(message, f"Đã buff tym cho {link} x{quantity}. ({data['count']}/{MAX_BUFF_TYM})")
        else:
            bot.reply_to(message, "Có lỗi khi buff tym, thử lại sau.")