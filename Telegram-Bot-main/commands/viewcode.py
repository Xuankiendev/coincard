import os
from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup

def read_command_content(command_name):
    try:
        file_path = f"commands/{command_name}.py"
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return str(e)

def highlight_code(code):
    formatter = HtmlFormatter()
    highlighted_code = highlight(code, PythonLexer(), formatter)
    soup = BeautifulSoup(highlighted_code, "html.parser")
    return soup

def get_color_for_token_type(span):
    color_map = {
        'k': (189, 147, 249),
        'kn': (189, 147, 249),
        'kd': (189, 147, 249),
        'kp': (189, 147, 249),
        'kt': (189, 147, 249),
        'kc': (189, 147, 249),
        'n': (248, 248, 242),
        'nn': (248, 248, 242),
        'na': (139, 233, 253),
        'nb': (139, 233, 253),
        'nc': (80, 250, 123),
        'no': (255, 184, 108),
        'nd': (248, 248, 242),
        'ni': (248, 248, 242),
        'ne': (248, 248, 242),
        'nf': (80, 250, 123),
        'nl': (248, 248, 242),
        'nv': (139, 233, 253),
        's': (255, 121, 198),
        'sa': (255, 121, 198),
        'sb': (255, 121, 198),
        'sc': (255, 121, 198),
        'sd': (98, 114, 164),
        's2': (255, 121, 198),
        'se': (255, 121, 198),
        'sh': (255, 121, 198),
        'si': (255, 121, 198),
        'sx': (255, 121, 198),
        'sr': (255, 121, 198),
        's1': (255, 121, 198),
        'ss': (255, 121, 198),
        'c': (98, 114, 164),
        'ch': (98, 114, 164),
        'cm': (98, 114, 164),
        'c1': (98, 114, 164),
        'o': (248, 248, 242),
        'ow': (248, 248, 242),
        'p': (248, 248, 242),
        'm': (255, 184, 108),
        'mb': (255, 184, 108),
        'mf': (255, 184, 108),
        'mh': (255, 184, 108),
        'mi': (255, 184, 108),
        'il': (255, 184, 108),
        'gh': (248, 248, 242),
        'gi': (248, 248, 242),
        'gd': (248, 248, 242),
        'gp': (248, 248, 242),
        'gt': (248, 248, 242),
        'err': (255, 85, 85),
        'w': (248, 248, 242),
        'bp': (248, 248, 242)
    }
    if 'class' in span.attrs:
        token_type = span['class'][0]
        short_type = token_type.split('.')[0][1:] if '.' in token_type else token_type[:2]
        return color_map.get(short_type, (248, 248, 242))
    return (248, 248, 242)

def split_code_lines(code_lines):
    if len(code_lines) <= 100:
        return [code_lines]
    return [code_lines[i:i + 100] for i in range(0, len(code_lines), 100)]

def create_image_from_code(code, command_name, font_path="assets/font/BeVietnamPro-Bold.ttf"):
    fontcre = "assets/font/UTM-AvoBold.ttf"
    fontlenh = "assets/font/BeVietnamPro-Bold.ttf"
    highlighted_soup = highlight_code(code)
    code_lines = code.splitlines()
    line_height = 40
    line_offset = 50
    bottom_offset = 50
    temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    temp_font = ImageFont.truetype(font_path, 30)
    max_width = max(temp_draw.textlength(line, font=temp_font) for line in code_lines) + 100
    img_width = min(max(800, max_width), 2000)
    img_width = int(img_width)
    available_code_width = img_width - 80
    background_color = (30, 30, 46)
    header_color = (48, 48, 52)
    image_paths = []
    line_groups = split_code_lines(code_lines)
    total_visual_lines = 0
    for line in code_lines:
        line_width = temp_draw.textlength(line, font=temp_font)
        total_visual_lines += max(1, int(line_width // available_code_width) + 1)
    for group_index, line_group in enumerate(line_groups):
        header_height = 70
        group_visual_lines = 0
        for line in line_group:
            line_width = temp_draw.textlength(line, font=temp_font)
            group_visual_lines += max(1, int(line_width // available_code_width) + 1)
        img_height = int(header_height + line_offset + group_visual_lines * line_height + bottom_offset + 20)
        scale_factor = 2
        temp_width = img_width * scale_factor
        temp_height = img_height * scale_factor
        background = Image.new('RGBA', (temp_width, temp_height), background_color)
        draw = ImageDraw.Draw(background)
        draw.rectangle([(0, 0), (temp_width, header_height * scale_factor)], fill=header_color)
        header_font = ImageFont.truetype(font_path, 38 * scale_factor)
        mitai_text = "V X K I T V N"
        mitai_text_width = temp_draw.textlength(mitai_text, font=header_font)
        mitai_text_x = (temp_width - mitai_text_width) // 2 + 10 * scale_factor
        mitai_text_bbox = draw.textbbox((0, 0), mitai_text, font=header_font)
        mitai_text_height = mitai_text_bbox[3] - mitai_text_bbox[0]
        mitai_text_y = (header_height * scale_factor - mitai_text_height) // 2
        draw.text((mitai_text_x, mitai_text_y), mitai_text, font=header_font, fill=(120, 120, 120))
        dot_radius_outer = 14 * scale_factor
        dot_radius_inner = 10 * scale_factor
        dot_spacing = 25 * scale_factor
        dots_x_start = 40 * scale_factor
        dot_positions = [
            (dots_x_start, 35 * scale_factor),
            (dots_x_start + 2 * dot_radius_outer + dot_spacing, 35 * scale_factor),
            (dots_x_start + 4 * dot_radius_outer + 2 * dot_spacing, 35 * scale_factor)
        ]
        dot_colors = [(255, 69, 58), (40, 215, 75), (255, 200, 10)]
        inner_dot_color = header_color
        for pos, border_color in zip(dot_positions, dot_colors):
            draw.ellipse([pos[0] - dot_radius_outer, pos[1] - dot_radius_outer,
                          pos[0] + dot_radius_outer, pos[1] + dot_radius_outer], fill=border_color)
            draw.ellipse([pos[0] - dot_radius_inner, pos[1] - dot_radius_inner,
                          pos[0] + dot_radius_inner, pos[1] + dot_radius_inner], fill=inner_dot_color)
        command_font = ImageFont.truetype(fontlenh, 28 * scale_factor)
        command_text = f"{command_name}.py" if group_index == 0 else f"{command_name}-page-{group_index+1}.py"
        command_text_width = temp_draw.textlength(command_text, font=command_font)
        python_logo_width = 36 * scale_factor
        tab_padding = 25 * scale_factor
        tab_width = int(command_text_width + python_logo_width + tab_padding * 3)
        tab_height = 60 * scale_factor
        tab_color = background_color
        corner_radius = 18 * scale_factor
        tab_x = dots_x_start + 4 * dot_radius_outer + 2 * dot_spacing + 50 * scale_factor
        tab_y = mitai_text_y + (mitai_text_height - tab_height) // 2
        draw.rounded_rectangle([(tab_x, tab_y), (tab_x + tab_width, tab_y + tab_height)], radius=corner_radius, fill=tab_color)
        python_logo_path = "assets/cache/python-logo.jpg"
        if os.path.exists(python_logo_path):
            python_logo = Image.open(python_logo_path).convert("RGBA")
            python_logo = python_logo.resize((36 * scale_factor, 36 * scale_factor), Image.Resampling.LANCZOS)
            logo_x = tab_x + (tab_width - (python_logo_width + command_text_width + tab_padding)) // 2
            logo_y = tab_y + (tab_height - 36 * scale_factor) // 2 - 2 * scale_factor
            background.paste(python_logo, (int(logo_x), logo_y), python_logo.split()[3])
        text_x = logo_x + python_logo_width + tab_padding
        text_y = tab_y + (tab_height - 28 * scale_factor) // 2 - 5 * scale_factor
        draw.text((text_x, text_y), command_text, font=command_font, fill=(255, 255, 255))
        background = background.resize((img_width, img_height), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(background)
        code_area_height = img_height - header_height - bottom_offset
        code_content_height = group_visual_lines * line_height
        y_offset = header_height + (code_area_height - code_content_height) // 2 + 24
        code_font = ImageFont.truetype(font_path, 28)
        line_font = ImageFont.truetype(font_path, 28)
        start_line = group_index * 50 + 1
        for i, line in enumerate(line_group):
            line_number = f"{start_line + i:2}"
            draw.text((10, y_offset), line_number, font=line_font, fill=(100, 100, 100))
            highlighted_line = highlight(line, PythonLexer(), HtmlFormatter())
            soup_line = BeautifulSoup(highlighted_line, 'html.parser')
            line_width = temp_draw.textlength(line, font=code_font)
            if line_width <= available_code_width:
                leading_spaces = len(line) - len(line.lstrip(' '))
                x_offset = 80 + leading_spaces * draw.textlength(' ', font=code_font)
                spans = soup_line.find_all('span')
                last_end_index = 0
                for span in spans:
                    token_text = span.get_text()
                    token_color = get_color_for_token_type(span)
                    start_index = line.find(token_text, last_end_index)
                    if start_index > last_end_index:
                        space_text = line[last_end_index:start_index]
                        draw.text((x_offset, y_offset), space_text, font=code_font, fill=(248, 248, 242))
                        x_offset += draw.textlength(space_text, font=code_font)
                    draw.text((x_offset, y_offset), token_text, font=code_font, fill=token_color)
                    x_offset += draw.textlength(token_text, font=code_font)
                    last_end_index = start_index + len(token_text)
                if last_end_index < len(line):
                    remaining_space = line[last_end_index:]
                    draw.text((x_offset, y_offset), remaining_space, font=code_font, fill=(248, 248, 242))
                y_offset += line_height
            else:
                remaining_line = line
                leading_spaces = len(line) - len(line.lstrip(' '))
                x_offset_start = 80 + leading_spaces * draw.textlength(' ', font=code_font)
                while remaining_line:
                    current_width = 0
                    split_index = 0
                    for j, char in enumerate(remaining_line):
                        char_width = draw.textlength(char, font=code_font)
                        if current_width + char_width > available_code_width - x_offset_start:
                            break
                        current_width += char_width
                        split_index = j + 1
                    if split_index == 0:
                        split_index = len(remaining_line)
                    current_part = remaining_line[:split_index]
                    remaining_line = remaining_line[split_index:]
                    if current_part:
                        x_offset = x_offset_start
                        if x_offset == x_offset_start and current_part.startswith(' ' * leading_spaces):
                            current_part = current_part[leading_spaces:]
                            x_offset = 80 + leading_spaces * draw.textlength(' ', font=code_font)
                        highlighted_part = highlight(current_part, PythonLexer(), HtmlFormatter())
                        soup_part = BeautifulSoup(highlighted_part, 'html.parser')
                        spans = soup_part.find_all('span')
                        last_end_index = 0
                        for span in spans:
                            token_text = span.get_text()
                            token_color = get_color_for_token_type(span)
                            start_index = current_part.find(token_text, last_end_index)
                            if start_index > last_end_index:
                                space_text = current_part[last_end_index:start_index]
                                draw.text((x_offset, y_offset), space_text, font=code_font, fill=(248, 248, 242))
                                x_offset += draw.textlength(space_text, font=code_font)
                            draw.text((x_offset, y_offset), token_text, font=code_font, fill=token_color)
                            x_offset += draw.textlength(token_text, font=code_font)
                            last_end_index = start_index + len(token_text)
                        if last_end_index < len(current_part):
                            remaining_space = current_part[last_end_index:]
                            draw.text((x_offset, y_offset), remaining_space, font=code_font, fill=(248, 248, 242))
                    y_offset += line_height
                    if remaining_line:
                        draw.text((80, y_offset), "-> ", font=code_font, fill=(100, 100, 100))
                        x_offset_start = 80 + draw.textlength("-> ", font=code_font)
        image_path = f"assets/cache/{command_name}_{group_index}.png"
        background.save(image_path, quality=125)
        image_paths.append((image_path, background.width, background.height))
    return image_paths

def viewcode(message, bot):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Nhập tên lệnh cần xem code.")
        return
    command_name = args[1].strip()
    command_content = read_command_content(command_name)
    if command_content is None:
        bot.reply_to(message, f"Không tìm thấy lệnh '{command_name}' trong thư mục commands.")
        return
    try:
        image_paths = create_image_from_code(command_content, command_name)
        for image_path, _, _ in image_paths:
            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, reply_to_message_id=message.message_id)
            os.remove(image_path)
    except Exception as e:
        bot.reply_to(message, f"Có lỗi xảy ra: {str(e)}")