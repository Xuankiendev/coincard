from gtts import gTTS
import os

def convert_text(text):
    try:
        tts = gTTS(text=text, lang='vi')
        aac_file = f'voice.aac'
        tts.save(aac_file)
        return aac_file
    except Exception as e:
        print(f"Lỗi {str(e)}")
        return None

def voice(message, bot):
    text = message.text.split(' ', 1)
    if len(text) < 2:
        bot.reply_to(message, "<blockquote>Vui lòng cung cấp nội dung để tạo voice.\nVí dụ: /voice Nội dung</blockquote>", parse_mode='HTML')
        return
    text = text[1]
    aac_file = convert_text(text)
    if aac_file:
        with open(aac_file, 'rb') as audio:
            bot.send_voice(message.chat.id, audio, reply_to_message_id=message.message_id, caption=f"<blockquote>Thành công.</blockquote>", parse_mode='HTML')
        os.remove(aac_file)