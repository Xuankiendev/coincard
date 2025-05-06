import os
import subprocess
import io
import sys
import re

def shell(message, bot):
    command = message.text[len(f"/shell "):].strip()

    if not command:
        bot.reply_to(message, "Vui lòng cung cấp mã hoặc lệnh để chạy.")
        return

    if command.startswith("pip uninstall"):
        command += " -y"

    if command.startswith(("pip", "python", "node", "npm", "sudo", "ls", "cd")):
        try:
            result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = result.communicate()

            if result.returncode == 0:
                response_message = stdout or "Done!"
            else:
                response_message = stderr or "Lỗi không xác định."
        except Exception as e:
            response_message = f"Có lỗi xảy ra: {str(e)}"
    else:
        try:
            output_buffer = io.StringIO()
            sys.stdout = output_buffer

            compiled_code = compile(command, '<string>', 'exec')
            local_vars = {}
            exec(compiled_code, {}, local_vars)

            sys.stdout = sys.__stdout__

            output = output_buffer.getvalue()
            output_buffer.close()

            if output:
                response_message = f"{output}"
            elif local_vars:
                output = "\n".join(f"{k}: {v}" for k, v in local_vars.items())
                response_message = f"{output}"
            else:
                response_message = "Done!"
        except NameError as e:
            response_message = f"NameError: {str(e)}\nInput code: {repr(command)}"
        except SyntaxError as e:
            response_message = f"SyntaxError: {str(e)}\nInput code: {repr(command)}"
        except Exception as e:
            response_message = f"Error: {str(e)}\nInput code: {repr(command)}"
        finally:
            sys.stdout = sys.__stdout__

    bot.reply_to(message, response_message)