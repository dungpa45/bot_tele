import glob
import os, json, random
import pickle
import requests
import redis
from telegram.ext import Updater, CommandHandler
from telegram import ReplyKeyboardMarkup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# connect redis
HOST = data["redis"]["host"]
PASSWORD = data["redis"]["pass"]
redis_server = redis.Redis(host=HOST, port=6379, db=1, password=PASSWORD)
all_keys = redis_server.keys()

def get_all_key_redis():
    all_keys = redis_server.keys()
    all_keys = [key.decode("utf-8") for key in all_keys]
    print(all_keys)
    return all_keys

def save_in_redis(d_value):
    print(type(d_value))
    try:
        with redis_server.pipeline() as pipe:
            # save key in redis
            pipe.set("girl",d_value)
            pipe.execute()
        redis_server.bgsave()
    except Exception as e:
        print("loi ko luu dc",e)
    print("save done")

def get_data_redis(str_key):
    # d_b_value = redis_server.hgetall(str_key)
    s_b_value = redis_server.get(str_key)
    s_value = s_b_value.decode("utf-8")
    l_value = json.loads(s_value)
    return l_value

reply_keboard = [['/girl', '/woman'],['/vsbg', '/sexygirl'], ['/gaingon', '/xinh']]
markup = ReplyKeyboardMarkup(reply_keboard, one_time_keyboard=True)

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

def get_google_album():
    print("get image from gg")
    scopes = ['https://www.googleapis.com/auth/photoslibrary.readonly']

    creds = None
    CREDENTIALS_FILE = 'credentials.pickle'

    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                scopes)
            creds = flow.run_local_server(port=8090)
            with open(CREDENTIALS_FILE, 'wb') as token:
                pickle.dump(creds, token)

    service = build('photoslibrary', 'v1', credentials=creds,static_discovery=False)

    albums_shared = service.sharedAlbums().list(
        pageSize=10).execute()

    list_album = albums_shared.get('sharedAlbums', [])
    # print(list_album)
    for album in list_album:
        if album["title"] == "gái xinh":
            album_id = album["id"]

    nextpagetoken = 'Dummy'
    c=0
    list_item=[]
    while nextpagetoken != '':
        print("wait.....")
        nextpagetoken = '' if nextpagetoken == 'Dummy' else nextpagetoken
        results = service.mediaItems().search(
                body={"albumId": album_id,
                    "pageSize": 100, "pageToken": nextpagetoken}).execute()
        # The default number of media items to return at a time is 25. The maximum pageSize is 100.
        items = results.get('mediaItems', [])
        nextpagetoken = results.get('nextPageToken', '')
        for item in items:
            c+=1
            # print(f"{c}\nURL: {item['productUrl']}")
            list_item.append(item['baseUrl'])
            # l.append(item['productUrl'])
    return list_item

def get_girl_img():
    print("check redis first")
    list_keys = get_all_key_redis()
    if list_keys == []:
        print("Chua co trong redis")
        l_img = get_google_album()
        img = random.choice(l_img)
        print("gg",img)
        s_l_img = json.dumps(l_img)
        save_in_redis(s_l_img)
        return img
    else:
        print("Da co trong redis")
        l_img = get_data_redis("girl")
        img = random.choice(l_img)
        print("redis",img)
        return img

def get_image_local(img_dir):
    data_path = os.path.join(img_dir, '*.jpg')
    files = glob.glob(data_path)
    img = random.choice(files)
    return img

def get_id_album(id_album):
    l_img = d_album_img[id_album]
    return l_img

def get_vsbg_img():
    l_img = get_id_album(d_title_id_album[titles_album[1]])
    img = random.choice(l_img)
    return img

# def get_girl_img():
#     l_img = get_id_album(d_title_id_album[titles_album[2]])
#     img = random.choice(l_img)
#     return img

def get_korea_img():
    l_img = get_id_album(d_title_id_album[titles_album[0]])
    img = random.choice(l_img)
    return img

def get_gaitay_img():
    l_img = get_id_album(d_title_id_album[titles_album[3]])
    img = random.choice(l_img)
    return img

def start(bot, update):
    user = update.message.from_user
    update.message.reply_text(
        "Hello {} \nType /gái /xinh /gaixinh /gaingon /sexygirl /girl /lady /vsbg /woman  to see random picture\nHave fun :)".format(
            user.full_name),
        reply_markup=markup)

def help(bot, update):
    update.message.reply_text('''Note:
    /gái /girl /woman: Gái xinh chọn lọc
    /gaidep /lady /gaixinh : Gái rất xinh 
    /sexygirl /vsbg /sexylady : Gái xinh quyến rũ
    /gaingon /girlxinh /xinh : Gái ngon hơn
    /korean /korea /gáihàn /gaihan: Gái Hàn Xẻng
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
                   photo=korea)

def gaitay(bot, update):
    gaitay = get_gaitay_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id, reply_to_message_id=mess_id,
                   photo=gaitay)

def anh(bot,update):
    gai = get_girl_img()
    update.context.message.reply_photo(photo=gai)

# def nangtho(bot, update):
#     list_nangtho = os.listdir('/home/dungpa/ig_girl')
#     str_nangtho = "/" + '\n/'.join(map(str,list_nangtho))
#     update.message.reply_text('''Danh sách các nàng ther:\n {}
#     \nFor have eat no ? :)'''.format(str_nangtho))

# def get_nangtho(bot,update):
#     chat_id = update.message.chat_id
#     mess_id = update.message.message_id
#     cmd = update["message"]["text"]
#     # name_folder = cmd.split("/")[1]
#     imgs = get_image_local("/home/dungpa/ig_girl"+cmd)
#     bot.send_photo(chat_id=chat_id,reply_to_message_id=mess_id, photo=open(imgs,"rb"))

def main():
    # TOKEN = data["telegram"]["token_quote"]
    TOKEN = "1339111350:AAFGUd_GP1jTpQ-ZGwXx9boBer6Z3p-azHM"
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dp.add_handler(CommandHandler('help', help))
    # dp.add_handler(CommandHandler('nangtho', nangtho))
    # dp.add_handler(CommandHandler(os.listdir('/home/dungpa/ig_girl'), get_nangtho))
    dp.add_handler(CommandHandler(["girl", "gái","gaidep","girlxinh",
                                    "lady","women", "woman","gaixinh","xinh"], girl))
    dp.add_handler(CommandHandler(['vsbg', 'sexygirl', 'sexylady','gaingon'], vsbg))
    dp.add_handler(CommandHandler(['korea', 'korean', 'gaihan',"gáihàn"], korea))
    dp.add_handler(CommandHandler(['gáitây', 'gaitay'], gaitay))
    dp.add_handler(start_handler)
    # start the bot
    updater.start_polling()
    # Run the bot until press ctrl +C
    updater.idle()

if __name__ == '__main__':
    main()
