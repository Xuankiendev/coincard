import requests

def fetch_ip_info(ip):
    try:
        response = requests.get(f'https://ipwho.is/{ip}')
        data = response.json()
        if data.get('success'):
            return data
        return None
    except Exception as e:
        print(f"Lỗi lấy thông tin IP: {e}")
        return None

def ipinfo(message, bot):
    chat_id = message.chat.id
    ip = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None
    if not ip:
        bot.reply_to(message, "🚫 Vui lòng cung cấp địa chỉ IP")
        return
    info = fetch_ip_info(ip)
    if not info:
        bot.reply_to(message, "🚫 Lỗi lấy thông tin IP")
        return
    msg_text = (
        f"<b>📍 Thông tin IP: {info['ip']}</b>\n\n"
        f"🌍 Quốc gia: {info['country']} ({info['country_code']})\n"
        f"🗺️ Khu vực: {info['region']} ({info['region_code']})\n"
        f"🏙️ Thành phố: {info['city']}\n"
        f"📍 Vĩ độ: {info['latitude']}\n"
        f"📍 Kinh độ: {info['longitude']}\n"
        f"🏳️ Cờ: {info['flag']['emoji']}\n"
        f"📞 Mã gọi: +{info['calling_code']}\n"
        f"🌐 Nhà cung cấp: {info['connection']['isp']}\n"
        f"🕒 Múi giờ: {info['timezone']['id']} ({info['timezone']['utc']})"
    )
    bot.reply_to(message, msg_text, parse_mode='HTML')