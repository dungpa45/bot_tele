import json
import requests
from datetime import datetime, timedelta
from var_file import *

place = "Hanoi"
link = 'http://api.openweathermap.org/data/2.5/weather?q={}&lang=vi&appid={}'.format(place,API_WEATHER)
try:
    contents = requests.get(link)
    contents.raise_for_status()
except Exception as e:
    contents = None
    print(f"Error fetching OpenWeather data: {e}")

link_air = "http://api.airvisual.com/v2/city?city=Hanoi&state=Hanoi&country=Vietnam&key={}".format(API_AIRVISUAL)
try:
    content_air_res = requests.get(link_air)
    content_air_res.raise_for_status()
    content_air = content_air_res.json()
except Exception as e:
    content_air = None
    print(f"Error fetching AirVisual data: {e}")

def getEmoji(weatherID):
    if weatherID:
        if str(weatherID)[0] == '2' or weatherID == 900 or weatherID==901 or weatherID==902 or weatherID==905:
            return thunderstorm
        elif str(weatherID)[0] == '3':
            return drizzle
        elif str(weatherID)[0] == '5':
            return rain
        elif str(weatherID)[0] == '6' or weatherID==903 or weatherID== 906:
            return snowflake + ' ' + snowman
        elif str(weatherID)[0] == '7':
            return atmosphere
        elif weatherID == 800:
            return clearSky
        elif weatherID == 801:
            return fewClouds
        elif weatherID==802 or weatherID==803 or weatherID==804:
            return clouds
        elif weatherID == 904:
            return hot
        else:
            return defaultEmoji

def process_message(input):
    try:
        # Loading JSON into a string
        raw_json = json.loads(input)
        # Outputing as JSON with indents
        output = json.dumps(raw_json, indent=4)
    except:
        output = input
    return output

def temp_K_to_C(temp):
    return int(temp - 273.15)

def unix_time_to_UTC(time):
    # t = datetime.fromtimestamp(time)
    t = datetime.fromtimestamp(time) + timedelta(hours=7)
    return t.strftime('%H:%M:%S')

def data_openweather(content):
    if content is None:
        return "❌ Không thể lấy dữ liệu thời tiết lúc này."
    try:
        data = content.json()
        weather_id = data["weather"][0]["id"]
        emoji = getEmoji(weather_id)
        weather = data["weather"][0]["main"]
        weather_des = data["weather"][0]["description"]
        main = data["main"]
        temp = temp_K_to_C(main['temp'])
        feels = temp_K_to_C(main["feels_like"])
        temp_min = temp_K_to_C(main["temp_min"])
        tepm_max = temp_K_to_C(main["temp_max"])
        humidity = main["humidity"]
        wind = data["wind"]
        sunrise = unix_time_to_UTC(data["sys"]["sunrise"])
        sunset = unix_time_to_UTC(data["sys"]["sunset"])
        print(content.json())

        tmp = "Thời tiết hôm nay"+ \
            "\n"+ emoji + emoji + emoji +\
            "\nNhiệt độ: *"+str(temp)+degree_sign+"*"\
            "\nCao nhất: "+str(temp_min)+degree_sign+" - Thấp nhất: "+str(tepm_max)+degree_sign+\
            "\nCảm giác như: "+str(feels)+degree_sign+\
            "\nĐộ ẩm: "+str(humidity)+"%"+\
            "\nThời tiết: " +weather_des +\
            "\nMặt trời: "+str(sunrise)+" - "+str(sunset)
        return tmp
    except Exception as e:
        print(f"Error processing OpenWeather data: {e}")
        return "❌ Lỗi khi xử lý dữ liệu thời tiết."

def data_air(content):
    if content is None:
        return "\n❌ Không thể lấy dữ liệu ô nhiễm AQI."
    try:
        data = content['data']
        print(data)
        AQI = data["current"]["pollution"]["aqius"]
        if AQI in range(0, 51):
            mucdo = "Tốt. "+starFace+"\nBạn nên để không khí trong nhà được lưu thông"
        elif AQI in range(51, 101):
            mucdo = "Trung bình. "+neutralFace+"\nNhững người nhạy cảm nên tránh"
        elif AQI in range(101, 151):
            mucdo = confuseFace+" Không tốt cho nhóm nhạy cảm và công chúng nói chung."
        elif AQI in range(151, 201):
            mucdo = "Có hại cho sức khỏe. "+fearfulFace+"\nTăng mức độ trầm trọng của bệnh tim và phổi"
        elif AQI in range(201, 301):
            mucdo = "Rất có hại cho sức khỏe. "+medicalMask+"\nTất cả mọi người sẽ bị ảnh hưởng đáng kể"
        else:
            mucdo = "Nguy hại. "+nauseatedFace+"\nTất cả mọi người có nguy cơ gặp các phản ứng mạnh, ảnh hưởng xấu đến sức khỏe"
        tmp = "\nChỉ số ô nhiễm AQI: *"+ str(AQI) + "*\nMức độ: "+ mucdo
        return tmp
    except Exception as e:
        print(f"Error processing AirVisual data: {e}")
        return "\n❌ Lỗi khi xử lý dữ liệu ô nhiễm."
        
def send_weather(chat_id):
    try:
        mess = data_openweather(contents) + data_air(content_air)
        message = process_message(mess)
        payload = {
            'parse_mode':'Markdown',
            "text": message.encode("utf8") if isinstance(message, str) else message,
            "chat_id": chat_id
        }
        requests.post("https://api.telegram.org/bot{}/sendMessage".format(TOKEN), payload)
    except Exception as e:
        print(f"Error in send_weather: {e}")
        post_error(f"Lỗi gửi tin nhắn thời tiết: {str(e)}", chat_id)
