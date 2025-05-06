import os
import subprocess
import json

processes = []

def spamsms(message, bot):
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, '<blockquote>Vui lòng nhập số điện thoại và số lần sau lệnh /spamsms (Ví dụ: /spamsms 0123456789 100)</blockquote>', parse_mode='HTML')
        return
    phone_number = args[1]
    count = args[2]
    spam_files = [
        "data-apispamsms/1.py",
        "data-apispamsms/2.py",
        "data-apispamsms/3.py",
        "data-apispamsms/4.py",
        "data-apispamsms/5.py",
        "data-apispamsms/6.py",
        "data-apispamsms/7.py",
        "data-apispamsms/8.py",
        "data-apispamsms/9.py",
        "data-apispamsms/10.py",
        "data-apispamsms/11.py",
        "data-apispamsms/12.py",
        "data-apispamsms/13.py",
        "data-apispamsms/14.py",
        "data-apispamsms/15.py"
    ]
    for spam_file in spam_files:
        file_path = os.path.join(os.getcwd(), spam_file)
        process = subprocess.Popen(["python", file_path, phone_number, count])
        processes.append(process)
    bot.reply_to(message, f'''<blockquote>Đang tiến hành Spam SMS, số điện thoại: {phone_number}, số lần: {count}
Dùng lệnh: /stopsms để dừng Spam (Admin Only)!</blockquote>''', parse_mode='HTML')

def init(bot):
    pass