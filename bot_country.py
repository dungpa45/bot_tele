import json
import re, requests
import random
from telegram.ext import Updater ,CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardMarkup
import glob, os
from yaml import Loader
from yaml import load

absolutepath = os.path.abspath(__file__)
fileDirectory = os.path.dirname(absolutepath)
print(fileDirectory)
with open(fileDirectory+"/secret.yaml","r") as yml_file:
    data = load(yml_file, Loader=Loader)

reply_keyboard = [['/quiz','/random_country']]
markup = ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True)

region_all = requests.get("https://restcountries.eu/rest/v2/all").json()
list_name = []
for i in region_all:
    name = i["name"]
    list_name.append(name)


def get_flag_image(code3):
    # data_path = os.path.join('flag','*.png')
    # files = glob.glob(data_path)
    img_png = "flag/"+code3+".png"
    return img_png

def get_name_region():
    rnd = random.choices(list_name,k=4)
    return rnd

def icon_flag(code):
    OFFSET = 127462 - ord('A')
    code = code.upper()
    flag_emo = chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)
    return flag_emo

def get_all_data_country(l_data):
    l_info_country = []
    for info in l_data:
        name = info["name"]
        code2 = info["alpha2Code"].lower()
        icon = " "+icon_flag(code2)
        capital = info["capital"]
        spelling = ", ".join(info["altSpellings"])
        region = info["region"]
        subregion = info["subregion"]
        population = info["population"]
        demonym = info["demonym"] #dan toc
        area = info["area"]
        timezone = ", ".join(info["timezones"])
        borders = ", ".join(info["borders"]) #bien gioi
        languages =", ".join(lang["name"] for lang in info["languages"])
        currencies = info["currencies"][0]["name"]
        gini = info["gini"] #chi so binh dang thu nhap
        regionalBlocs = ", ".join(trade["name"] for trade in info["regionalBlocs"])
        regionalBlocs_acronym = ", ".join(trade["acronym"] for trade in info["regionalBlocs"])
        domain = info["topLevelDomain"][0]
        callingcode = info["callingCodes"][0]
    
        temp = "_Information about:_ "+"*"+name+"*"+icon+icon+\
            "\nSpelling: "+spelling+\
            "\nCapital: "+capital+\
            "\nRegion: "+region+" - Subregion: "+subregion+\
            "\nPopulation: "+str(population)+\
            "\nDemonym: "+demonym+\
            "\nArea: "+str(area)+" km2"+\
            "\nTimezone: "+timezone+\
            "\nBorders: "+borders+\
            "\nLanguage: "+languages+\
            "\nCurrencies: "+currencies+\
            "\nTrade blocs: "+regionalBlocs+" - "+regionalBlocs_acronym+\
            "\nincome inequality: "+str(gini)+\
            "\nTop level Domain: "+domain+\
            "\nCalling code: "+callingcode
        l_info_country.append(temp)
    print("ok")
    return l_info_country

def get_info_by_name(search_name):
    name_url = "https://restcountries.eu/rest/v2/name/{}".format(search_name)
    l_info = requests.get(name_url).json()
    l_region_info = get_all_data_country(l_info)
    return l_region_info

def get_country_by_capital(name_cap):
    name_url = "https://restcountries.eu/rest/v2/capital/{}".format(name_cap)
    l_data = requests.get(name_url).json()
    l_region = []
    for data in l_data:
        name = data["name"]
        code2 = data["alpha2Code"].lower()
        icon = " "+icon_flag(code2)
        capital = data["capital"]
        temp = "*"+name+"*"+icon+icon+"\n"+capital
        l_region.append(temp)
    return l_region

def start(bot, update):
    user = update.message.from_user
    update.message.reply_text('''Hello {} \nYou can type name of country you want find more information.
    You want to play, let press quiz.
    \nPlease type keyword with English'''.format(user.full_name), reply_markup=markup)

def help(bot, update):
    update.message.reply_text('''Help:
    You want to find all info about country: info <country>
    You want to find country with capital: cap <capital>

    _Have fun_ :) ''',ParseMode.MARKDOWN)

def rep(bot, update):
    user_text = update.message.text
    input_text = user_text.split(" ")
    print(input_text, type(input_text),input_text[0])
    
    if input_text[0] in ["info","Info"]:
        info_data = "\n\n".join(get_info_by_name(input_text[1]))
        update.message.reply_text(info_data,ParseMode.MARKDOWN)
    elif input_text[0] in ["cap","Cap"]:
        name_region = "\n".join(get_country_by_capital(input_text[1]))
        update.message.reply_text(name_region,ParseMode.MARKDOWN)
    else:
        update.message.reply_text("*incorrect syntax*\nYou can type /help for guide",ParseMode.MARKDOWN)

def get_ran_country():
    list_inf = get_all_data_country(region_all)
    inf = random.choice(list_inf)
    return inf

def random_country(bot, update):
    region = get_ran_country()
    mess_id = update.message.message_id
    update.message.reply_text(region,ParseMode.MARKDOWN,reply_to_message_id=mess_id)

def quiz(bot,update):
    a = get_name_region()[0]
    b = get_name_region()[1]
    c = get_name_region()[2]
    d = get_name_region()[3]
    l=[a,b,c,d]
    pick1 = random.choice(l)
    url = "https://restcountries.eu/rest/v2/name/{}".format(pick1)
    alpha3 = requests.get(url).json()[0]["alpha3Code"].lower()
    image_flag = get_flag_image(alpha3)
    button = [[InlineKeyboardButton(a,callback_data="Viet Nam"),
                InlineKeyboardButton(b,callback_data="England")],
              [InlineKeyboardButton(c,callback_data="s"),
                InlineKeyboardButton(d,callback_data="sa")]
            ]
    print(image_flag)
    reply_markup = InlineKeyboardMarkup(button)
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id,photo=open(image_flag,'rb'),reply_markup=reply_markup)
    update.message.reply_text("select:",reply_markup=reply_markup)
    
    
def button(bot, update):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Selected option: {}".format(query.data))


def main():
    TOKEN = data["telegram"]["token_country"]
    updater = Updater(token=TOKEN)
    dp = updater.dispatcher
    start_handler = CommandHandler('start',start)
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('quiz', quiz))
    dp.add_handler(CommandHandler('random_country', random_country))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text,rep))
    dp.add_handler(start_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
