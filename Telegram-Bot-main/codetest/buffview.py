import telebot
import threading, time, requests
from urllib.parse import urlparse

API_KEY = "a76f7a6409973bc34447f0bae64a1445"
SERVICE_ID_VIEW = 592
MAX_BUFF_VIEW = 1000

buffview_data = {}
user_data_lock = threading.Lock()

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
    except requests.exceptions.RequestException as e:
        print(f"Loi khi gui yeu cau API: {e}")
        return False

def buffview(message, bot):
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_time = time.time()

    with user_data_lock:
        user_info = buffview_data.get(user_id, {"last": 0, "count": 0, "links": []})
        last_time = user_info["last"]

    if current_time - last_time >= 600:
        try:
            args = message.text.split()
            if len(args) < 3:
                bot.send_message(chat_id, "Sai cu phap: /buffview <link> <so luong>")
                return

            link = args[1]
            quantity = int(args[2])

            if not is_valid_url(link):
                bot.send_message(chat_id, "Link khong hop le.")
                return

            if quantity <= 0:
                bot.send_message(chat_id, "So luong phai lon hon 0.")
                return

            if quantity > MAX_BUFF_VIEW:
                bot.send_message(chat_id, f"So luong toi da cho moi lan la {MAX_BUFF_VIEW} view.")
                return

            with user_data_lock:
                if user_info["count"] >= MAX_BUFF_VIEW:
                    bot.send_message(chat_id, f"Ban da dat gioi han buff view ({MAX_BUFF_VIEW}).")
                    return

                if link in user_info["links"]:
                    bot.send_message(chat_id, "Ban da buff link nay truoc do roi. Vui long dung link khac.")
                    return

                if send_buff_once(link, quantity, SERVICE_ID_VIEW):
                    user_info["last"] = current_time
                    user_info["count"] += 1
                    user_info["links"].append(link)
                    buffview_data[user_id] = user_info
                    bot.send_message(chat_id, f"Da buff view cho {link} x{quantity}.")
                else:
                    bot.send_message(chat_id, "Co loi khi buff view, thu lai sau.")

        except Exception as e:
            print(f"Loi khong mong muon: {e}")
            bot.send_message(chat_id, "Co loi xay ra khi xu ly. Vui long thu lai.")
    else:
        wait = int(600 - (current_time - last_time))
        bot.send_message(chat_id, f"Ban can doi {wait} giay nua moi buff tiep.")