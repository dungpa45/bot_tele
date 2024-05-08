import os

TOKEN = os.environ["TOKEN"]
API_NINJA = os.environ["API_NINJA"]
API_WEATHER = os.environ["API_WEATHER"]
API_AIRVISUAL = os.environ["API_AIRVISUAL"]

link_quote = "https://favqs.com/api/qotd"
link_fact = 'https://api.api-ninjas.com/v1/facts?limit=1'
link_uselessfact = "https://uselessfacts.jsph.pl/api/v2/facts/random"
link_shorten = 'https://cleanuri.com/api/v1/shorten'
link_subnet = 'https://networkcalc.com/api/ip/'
link_meals = "https://www.themealdb.com/api/json/v1/1/random.php"
link_cocktail = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
link_country = 'https://restcountries.com/v3.1/independent?status=true'
link_vnexpress_new = "https://vnexpress.net/rss/tin-noi-bat.rss"
link_aws_new = 'https://aws.amazon.com/blogs/aws/feed/'
link_gold = "https://gw.vnexpress.net/cr/?name=tygia_vangv202206"
link_xsmb = "https://api-xsmb.cyclic.app/api/v1"
link_xang = "https://vnexpress.net/chu-de/gia-xang-dau-3026"

modau = '''/quote để xem một câu quote
/fact để xem fact /uselessfact xem fact vô tri
/meal để xem một món ăn ngẫu nhiên
/cocktail để xem một cốc têu ngẫu nhiên
/an_trua hay /antrua để coi ăn cái chi
/country để xem thông tin một quốc gia bất kỳ
/news or /aws số_tin (số tin <=10) xem vài tin tức mới (vd: /news 3)
/weather Để xem thời tiết
/gold Xem giá vàng mới
/xsmb Xem kết quả xsmb mới nhất
/xang Xem giá xăng mới cập nhật
Nhập đường link bất kỳ sẽ cho ra một link rút gọn
Nhập IP hoặc CIDR để kiểm tra'''

meme_shiba = [
    "CAACAgIAAxkBAAEjQcdko_dV3sjlt4gfzMnxPwH0MUFHfwACFAADBc7CLQViulNpIrtiLwQ",
    "CAACAgIAAxkBAAEjQetko_pCzXbPPvGI4mOnlpgseNzbEwACRwADBc7CLQABCW2lqqWMJS8E",
    "CAACAgIAAxkBAAEjQeVko_o1Mu0iAesAAcncnhIlGk38_5cAAhYAAwXOwi2GqrCk_LK3PS8E",
    "CAACAgIAAxkBAAEjQe5ko_pZGT837ytT2HsacqklosOd1wACIBIAAkl9SEg1uJaZLbP0Ui8E",
    "CAACAgIAAxkBAAEjSqdkpOUoeyHXMDZLWSQyKR5sc45TvAACDwADBc7CLdU09hfXHyxULwQ",
    "CAACAgUAAxkBAAEjSrBkpOVo-aEqJEjbihnv87RltH38_QACzwMAAmf4EVRVNziyEn7XIi8E",
    "CAACAgIAAxkBAAEjSrNkpOV4vVp6KFZEy4nY_kuTOsYSqQACGQ4AAr180UpeHEVsns7Gxi8E"
]

l_antrua = ['cơm rang', 'bún vịt', 'cơm rang ngan', 'bún đậu', 'xôi', 'bún chả',
                 'bánh mỳ', 'bún pò', 'cơm thố', 'phở pò','cơm trộn','nem nướng']
#################################################################
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
