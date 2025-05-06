import os
import requests

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_resources(url, path):
    ensure_dir(os.path.dirname(path))
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def downloadresources(message, bot):
    resource_dir = 'assets/resources'

    def get_resource_list():
        files = []
        if os.path.exists(resource_dir):
            for root, _, filenames in os.walk(resource_dir):
                for filename in filenames:
                    files.append(os.path.relpath(os.path.join(root, filename), resource_dir))
        return files

    args = message.text.split(maxsplit=1)[1:] if len(message.text.split()) > 1 else []

    if message.reply_to_message:
        if not args:
            bot.reply_to(message, "Vui lòng cung cấp tên file, ví dụ: /downloadresources filename.jpg")
            return

        filename_path = args[0].split('|', 1)
        filename = filename_path[0].strip()
        custom_path = filename_path[1].strip() if len(filename_path) > 1 else 'assets/resources'

        file_info = None
        file_url = None
        file_ext = os.path.splitext(filename)[1].lower() or '.jpg'

        if message.reply_to_message.photo:
            file_info = bot.get_file(message.reply_to_message.photo[-1].file_id)
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        elif message.reply_to_message.video:
            file_info = bot.get_file(message.reply_to_message.video.file_id)
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{erealized_file_path}"
            file_ext = '.mp4'
        elif message.reply_to_message.audio:
            file_info = bot.get_file(message.reply_to_message.audio.file_id)
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
            file_ext = '.mp3'
        elif message.reply_to_message.document:
            file_info = bot.get_file(message.reply_to_message.document.file_id)
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
            file_ext = os.path.splitext(message.reply_to_message.document.file_name)[1] or '.file'
        elif message.reply_to_message.voice:
            file_info = bot.get_file(message.reply_to_message.voice.file_id)
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
            file_ext = '.ogg'

        if file_url:
            save_path = os.path.join(custom_path, filename if filename.endswith(file_ext) else filename + file_ext)
            try:
                download_resources(file_url, save_path)
                bot.reply_to(message, f"Đã lưu file tại: {save_path}")
            except Exception as e:
                bot.reply_to(message, f"Lỗi khi lưu file: {str(e)}")
        else:
            bot.reply_to(message, "Không hỗ trợ download loại file này.")

    else:
        if args and args[0].lower().startswith('remove'):
            remove_args = args[0].split(maxsplit=1)
            if len(remove_args) < 2:
                bot.reply_to(message, "Vui lòng cung cấp tên file để xóa, ví dụ: /downloadresources remove filename.jpg")
                return

            filename = remove_args[1].strip()
            file_path = None
            similar_files = []

            for root, _, filenames in os.walk(resource_dir):
                for fname in filenames:
                    if fname == filename:
                        file_path = os.path.join(root, fname)
                        break
                    if filename.lower() in fname.lower():
                        similar_files.append(os.path.relpath(os.path.join(root, fname), resource_dir))

            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    bot.reply_to(message, f"Đã xóa file: {filename}")
                except Exception as e:
                    bot.reply_to(message, f"Lỗi khi xóa file: {str(e)}")
            else:
                if similar_files:
                    bot.reply_to(message, f"Không tìm thấy file: {filename}, các file có tên giống:\n" + "\n".join(similar_files))
                else:
                    bot.reply_to(message, f"Không tìm thấy file: {filename}")

        elif args:
            filename = args[0].strip()
            file_path = None
            similar_files = []

            for root, _, filenames in os.walk(resource_dir):
                for fname in filenames:
                    if fname == filename:
                        file_path = os.path.join(root, fname)
                        break
                    if filename.lower() in fname.lower():
                        similar_files.append(os.path.relpath(os.path.join(root, fname), resource_dir))

            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        if file_path.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                            bot.send_photo(message.chat.id, f, reply_to_message_id=message.message_id)
                        elif file_path.endswith(('.mp4', '.mkv', '.avi')):
                            bot.send_video(message.chat.id, f, reply_to_message_id=message.message_id)
                        elif file_path.endswith(('.mp3', '.ogg', '.wav')):
                            bot.send_audio(message.chat.id, f, reply_to_message_id=message.message_id)
                        else:
                            bot.send_document(message.chat.id, f, reply_to_message_id=message.message_id)
                except Exception as e:
                    bot.reply_to(message, f"Lỗi khi gửi file: {str(e)}")
            else:
                if similar_files:
                    bot.reply_to(message, f"Không tìm thấy file: {filename}, các file có tên giống:\n" + "\n".join(similar_files))
                else:
                    bot.reply_to(message, f"Không tìm thấy file: {filename}")

        else:
            files = get_resource_list()
            if files:
                bot.reply_to(message, "Danh sách resources:\n" + "\n".join(files))
            else:
                bot.reply_to(message, "Dùng lệnh: /downloadresources và reply ảnh với tên ảnh cần lưu để download resources.")