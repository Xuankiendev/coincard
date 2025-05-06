import subprocess
import json
import os

PHATNGUOI_API_KEY = "v2g0Ey8MCFTzuZbQUFgSIXOlsM64B3HKTcX" 

def phatnguoi(message, bot):
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "<blockquote>Vui lòng nhập đủ 3 tham số!</blockquote>", parse_mode='HTML')
        return
    
    bien_so = args[1]
    loai_xe = args[2].upper()
    
    if loai_xe not in ['1', '2']:
        bot.reply_to(message, "<blockquote>Loại xe không hợp lệ! Chọn 1 (ô tô) hoặc 2 (xe máy).</blockquote>", parse_mode='HTML')
        return
    
    try:
        payload = {
            "apikey": PHATNGUOI_API_KEY,
            "bienso": bien_so,
            "loai": loai_xe
        }
        curl_command = [
            "curl", "-X", "POST",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload),
            "https://api.1touch.pro/api/phat-nguoi"
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"curl error: {result.stderr}")
        
        data = json.loads(result.stdout)
        
        if data.get('status') == 'success' and data.get('data'):
            reply = ""
            for violation in data['data']:
                reply += "<b><i>THÔNG TIN PHẠT NGUỘI 🚨</i></b>\n\n" + \
                    f"<b>🏷️ Biển số:</b> {violation.get('bien_kiem_soat', 'N/A')}\n" + \
                    f"<b>🚗 Loại phương tiện:</b> {violation.get('loai_phuong_tien', 'N/A')}\n" + \
                    f"<b>⏰ Thời gian vi phạm:</b> {violation.get('thoi_gian_vi_pham', 'N/A')}\n" + \
                    f"<b>📍 Địa điểm vi phạm:</b> {violation.get('dia_diem_vi_pham', 'N/A')}\n" + \
                    f"<b>🚫 Hành vi vi phạm:</b> {violation.get('hanh_vi_vi_pham', 'N/A')}\n" + \
                    f"<b>ℹ️ Trạng thái:</b> {violation.get('trang_thai', 'N/A')}\n" + \
                    f"<b>👮 Đơn vị phát hiện:</b> {violation.get('don_vi_phat_hien', 'N/A')}\n" + \
                    f"<b>🏢 Địa chỉ liên hệ:</b> {violation.get('dia_chi', 'N/A')}\n" + \
                    f"<b>☎️ Số điện thoại:</b> {violation.get('so_dien_thoai', 'N/A')}\n\n"
            bot.reply_to(message, reply, parse_mode='HTML')
        else:
            bot.reply_to(message, "<blockquote>Không tìm thấy thông tin phạt nguội cho biển số này.</blockquote>", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"<blockquote>Xin lỗi, không thể kiểm tra phạt nguội lúc này: {str(e)}</blockquote>", parse_mode='HTML')