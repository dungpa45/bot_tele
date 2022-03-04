from telegram.ext import Updater ,CommandHandler
import requests, re, os
from telegram import ReplyKeyboardMarkup
from PIL import Image 
import random


reply_keboard = [['/dog','/cat']]
markup = ReplyKeyboardMarkup(reply_keboard,one_time_keyboard=True)

CHOOSE = 1

def get_url():
    # Access the API and get the image URL
    contents = requests.get('https://random.dog/woof.json').json()
    #Get the image URL since we need that parameter to be able to send the image.
    image_url = contents['url']
    return image_url

def get_url1():
    # Access the API and get the image URL
    n =random.randint(0,99999999999999999999999)
    # contents1 = requests.get('http://aws.random.cat/meow').json()
    contents1 = requests.get('https://cataas.com/cat?{}'.format(n))
    #Get the image URL since we need that parameter to be able to send the image.
    # image_file = contents1['file']
    image_file = contents1.url
    return image_file


# iterate the URL until we get the file extension that we want
def get_image_url():
    allowed_extension = ['jpg', 'JPG', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url 

def get_image_url1():
    allowed_extension = ['jpg', 'JPG', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url1 = get_url1()
        
        file_extension = re.search("([^.]*)$", url1).group(1).lower()
    return url1 

def start(bot,update):
    user = update.message.from_user
    update.message.reply_text(
        "Hello master {} \nType /dog or /cat to see random picture\nType some text".format(user.full_name),reply_markup=markup)
    # update.message.reply_text("Type /dog or /cat to see random picture")
    

def dog(bot,update):
    url = get_image_url()
    #Get the recipient’s ID
    chat_id = update.message.chat_id
    #it’s time to send the message, which is an image.
    bot.send_photo(chat_id=chat_id, photo=url)

def cat(bot1,update1):
    # url1 = get_image_url1()
    url1 = get_url1()
    chat_id = update1.message.chat_id
    bot1.send_photo(chat_id=chat_id, photo=url1)


def main():
    TOKEN = "754452513:AAFOY_HfYO8dlX8i-R5wE2bjpr3N4i7_3a4"
    # PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(TOKEN)
    
    dp = updater.dispatcher
    start_handler = CommandHandler('start',start)
    dp.add_handler(CommandHandler('dog',dog))
    dp.add_handler(CommandHandler('cat',cat))
    dp.add_handler(start_handler)
    #start the bot
    updater.start_polling()
    #Run the bot until press ctrl +C
    updater.idle()
    
if __name__ == '__main__':
    main()
   
