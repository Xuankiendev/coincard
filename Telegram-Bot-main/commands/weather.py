import requests
from datetime import datetime
import random

TOMORROW_API_KEY = "mdTWQAInBIDB3mHiDtkwuTlwhVB50rqn"
OPENWEATHER_API_KEY = "e707d13f116e5f7ac80bd21c37883e5e"
WEATHERAPI_KEY = "fe221e3a25734f0297994922240611"

def get_uv_level(index):
    if index <= 2: return "Thấp"
    if index <= 5: return "Trung bình"
    if index <= 7: return "Cao"
    if index <= 10: return "Rất cao"
    return "Nguy hiểm"

def get_wind_direction(degrees):
    directions = ["Bắc", "Đông Bắc", "Đông", "Đông Nam", "Nam", "Tây Nam", "Tây", "Tây Bắc"]
    index = round(degrees / 45) % 8
    return directions[index]

def get_precipitation_forecast(hourly_data):
    if not isinstance(hourly_data, list): return "Không có dữ liệu dự báo mưa"
    next_24_hours = hourly_data[:24]
    rain_hour = next((hour for hour in next_24_hours if hour.get("values", {}).get("precipitationProbability", 0) > 50), None)
    if not rain_hour:
        light_rain_hour = next((hour for hour in next_24_hours if hour.get("values", {}).get("precipitationProbability", 0) > 30), None)
        if light_rain_hour: return "Có thể có mưa nhỏ trong 24 giờ tới"
        return "Dự kiến không có mưa trong 24 giờ tới"
    try:
        time = datetime.fromisoformat(rain_hour["time"].replace("Z", "+00:00"))
        hour = time.hour
        day_names = ["Chủ Nhật", "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"]
        day_name = day_names[time.weekday()]
        time_of_day = "sáng" if 5 <= hour < 12 else "chiều" if 12 <= hour < 18 else "tối" if 18 <= hour < 22 else "đêm"
        probability = rain_hour["values"]["precipitationProbability"]
        intensity = get_rain_intensity(rain_hour["values"].get("rainIntensity", 0))
        return f"Dự báo {intensity} vào {time_of_day} {day_name} ({probability}% khả năng)"
    except:
        return "Không thể dự đoán chính xác thời gian mưa"

def get_rain_intensity(intensity):
    if intensity == 0: return "không mưa"
    if intensity < 2.5: return "mưa nhỏ"
    if intensity < 7.6: return "mưa vừa"
    if intensity < 15.2: return "mưa to"
    if intensity < 30.4: return "mưa rất to"
    return "mưa đặc biệt to"

def get_weather_description(code):
    weather_codes = {
        1000: "Quang đãng",
        1100: "Có mây nhẹ",
        1101: "Có mây",
        1102: "Nhiều mây",
        1001: "Âm u",
        2000: "Sương mù",
        2100: "Sương mù nhẹ",
        4000: "Mưa nhỏ",
        4001: "Mưa",
        4200: "Mưa nhẹ",
        4201: "Mưa vừa",
        4202: "Mưa to",
        5000: "Tuyết",
        5001: "Tuyết rơi nhẹ",
        5100: "Mưa tuyết nhẹ",
        6000: "Mưa đá",
        6200: "Mưa đá nhẹ",
        6201: "Mưa đá nặng",
        7000: "Sấm sét",
        7101: "Sấm sét mạnh",
        7102: "Giông bão",
        8000: "Một vài cơn mưa rào"
    }
    return weather_codes.get(code, "Không rõ")

def weather(message, bot):
    args = message.text.split(' ', 1)
    location = args[1].strip() if len(args) > 1 else ""
    if not location:
        major_cities = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Huế"]
        location = random.choice(major_cities)
        is_overall = True
    else:
        is_overall = False
    try:
        geo_response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=vi&format=json")
        geo_data = geo_response.json()
        if not geo_data.get("results"):
            bot.reply_to(message, "<blockquote>Không tìm thấy địa điểm này.</blockquote>", parse_mode='HTML')
            return
        geo = geo_data["results"][0]
        lat, lon = geo["latitude"], geo["longitude"]
        name, admin1, country = geo["name"], geo.get("admin1", ""), geo.get("country", "")
        tomorrow_response = requests.get(f"https://api.tomorrow.io/v4/weather/forecast?location={lat},{lon}&apikey={TOMORROW_API_KEY}")
        openweather_response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=vi")
        weatherapi_response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key={WEATHERAPI_KEY}&q={lat},{lon}&days=3&aqi=yes&lang=vi")
        tomorrow_data = tomorrow_response.json()
        openweather_data = openweather_response.json()
        weatherapi_data = weatherapi_response.json()
        daily = tomorrow_data["timelines"]["daily"][0]["values"]
        current = openweather_data
        forecast = weatherapi_data["forecast"]["forecastday"]
        uv_index = weatherapi_data["current"]["uv"]
        uv_level = get_uv_level(uv_index)
        current_weather = current["weather"][0]
        current_temp = current["main"]
        current_wind = current["wind"]
        current_rain = current.get("rain", {}).get("1h", 0)
        tomorrow_weather_code = daily.get("weatherCodeMax") or daily.get("weatherCodeMin")
        weather_desc = get_weather_description(tomorrow_weather_code)
        weather_info = f"[ THÔNG BÁO THỜI TIẾT ]\n" + \
                       f"📍 {name}{', ' + admin1 if admin1 else ''}{', ' + country if country else ''}{' (Tổng Quan)' if is_overall else ''}\n" + \
                       f"⏰ Cập nhật: {datetime.fromtimestamp(current['dt']).strftime('%H:%M %d/%m/%Y')}\n\n" + \
                       f"🌡️ NHIỆT ĐỘ VÀ ĐỘ ẨM\n" + \
                       f"• Hiện tại: {current_temp['temp']}°C (Cảm giác: {current_temp['feels_like']}°C)\n" + \
                       f"• Thấp nhất: {current_temp['temp_min']}°C\n" + \
                       f"• Cao nhất: {current_temp['temp_max']}°C\n" + \
                       f"• Độ ẩm: {current_temp['humidity']}%\n\n" + \
                       f"🌤️ ĐIỀU KIỆN THỜI TIẾT\n" + \
                       f"• Hiện tại: {current_weather['description'].capitalize()}\n" + \
                       f"• Dự báo: {weather_desc}\n" + \
                       f"• Mây che phủ: {current['clouds']['all']}%\n" + \
                       f"• Tầm nhìn: {(current['visibility'] / 1000):.1f}km\n\n" + \
                       f"🌧️ LƯỢNG MƯA VÀ KHẢ NĂNG MƯA\n" + \
                       f"• Lượng mưa (1h qua): {current_rain}mm\n" + \
                       f"• {get_precipitation_forecast(tomorrow_data['timelines']['hourly'])}\n\n" + \
                       f"💨 GIÓ\n" + \
                       f"• Tốc độ: {current_wind['speed']} m/s\n" + \
                       f"• Hướng: {get_wind_direction(current_wind['deg'])}\n" + \
                       f"• Gió giật: {current_wind.get('gust', 0)} m/s\n\n" + \
                       f"☀️ CHỈ SỐ UV\n" + \
                       f"• UV: {uv_index} ({uv_level})"
        bot.reply_to(message, weather_info, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"<blockquote>Đã xảy ra lỗi: {str(e)}</blockquote>", parse_mode='HTML')
