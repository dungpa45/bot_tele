import json
import requests
import time
from datetime import datetime, timedelta
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from yaml import Loader
from yaml import load

absolutepath = os.path.abspath(__file__)
fileDirectory = os.path.dirname(absolutepath)
print(fileDirectory)
with open(fileDirectory+"/secret.yaml","r") as yml_file:
    data = load(yml_file, Loader=Loader)

TOKEN = data["telegram"]["token_girl"]
USER_ID = data["telegram"]["user_id"]
TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage".format(TOKEN)
API_key = data["api_key"]["openweather"]
API_key_air = data["api_key"]["airvisual"]
place = "Hanoi"
link = 'http://api.openweathermap.org/data/2.5/weather?q={}&lang=vi&appid={}'.format(place,API_key)
contents = requests.get(link)

link_air = "http://api.airvisual.com/v2/city?city=Hanoi&state=Hanoi&country=Vietnam&key={}".format(API_key_air)
content_air = requests.get(link_air).json()


degree_sign= u'\N{DEGREE SIGN}' + "C"
thunderstorm = u'\U0001F4A8'    # Code: 200's, 900, 901, 902, 905
drizzle = u'\U0001F4A7'         # Code: 300's
rain = u'\U00002614'            # Code: 500's
snowflake = u'\U00002744'       # Code: 600's snowflake
snowman = u'\U000026C4'         # Code: 600's snowman, 903, 906
atmosphere = u'\U0001F301'      # Code: 700's foogy
clearSky = u'\U00002600'        # Code: 800 clear sky
fewClouds = u'\U000026C5'       # Code: 801 sun behind clouds
clouds = u'\U00002601'          # Code: 802-803-804 clouds general
hot = u'\U0001F525'             # Code: 904
# Emoji
defaultEmoji = u'\U0001F300'    # default emojis
starFace = u'\U0001F929'        # 0-50
neutralFace = u'\U0001F610'        # 51-100
confuseFace = u'\U0001F615'        # 101-150
fearfulFace = u'\U0001F628'        # 151-200
medicalMask = u'\U0001F637'     # 201-300
nauseatedFace = u'\U0001F922'   # > 301

updater = Updater(token=TOKEN)

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
    t = datetime.fromtimestamp(time) + timedelta(hours=7)
    return t.strftime('%H:%M:%S')
    # return datetime.fromtimestamp(time).strftime('%H:%M:%S')

def data_openweather(content):
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
        "\nNhiệt độ: "+str(temp)+degree_sign+\
        "\nCao nhất: "+str(temp_min)+degree_sign+" - Thấp nhất: "+str(tepm_max)+degree_sign+\
        "\nCảm giác như: "+str(feels)+degree_sign+\
        "\nĐộ ẩm: "+str(humidity)+"%"+\
        "\nThời tiết: " +weather_des +\
        "\nMặt trời: "+str(sunrise)+" - "+str(sunset)
    return tmp

def data_air(content):
    data = content['data']
    AQI = data["current"]["pollution"]["aqius"]
    if AQI in range(0,50):
        mucdo = "Tốt. "+starFace+"\nBạn nên để không khí trong nhà được lưu thông"
    elif AQI in range(51,100):
        mucdo = "Trung bình. "+neutralFace+"\nNhững người nhạy cảm nên tránh"
    elif AQI in range(101,150):
        mucdo = confuseFace+" Không tốt cho nhóm nhạy cảm và công chúng nói chung."
    elif AQI in range(151,200):
        mucdo = "Có hại cho sức khỏe. "+fearfulFace+"\nTăng mức độ trầm trọng của bệnh tim và phổi"
    elif AQI in range(201,300):
        mucdo = "Rất có hại cho sức khỏe. "+medicalMask+"\nTất cả mọi người sẽ bị ảnh hưởng đáng kể"
    else:
        mucdo = "Nguy hại. "+nauseatedFace+"\nTất cả mọi người có nguy cơ gặp các phản ứng mạnh, ảnh hưởng xấu đến sức khỏe"
    tmp = "\nChỉ số ô nhiễm AQI: "+ str(AQI) + "\nMức độ: "+ mucdo
    return tmp
        

mess = data_openweather(contents) + data_air(content_air)
message = process_message(mess)

payload = {
    "text": message.encode("utf8"),
    "chat_id": USER_ID
}

requests.post(TELEGRAM_URL, payload)
