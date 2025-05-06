from urllib.parse import quote
import requests

bank_codes = {
    "vcb": {"bin": "970436", "name": "VIETCOMBANK"},
    "vietcombank": {"bin": "970436", "name": "VIETCOMBANK"},
    "tcb": {"bin": "970407", "name": "TECHCOMBANK"},
    "techcombank": {"bin": "970407", "name": "TECHCOMBANK"},
    "mb": {"bin": "970422", "name": "MB BANK"},
    "mbbank": {"bin": "970422", "name": "MB BANK"},
    "mb bank": {"bin": "970422", "name": "MB BANK"},
    "acb": {"bin": "970416", "name": "ACB"},
    "vib": {"bin": "970441", "name": "VIB"},
    "bidv": {"bin": "970418", "name": "BIDV"},
    "vietinbank": {"bin": "970415", "name": "VIETINBANK"},
    "vtb": {"bin": "970415", "name": "VIETINBANK"},
    "tpbank": {"bin": "970423", "name": "TPBANK"},
    "vpbank": {"bin": "970432", "name": "VPBANK"},
    "agribank": {"bin": "970405", "name": "AGRIBANK"},
    "sacombank": {"bin": "970403", "name": "SACOMBANK"},
    "scb": {"bin": "970429", "name": "SCB"},
    "hdbank": {"bin": "970437", "name": "HDBANK"},
    "ocb": {"bin": "970448", "name": "OCB"},
    "msb": {"bin": "970426", "name": "MSB"},
    "maritimebank": {"bin": "970426", "name": "MSB"},
    "shb": {"bin": "970443", "name": "SHB"},
    "eximbank": {"bin": "970431", "name": "EXIMBANK"},
    "exim": {"bin": "970431", "name": "EXIMBANK"},
    "dongabank": {"bin": "970406", "name": "DONGABANK"},
    "dab": {"bin": "970406", "name": "DONGABANK"},
    "pvcombank": {"bin": "970412", "name": "PVCOMBANK"},
    "gpbank": {"bin": "970408", "name": "GPBANK"},
    "oceanbank": {"bin": "970414", "name": "OCEANBANK"},
    "namabank": {"bin": "970428", "name": "NAMABANK"},
    "ncb": {"bin": "970419", "name": "NCB"},
    "vietabank": {"bin": "970427", "name": "VIETABANK"},
    "vietbank": {"bin": "970433", "name": "VIETBANK"},
    "vrb": {"bin": "970421", "name": "VRB"},
    "wooribank": {"bin": "970457", "name": "WOORIBANK"},
    "uob": {"bin": "970458", "name": "UOB"},
    "standardchartered": {"bin": "970410", "name": "STANDARD CHARTERED"},
    "publicbank": {"bin": "970439", "name": "PUBLIC BANK"},
    "shinhanbank": {"bin": "970424", "name": "SHINHAN BANK"},
    "hsbc": {"bin": "458761", "name": "HSBC"},
    "coop": {"bin": "970446", "name": "COOPBANK"},
    "coopbank": {"bin": "970446", "name": "COOPBANK"},
    "lienvietpostbank": {"bin": "970449", "name": "LIENVIETPOSTBANK"},
    "lvb": {"bin": "970449", "name": "LIENVIETPOSTBANK"},
    "baovietbank": {"bin": "970438", "name": "BAOVIETBANK"},
    "bvb": {"bin": "970438", "name": "BAOVIETBANK"}
}

qrbank_data = {}

def generate_vietqr_data(bank_bin, account_number, amount=0, account_name="", add_info=""):
    account_name = quote(account_name) if account_name else ""
    add_info = quote(add_info) if add_info else ""
    return f"https://img.vietqr.io/image/{bank_bin}-{account_number}-qr_only.jpg?accountName={account_name}&amount={amount}&addInfo={add_info}"

def get_bank_info(bank_code):
    return bank_codes.get(bank_code.lower())

def is_valid_qr_url(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200 and "image" in response.headers.get("content-type", "")
    except:
        return False

def qrbank(message, bot):
    if message.text != "/qrbank":
        return
    msg = bot.send_message(message.chat.id, "💡 Vui lòng reply tin nhắn này với định dạng:\n[số tài khoản] | [mã ngân hàng] | [số tiền] | [chủ tài khoản] | [nội dung chuyển khoản]", parse_mode='HTML')
    qrbank_data[message.chat.id] = msg.message_id

def init(bot):
    @bot.message_handler(func=lambda m: m.chat.id in qrbank_data)
    def handle_input(msg):
        reply_id = qrbank_data.get(msg.chat.id)
        if not msg.reply_to_message or msg.reply_to_message.message_id != reply_id:
            return
        parts = msg.text.split("|")
        if len(parts) < 2:
            bot.send_message(msg.chat.id, "🚫 Định dạng không hợp lệ! Yêu cầu ít nhất: [chủ tài khoản] | [mã ngân hàng]", parse_mode='HTML')
            return
        account = parts[0].strip()
        bank_code = parts[1].strip()
        amount = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        account_name = parts[3].strip() if len(parts) > 3 else ""
        add_info = parts[4].strip() if len(parts) > 4 else ""
        if not account.isdigit() or len(account) < 6 or len(account) > 20:
            bot.send_message(msg.chat.id, "🚫 Số tài khoản không hợp lệ!", parse_mode='HTML')
            return
        bank_info = get_bank_info(bank_code)
        if not bank_info:
            bot.send_message(msg.chat.id, "🚫 Mã ngân hàng không hợp lệ!", parse_mode='HTML')
            return
        qr_url = generate_vietqr_data(bank_info["bin"], account, amount, account_name, add_info)
        caption = f"<b>✅ Mã QR của bạn!</b>\n🏦 Ngân hàng: {bank_info['name']}\n🆔 Số tài khoản: {account}"
        if amount:
            caption += f"\n💰 Số tiền: {amount}"
        if account_name:
            caption += f"\n👤 Chủ tài khoản: {account_name}"
        if add_info:
            caption += f"\n📝 Nội dung: {add_info}"
        if is_valid_qr_url(qr_url):
            bot.send_photo(msg.chat.id, qr_url, caption=caption, parse_mode='HTML')
        else:
            bot.send_message(msg.chat.id, caption + "\n🚫 Không thể tạo mã QR!", parse_mode='HTML')
        del qrbank_data[msg.chat.id]
