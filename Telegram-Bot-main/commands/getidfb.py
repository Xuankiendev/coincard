import requests
from urllib.parse import quote_plus

def getidfb(message, bot):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng nhập link Facebook.\nVí dụ: /getidfb Link Facebook Cần Get")
        return
    try:
        fb_url = quote_plus(args[1])
        api_url = f"https://ffb.vn/api/tool/get-id-fb?idfb={fb_url}"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if data.get("error") == 0:
            reply = (
                f"{data['msg']} ✅\n\n"
                f"🆔 ID: <code>{data['id']}</code>\n"
                f"👤 Tên: {data['name']}\n"
                f"📊 Chi tiết tại: https://www.facebook.com/{data['id']}"
            )
        else:
            reply = f"Lỗi: {data.get('msg', 'Không rõ lỗi')}"
        bot.reply_to(message, reply, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"Lỗi khi gọi API: {str(e)}")