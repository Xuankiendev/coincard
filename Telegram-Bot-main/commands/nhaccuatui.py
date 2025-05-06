import telebot
import json
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re

nhaccuatui_data = {}

def search_nhaccuatui(keyword):
    url = f"https://www.nhaccuatui.com/tim-kiem/bai-hat?q={quote_plus(keyword)}&b=keyword&l=tat-ca&s=default"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for song in soup.select(".sn_search_returns_list_song .sn_search_single_song"):
        song_link = song.find("a")
        if not song_link:
            continue
        title = song_link.get("title", "").strip()
        key = song_link.get("key", "")
        href = song_link.get("href", "")
        artist_tag = song.find(class_="name_singer")
        artist = artist_tag.text.strip() if artist_tag else "Không rõ"
        thumb_tag = song_link.find(class_="thumb")
        thumbnail = ""
        if thumb_tag:
            thumbnail = thumb_tag.get("data-src") or thumb_tag.get("src", "")
            if thumbnail and not thumbnail.startswith("http"):
                thumbnail = f"https://www.nhaccuatui.com{thumbnail}"
            if thumbnail:
                thumbnail = thumbnail.replace(".jpg", "_600.jpg")
        results.append({"id": key, "songLink": href, "title": title, "artistsNames": artist, "thumbnail": thumbnail})
    return results

def get_nct_stream_url(song_id, song_link):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nhaccuatui.com/"
    }
    response = requests.get(song_link, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all("script")
    key = None
    for script in scripts:
        content = script.string or ""
        match = re.search(r"key1=([a-f0-9]{32})", content, re.I)
        if match:
            key = match.group(1)
            break
    if not key:
        return None
    xml_url = f"https://www.nhaccuatui.com/flash/xml?html5=true&key1={key}"
    xml_response = requests.get(xml_url, headers=headers)
    xml_soup = BeautifulSoup(xml_response.text, 'html.parser')
    stream_tag = xml_soup.find("locationHQ") or xml_soup.find("location")
    if stream_tag:
        return stream_tag.text.strip()
    return None

def nhaccuatui(message, bot):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "🚫 Vui lòng nhập tên bài hát muốn tìm kiếm.\nVí dụ: /nhaccuatui Tên bài hát", parse_mode='HTML')
        return
    keyword = args[1].strip()
    results = search_nhaccuatui(keyword)
    if not results:
        bot.reply_to(message, f"🚫 Không tìm thấy bài hát nào với từ khóa: {keyword}", parse_mode='HTML')
        return
    songs = results[:10]
    text = "<b>🎵 Kết quả tìm kiếm trên Nhaccuatui</b>\n\n"
    for i, song in enumerate(songs, 1):
        text += f"<b>{i}. {song['title']}</b>\n"
        text += f"👤 Nghệ sĩ: {song['artistsNames']}\n"
        text += f"🆔 ID: {song['id']}\n\n"
    text += "<b>💡 Trả lời tin nhắn này bằng số từ 1-10 để chọn bài hát!</b>"
    sent = bot.reply_to(message, text, parse_mode='HTML')
    nhaccuatui_data[sent.message_id] = {
        "user_id": message.from_user.id,
        "songs": songs
    }

def init(bot):
    @bot.message_handler(func=lambda msg: msg.reply_to_message and msg.reply_to_message.message_id in nhaccuatui_data)
    def handle_nhaccuatui_selection(msg):
        reply_id = msg.reply_to_message.message_id
        if reply_id not in nhaccuatui_data:
            return
        user_id = msg.from_user.id
        data = nhaccuatui_data[reply_id]
        if user_id != data['user_id']:
            return
        text = msg.text.strip()
        if not text.isdigit():
            bot.reply_to(msg, "🚫 Vui lòng chỉ nhập số từ 1-10.", parse_mode='HTML')
            return
        index = int(text) - 1
        if index < 0 or index >= len(data["songs"]):
            bot.reply_to(msg, "🚫 Số không hợp lệ. Hãy nhập số từ 1-10.", parse_mode='HTML')
            return
        song = data["songs"][index]
        bot.delete_message(msg.chat.id, reply_id)
        bot.reply_to(msg, f"🧭 Đang tải: {song['title']} - {song['artistsNames']}", parse_mode='HTML')
        stream_url = get_nct_stream_url(song["id"], song["songLink"])
        if not stream_url:
            bot.reply_to(msg, "🚫 Không thể tải bài hát này.", parse_mode='HTML')
            return
        thumbnail_url = song.get("thumbnail")
        caption = f"<b>🎵 {song['title']}</b>\n"
        caption += f"👤 Nghệ sĩ: {song['artistsNames']}\n"
        caption += f"🎧 Nguồn: Nhaccuatui\n"
        caption += f"🎉 Chúc bạn thưởng thức âm nhạc vui vẻ!"
        try:
            bot.send_photo(msg.chat.id, thumbnail_url, caption=caption, parse_mode='HTML')
        except:
            bot.reply_to(msg, caption + "\n🚫 Không thể tải thumbnail.", parse_mode='HTML')
        bot.send_audio(msg.chat.id, stream_url, title=song["title"], performer=song["artistsNames"])
        del nhaccuatui_data[reply_id]