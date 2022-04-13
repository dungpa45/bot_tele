from telegram.ext import Updater ,CommandHandler
import requests, re, os
from telegram import ReplyKeyboardMarkup
import random
from yaml import Loader
from yaml import load

absolutepath = os.path.abspath(__file__)
fileDirectory = os.path.dirname(absolutepath)
print(fileDirectory)
with open(fileDirectory+"/secret.yaml","r") as yml_file:
    data = load(yml_file, Loader=Loader)

reply_keboard = [['/dog','/cat']]
markup = ReplyKeyboardMarkup(reply_keboard,one_time_keyboard=True)

CHOOSE = 1

def get_dog_url():
    # Access the API and get the image URL
    contents = requests.get('https://random.dog/woof.json').json()
    #Get the image URL since we need that parameter to be able to send the image.
    image_url = contents['url']
    return image_url

def get_cat_url():
    # Access the API and get the image URL
    n =random.randint(0,99999999999999999999999)
    # contents1 = requests.get('http://aws.random.cat/meow').json()
    # contents1 = requests.get('https://cataas.com/cat?{}'.format(n))
    contents1 = requests.get('https://api.thecatapi.com/v1/images/search').json()
    #Get the image URL since we need that parameter to be able to send the image.
    # image_file = contents1['file']
    # image_file = contents1.url
    image_file = contents1[0]['url']
    return image_file

def get_cat_breed():
    l_cat_breed=[]
    cat_breed_list = requests.get('https://api.thecatapi.com/v1/breeds').json()
    for cat in cat_breed_list:
        l_cat_breed.append(cat["name"])
    l_str = ' /'.join(map(str, l_cat_breed))
    print(l_str)
    return l_str

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

def start(bot,update):
    user = update.message.from_user
    update.message.reply_text(
        "Hello master {} \nType /dog or /cat to see random picture\nType /dog_breed or /cat_breed to see all breeds".format(user.full_name),reply_markup=markup)
    # update.message.reply_text("Type /dog or /cat to see random picture")   

def dog(bot,update):
    url = get_image_dog_url()
    #Get the recipient’s ID
    chat_id = update.message.chat_id
    #it’s time to send the message, which is an image.
    bot.send_photo(chat_id=chat_id, photo=url)

def cat(bot1,update1):
    # url1 = get_image_cat_url()
    url1 = get_cat_url()
    chat_id = update1.message.chat_id
    bot1.send_photo(chat_id=chat_id, photo=url1)

def cat_breeds(bot,update):
    chat_id = update.message.chat_id
    str_cat_breed = get_cat_breed()
    update.message.reply_text(str_cat_breed)

def main():
    TOKEN = "1074719682:AAGB0S76v5lwAIxbkEIZJkXz-COgh23gPG8"
    # TOKEN = data["telegram"]["token_dogcat"]
    updater = Updater(TOKEN)
    
    dp = updater.dispatcher
    start_handler = CommandHandler('start',start)
    dp.add_handler(CommandHandler('dog',dog))
    dp.add_handler(CommandHandler('cat',cat))
    dp.add_handler(CommandHandler('dog_breed',dog))
    dp.add_handler(CommandHandler('cat_breed',cat_breeds))
    dp.add_handler(start_handler)
    #start the bot
    updater.start_polling()
    #Run the bot until press ctrl +C
    updater.idle()
    
if __name__ == '__main__':
    main()
   
