import requests, re, os, logging, random
from telegram.ext import Updater ,CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import Update, ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# from yaml import Loader
# from yaml import load

# absolutepath = os.path.abspath(__file__)
# fileDirectory = os.path.dirname(absolutepath)
# print(fileDirectory)
# with open(fileDirectory+"/secret.yaml","r") as yml_file:
#     data = load(yml_file, Loader=Loader)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

reply_keboard = [['/dog','/cat']]
markup = ReplyKeyboardMarkup(reply_keboard,one_time_keyboard=True)

dog_breed_list = requests.get('https://api.thedogapi.com/v1/breeds').json()
dog_breed_list = random.sample(dog_breed_list,50)

cat_breed_list = requests.get('https://api.thecatapi.com/v1/breeds').json()
cat_breed_list = random.sample(cat_breed_list,50)

cat_img_link = "https://cdn2.thecatapi.com/images/" # add .png to the end of link

def get_dog_url():
    # Access the API and get the image URL
    contents = requests.get('https://random.dog/woof.json').json()
    #Get the image URL since we need that parameter to be able to send the image.
    image_url = contents['url']
    return image_url

def get_cat_url():
    # Access the API and get the image URL
    # contents1 = requests.get('http://aws.random.cat/meow').json()
    # contents1 = requests.get('https://cataas.com/cat?{}'.format(n))
    contents1 = requests.get('https://api.thecatapi.com/v1/images/search').json()
    #Get the image URL since we need that parameter to be able to send the image.
    image_file = contents1[0]['url']
    return image_file

def get_image_cat_breed():
    l_cat_breed=[]
    cat_breed_list = requests.get('https://api.thecatapi.com/v1/breeds').json()
    for cat in cat_breed_list:
        l_cat_breed.append(cat["name"])
    l_str = ' /'.join(map(str, l_cat_breed))
    print(l_str)
    return l_str

def get_list_dog_breed():
    l_dog_breed=[]
    l_d_bred=[]
    for dog in dog_breed_list:
        l_dog_breed.append(dog["name"])
        l_d_bred.append({"name":dog["name"],"image":dog["image"]["url"]})
    return [l_dog_breed,l_d_bred]

def get_image_breed_dog(dog_name):
    l_new_data = get_list_dog_breed()[1]
    for data in l_new_data:
        if dog_name in data["name"]:
            url = data["image"] 
            return data["image"]



# iterate the URL until we get the file extension that we want
def get_image_dog_url():
    allowed_extension = ['jpg', 'JPG', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_dog_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url 

def get_image_cat_url():
    allowed_extension = ['jpg', 'JPG', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url1 = get_cat_url()
        file_extension = re.search("([^.]*)$", url1).group(1).lower()
    return url1 

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text(
        "Hello master {} \nType /dog or /cat to see random picture\nType /dog_breed to see all breeds".format(user.full_name),reply_markup=markup)
    # update.message.reply_text("Type /dog or /cat to see random picture")   

def dog(update: Update, context: CallbackContext):
    url = get_image_dog_url()
    #Get the recipient’s ID
    chat_id = update.message.chat_id
    #it’s time to send the message, which is an image.
    context.bot.send_photo(chat_id=chat_id, photo=url)

def cat(update: Update, context: CallbackContext):
    # url1 = get_image_cat_url()
    url1 = get_cat_url()
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=url1)

# def cat_breeds(update: Update, context: CallbackContext):
#     chat_id = update.message.chat_id
#     str_cat_breed = get_cat_breed()
#     update.message.reply_text(str_cat_breed)

def dog_breeds(update: Update, context: CallbackContext):    
    kbs = []
    for name in get_list_dog_breed()[0]:
        kbs = kbs + [InlineKeyboardButton(text=name, callback_data="Dog:"+name)]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[x,y] for x,y in zip(kbs[::2], kbs[1::2])])
    update.message.reply_text("select dog breeds:",reply_markup=reply_markup)

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    breed_type = callback_data.split(":")[0]
    breed_name = callback_data.split(":")[1]
    if breed_type == "Dog":
        url = get_image_breed_dog(breed_name)
    # else:
    #     url = get_image_breed_cat()
    chat_id = update.callback_query.message.chat_id
    update.callback_query.message.edit_text(breed_name)
    context.bot.send_photo(chat_id=chat_id, photo=url)
    

def main():
    # TOKEN = "754452513:AAFOY_HfYO8dlX8i-R5wE2bjpr3N4i7_3a4"
    TOKEN = "1339111350:AAFGUd_GP1jTpQ-ZGwXx9boBer6Z3p-azHM"
    # TOKEN = data["telegram"]["token_dogcat"]
    updater = Updater(TOKEN,use_context=True)
    
    dp = updater.dispatcher
    start_handler = CommandHandler('start',start)
    dp.add_handler(CommandHandler('dog',dog))
    dp.add_handler(CommandHandler('cat',cat))
    dp.add_handler(CommandHandler('dog_breed',dog_breeds))
    # dp.add_handler(CommandHandler('cat_breed',cat_breeds))
    dp.add_handler(CallbackQueryHandler(button_callback))
    
    dp.add_handler(start_handler)
    #start the bot
    updater.start_polling()
    # updater.start_webhook()
    #Run the bot until press ctrl +C
    # updater.idle()
if __name__ == '__main__':
    main()
