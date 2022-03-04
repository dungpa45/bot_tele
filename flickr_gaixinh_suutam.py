from telegram.ext import Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, ReplyKeyboardMarkup
import glob
import random
import os
from flickrapi import FlickrAPI
import json
import requests
import random
from yaml import Loader
from yaml import load

with open("./secret.yaml","r") as yml_file:
    data = load(yml_file, Loader=Loader)

reply_keboard = [['/girl', '/woman'],['/vsbg', '/sexygirl'], ['/gaingon', '/xinh']]
markup = ReplyKeyboardMarkup(reply_keboard, one_time_keyboard=True)

CHOOSE = 1

def get_requestURL(user_id, endpoint="getList"):
    user_id = user_id.replace("@", "%40")
    url_upto_apikey = ("https://api.flickr.com/services/rest/?method=flickr.photosets." +
                       endpoint +
                       "&api_key="+ data["api_key"]["flickr"] +
                       "&user_id="+user_id +
                       "&format=json&nojsoncallback=1")
    return(url_upto_apikey)


user_id = "184613026@N08"  #toi
# user_id = "152972566@N05" #thg nay die r :(
url = get_requestURL(user_id, endpoint="getList")
strlist = requests.get(url).content
json_data = json.loads(strlist.decode('utf-8'))
albums = json_data["photosets"]["photoset"]

print("{} albums found for user_id={}".format(len(albums),user_id))

titles_album = ['Korea', 'VSBG','GaiChauA', 'GaiTay']
id_album = ['72157711140679127', '72157711004094338',
            "72157711003763163", "72157710952790532"]
# titles_album = ['VSBG 11 3 2020', 'MNTH 10-3-2020',
#                 'GXCL 8-1-2020', 'vsbg 8-1-2020', 'MNTH 8-1-2020']
# id_album = ['72157713444579362', '72157713435781243',
#             "72157712571486817", "72157712572926553", "72157712569680982"]
d_id_title = dict(zip(titles_album, id_album))

d_title_id_album = dict(zip(titles_album, id_album))


def get_photo_url(farmId, serverId, Id, secret):
    return (("https://farm" + str(farmId) +
             ".staticflickr.com/" + serverId +
             "/" + Id + '_' + secret + ".jpg"))


d_album_img = {}
for photoset_id, title in zip(id_album, titles_album):  # for each album
    url = get_requestURL(user_id, endpoint="getPhotos") + \
        "&photoset_id=" + photoset_id
    strlist = requests.get(url).content
    json1_data = json.loads(strlist.decode('utf-8'))

    urls = []
    for pic in json1_data["photoset"]["photo"]:  # for each picture in an album
        urls.append(get_photo_url(
            pic["farm"], pic['server'], pic["id"], pic["secret"]))

    d_album_img[photoset_id] = urls


def get_image_local(img_dir):
    data_path = os.path.join(img_dir, '*.jpg')
    files = glob.glob(data_path)
    img_ = random.choice(files)
    img = img_.replace('\\', '/')
    return img


def get_id_album(id_album):
    l_img = d_album_img[id_album]
    return l_img


def get_vsbg_img():
    l_img = get_id_album(d_title_id_album[titles_album[1]])
    img = random.choice(l_img)
    return img


def get_girl_img():
    l_img = get_id_album(d_title_id_album[titles_album[2]])
    img = random.choice(l_img)
    return img


def get_korea_img():
    l_img = get_id_album(d_title_id_album[titles_album[0]])
    img = random.choice(l_img)
    return img


def get_gaitay_img():
    l_img = get_id_album(d_title_id_album[titles_album[3]])
    img = random.choice(l_img)
    return img


def get_multi_vsbg_img():
    l_img = get_id_album(d_title_id_album["vsbg 8-1-2020"])
    img = random.choice(l_img)
    return img


def get_multi_girl_img():
    l_img = get_id_album(d_title_id_album["GXCL 8-1-2020"])
    # li_img = get_id_album(d_title_id_album["MNTH 8-1-2020"])
    img = random.choice(l_img)
    return img


def start(bot, update):
    user = update.message.from_user
    update.message.reply_text(
        "Hello master {} \nType /gái /xinh /gaixinh /gaingon /sexygirl /girl /lady /vsbg /woman  to see random picture\nHave fun :)".format(
            user.full_name),
        reply_markup=markup)


def help(bot, update):
    update.message.reply_text('''Note:
    /gái /girl /woman: Gái xinh chọn lọc
    /gaidep /lady /gaixinh : Gái rất xinh 
    /sexygirl /vsbg /sexylady : Gái xinh quyến rũ
    /gaingon, /girlxinh , /xinh : Gái ngon hơn
    /korean /korea /gáihàn: Gái Hàn Xẻng
    /gaitay /gáitây: Gái Tây
    Have fun :)''')


def girl(bot, update):
    girl = get_girl_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id, reply_to_message_id=mess_id, photo=girl)


def vsbg(bot, update):
    vsbg = get_vsbg_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id, reply_to_message_id=mess_id, photo=vsbg)


def korea(bot, update):
    korea = get_korea_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id, reply_to_message_id=mess_id,
                   photo=open(korea, "rb"))


def gaitay(bot, update):
    gaitay = get_gaitay_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id, reply_to_message_id=mess_id,
                   photo=open(gaitay, "rb"))


def multi_girl(bot, update):
    l_girl = get_multi_girl_img()
    print(l_girl, type(l_girl))
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id, reply_to_message_id=mess_id, photo=l_girl)


def multi_vsbg(bot, update):
    l_vsbg = get_multi_vsbg_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id, reply_to_message_id=mess_id, photo=l_vsbg)

def anh(bot,update):
    gai = get_girl_img()
    update.context.message.reply_photo(photo=gai)

def time(bot, update, job_queue):
    interval = 86400
    job_queue.run_repeating(anh, interval=interval, context=update)
    print("hi")
    job_queue.run_repeating()

def main():
    TOKEN = data["telegram"]["token_girl"]
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler(["girl", "gái", "women", "woman"], girl))
    # dp.add_handler(CommandHandler(["gaidep", "lady", "gaixinh"], multi_girl))
    dp.add_handler(CommandHandler(['vsbg', 'sexygirl', 'sexylady'], vsbg))
    # dp.add_handler(CommandHandler(['xinh', 'girlxinh', 'gaingon'], multi_vsbg))
    dp.add_handler(CommandHandler(['korea', 'korean', 'gaihan'], korea))
    dp.add_handler(CommandHandler(['gáitây', 'gaitay'], gaitay))
    dp.add_handler(MessageHandler(Filters.text, time, pass_job_queue=True))

    dp.add_handler(start_handler)
    # start the bot
    updater.start_polling()
    # Run the bot until press ctrl +C
    updater.idle()


if __name__ == '__main__':
    main()
