import requests
import json
import telebot
import re

chat_history = {}

def extract_markdown(text):
    text = re.sub(r'([`]{3,})', '```', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'([*]{2,})', '**', text)
    text = re.sub(r'([_]{2,})', '_', text)
    text = re.sub(r'([*])([ \t]*\n)', r'\1\n', text)
    text = re.sub(r'\*\s*\*\*([^\*]+)\*\*\s*:', r'* \1:', text)
    text = re.sub(r'([^\*])\*([^\*])', r'\1 * \2', text)
    text = text.replace('\r\n', '\n')
    return text.strip()

def chat(message, bot):
    args = message.text.split(' ', 1)
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng cung cấp câu hỏi cần giải đáp...❓", parse_mode='Markdown')
        return
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    ask = args[1]
    if chat_id not in chat_history:
        chat_history[chat_id] = []
    chat_history[chat_id].append({"role": "user", "parts": [{"text": f"{full_name} hỏi: {ask}"}]})
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyC5VvVGBk3T0TzfF_JCaDTDPAW97oRhdrc"
    headers = {'Content-Type': 'application/json'}
    prompt = '''Bạn là V X K AI ChatBot, được tạo ra bởi Vũ Xuân Kiên trong team V X K Community Service, Hải Phòng, Việt Nam. Chứ không phải Google.  
Hãy trả lời lịch sự, súc tích, sử dụng kí tự Markdown nhẹ nhàng, phù hợp để hiển thị đẹp trên Telegram mà không lỗi.
Nếu câu hỏi đã chứa định dạng Markdown, giữ nguyên và không thêm định dạng khác.  
Bạn có thể sử dụng emoji để câu trả lời đẹp mắt cùng với Markdown.
Hỗ trợ người dùng hết mình, tránh lỗi kí tự.  
Liên hệ nếu cần trợ giúp, công việc:
Telegram Vux Xuaan Kieen (@xkprj), HotMail: vxkitvn@gmail.com, HotLine: 0345864723.'''
    contents = [{"role": "user", "parts": [{"text": prompt}]}] + chat_history[chat_id]
    data = {"contents": contents}
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            bot.reply_to(message, "Lỗi khi gọi API. Vui lòng thử lại sau.", parse_mode='Markdown')
            return
        response_json = response.json()
        if 'candidates' in response_json and response_json['candidates']:
            answer = response_json['candidates'][0]['content']['parts'][0]['text']
            chat_history[chat_id].append({"role": "model", "parts": [{"text": answer}]})
            response_text = extract_markdown(f"❓ Câu hỏi của {full_name}: {ask}\n\n🤖 Gemini-1.5-Flash-Latest: {answer}")
            try:
                bot.reply_to(message, response_text, parse_mode='Markdown')
            except telebot.apihelper.ApiTelegramException as telegram_error:
                if "can't parse entities" in str(telegram_error):
                    bot.reply_to(message, response_text, parse_mode=None)
                else:
                    raise telegram_error
        else:
            bot.reply_to(message, "Không nhận được câu trả lời hợp lệ từ API.", parse_mode='Markdown')
    except Exception as e:
        print(f"Lỗi chi tiết: {str(e)}")
        print(f"Phản hồi API đầy đủ: {response_json}")
        bot.reply_to(message, "Gemini || Bot bị ngu tạm thời.", parse_mode='Markdown')