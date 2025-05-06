import requests
from urllib.parse import quote_plus

def shortlink(message, bot):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng cung cấp URL cần rút gọn!\nVí dụ: /shortlink https://example.com")
        return
    try:
        original_url = args[1].strip()
        api_token = "fb279f51506a0cb079f5af04a49cfd357b23e18333cc4519872cf4e5b7344f9f"
        api_url = f"https://yeumoney.com/QL_api.php?token={api_token}&format=json&url={quote_plus(original_url)}"
        response = requests.get(api_url)
        data = response.json()
        if data.get("status") == "success":
            shortened_url = data.get("shortenedUrl")
            bot.reply_to(message, f"Link rút gọn: {shortened_url}")
        else:
            bot.reply_to(message, "Không thể rút gọn link. Vui lòng thử lại!")
    except Exception as e:
        bot.reply_to(message, "Đã xảy ra lỗi khi rút gọn link!")