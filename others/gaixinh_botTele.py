from telegram.ext import Updater ,CommandHandler, InlineQueryHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, ReplyKeyboardMarkup
import glob, random, os
from yaml import Loader
from yaml import load

with open("/home/dung/OSAM/Build_bot/bot_tele_girl/secret.yaml","r") as yml_file:
    data = load(yml_file, Loader=Loader)

reply_keboard = [['/girl','/woman'],['/vsbg','/sexygirl'],['/korean','/gaitay']]
markup = ReplyKeyboardMarkup(reply_keboard,one_time_keyboard=True)


def get_image_local(img_dir):
    data_path = os.path.join(img_dir,'*.jpg')
    files = glob.glob(data_path)
    img_ = random.choice(files)
    img = img_.replace('\\','/')
    return img

def get_girl_img():
    img = get_image_local("F:\ANH\Girls\GaiChauA")
    return img

def get_woman_img():
    img = get_image_local("F:\ANH\Girls\GaiXinhChonLoc")
    return img

def get_vsbg_img():
    img = get_image_local("F:\ANH\Girls\VSBG")
    return img

def get_korea_img():
    img = get_image_local("F:\ANH\Girls\Korea")
    return img

def get_gaitay_img():
    img = get_image_local("F:\ANH\Girls\GaiTay")
    return img

def get_twice_img():
    img = get_image_local("F:\ANH\Girls\Twice")
    return img

def start(bot,update):
    user = update.message.from_user
    update.message.reply_text(
        "Hello master {} \nType /gái /sexygirl /girl /lady /vsbg /woman /korean /gaitay to see random picture\nHave fun :)".format(user.full_name),
        reply_markup=markup)

def help(bot,update):
    update.message.reply_text('''Note:
    /gái /girl /lady /woman: _Gái xinh chọn lọc_
    /sexygirl /vsbg : _Gái xinh quyến rũ_
    /korean /korea /gáihàn: _Gái Hàn Xẻng_
    /gaitay /gáitây: _Gái Tây_
    *Have fun* :) ''',ParseMode.MARKDOWN)

def girl(bot,update):
    girl = get_girl_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    # bot.send_photo(chat_id=chat_id,reply_to_message_id=mess_id, photo=open(girl,"rb"))
    angry = u'\U0001F620'
    text = "dadad"+angry
    bot.send_message(chat_id=chat_id,text=text, parse_mode=ParseMode.MARKDOWN)
def woman(bot,update):
    woman = get_woman_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id,reply_to_message_id=mess_id, photo=open(woman,"rb"))
    
def vsbg(bot,update):
    vsbg = get_vsbg_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id,reply_to_message_id=mess_id, photo=open(vsbg,"rb"))

def korea(bot,update):
    korea = get_korea_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id,reply_to_message_id=mess_id, photo=open(korea,"rb"))

def gaitay(bot,update):
    gaitay = get_gaitay_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id,reply_to_message_id=mess_id, photo=open(gaitay,"rb"))

def twice(bot,update):
    twice = get_twice_img()
    chat_id = update.message.chat_id
    mess_id = update.message.message_id
    bot.send_photo(chat_id=chat_id,reply_to_message_id=mess_id, photo=open(twice,"rb"))

def anh(bot,update):
    gai = get_girl_img()
    update.context.message.reply_photo(photo=open(gai,"rb"))

def time(bot, update, job_queue):
    job_queue.run_repeating(anh, interval=5, context=update)
    job_queue.run_repeating()

def main():
    TOKEN = data["telegram"]["token_girl"]
    updater = Updater(TOKEN)
    
    dp = updater.dispatcher
    start_handler = CommandHandler('start',start)
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(CommandHandler(['girl','gái','women'],girl))
    dp.add_handler(CommandHandler(['woman','gái','lady'],woman))
    dp.add_handler(CommandHandler(['vsbg','sexygirl','sexylady'],vsbg))
    dp.add_handler(CommandHandler(['korea','korean','gaihan'],korea))
    dp.add_handler(CommandHandler(['gáitây','gaitay'],gaitay))
    dp.add_handler(CommandHandler(['long','twice'],twice))
    dp.add_handler(MessageHandler(Filters.text, time, pass_job_queue=True))

    dp.add_handler(start_handler)
    #start the bot
    updater.start_polling()
    #Run the bot until press ctrl +C
    updater.idle()
    
if __name__ == '__main__':
    main()

