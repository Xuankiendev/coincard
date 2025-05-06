import subprocess
import os

def getvoice(message, bot):
    if not message.reply_to_message or not message.reply_to_message.video:
        bot.reply_to(message, "<blockquote>Vui lòng reply vào một video để trích xuất audio</blockquote>", parse_mode='HTML')
        return

    video_file = message.reply_to_message.video
    file_path = f"temp_video_{video_file.file_id}.mp4"
    audio_path = f"temp_audio_{video_file.file_id}.mp3"
    thumb_path = f"temp_thumb_{video_file.file_id}.jpg"
    username = message.from_user.username or message.from_user.first_name

    try:
        file_info = bot.get_file(video_file.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        ffmpeg_thumb_command = [
            "ffmpeg", "-i", file_path,
            "-ss", "00:00:01",
            "-vframes", "1",
            thumb_path
        ]
        subprocess.run(ffmpeg_thumb_command, capture_output=True, text=True)

        ffmpeg_audio_command = [
            "ffmpeg", "-i", file_path,
            "-vn", "-acodec", "mp3",
            "-ab", "192k", audio_path
        ]
        result = subprocess.run(ffmpeg_audio_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")

        with open(audio_path, 'rb') as audio, open(thumb_path, 'rb') as thumb:
            bot.send_audio(
                chat_id=message.chat.id,
                audio=audio,
                title="Extracted Audio",
                performer=f"@{username}",
                thumb=thumb,
                reply_to_message_id=message.message_id
            )

    except Exception as e:
        bot.reply_to(message, f"<blockquote>Lỗi khi trích xuất âm thanh: {str(e)}</blockquote>", parse_mode='HTML')

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
