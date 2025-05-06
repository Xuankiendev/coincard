import requests
import json

def fbinfo(message, bot):
    args = message.text.split(' ', 1)
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng cung cấp UID Facebook. Ví dụ: /facebookinfo 61554905537405", parse_mode='HTML')
        return
    uid = args[1]
    api_url = f"https://keyherlyswar.x10.mx/Apidocs/getinfofb.php?uid={uid}"
    response = requests.get(api_url)
    data = response.json()
    if 'id' not in data:
        bot.reply_to(message, f"Không tìm thấy thông tin của người dùng với UID {uid}.", parse_mode='HTML')
        return
    username = data.get('username', 'N/A')
    name = data.get('name', '').strip()
    avatar = data.get('cover', {}).get('source', '')
    created_time = data.get('created_time', 'N/A')
    birthday = data.get('birthday', 'N/A')
    subscribers = data.get('subscribers', {}).get('summary', {}).get('total_count', 0)
    posts = data.get('posts', {}).get('data', [])
    caption_short = f"👤 <b>Thông tin người dùng Facebook</b>\n" \
                    f"📛 Tên người dùng: <a href='https://www.facebook.com/{username}'>{username}</a>\n" \
                    f"💳 Họ tên: {name}\n" \
                    f"🧭 Thời gian tạo: {created_time}\n" \
                    f"📅  Sinh nhật: {birthday}\n" \
                    f"🔢 Số người theo dõi: {subscribers}"
    bot.send_photo(message.chat.id, avatar, caption=caption_short, parse_mode='HTML', reply_to_message_id=message.message_id)
    content = "📋 <b>Danh sách bài đăng gần đây:</b>\n"
    for i, post in enumerate(posts[:5], 1):
        post_message = post.get('message', 'N/A')
        created_time = post.get('created_time', 'N/A')
        story = post.get('story', '')
        comments_count = len(post.get('comments', {}).get('data', []))
        shares_count = post.get('shares', {}).get('count', 0) if 'shares' in post else 0
        content += f"""<blockquote>{i}. <b>{post_message}</b>
📅 {created_time} | 💬 {comments_count} bình luận | 🔄 {shares_count} lượt chia sẻ
Câu chuyện: {story}</blockquote>"""
        content += "---------------------\n"
    content += "<blockquote><b>👨‍💻 Facebook Account Information Check API Created And Provided By Programmer Vu Xuan Kien Nickname Vxkitvn</b></blockquote>"
    bot.send_message(message.chat.id, content, parse_mode='HTML')