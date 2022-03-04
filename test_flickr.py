import glob
import random
import os
from flickrapi import FlickrAPI
import json
import requests
import random
from yaml import Loader
from yaml import load

with open("/home/dung/OSAM/Build_bot/bot_tele_girl/secret.yaml","r") as yml_file:
    data = load(yml_file, Loader=Loader)

# reply_keboard = [['/girl', '/woman'],['/vsbg', '/sexygirl'], ['/gaingon', '/xinh']]
# markup = ReplyKeyboardMarkup(reply_keboard, one_time_keyboard=True)

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
for i in albums:
    print(i["id"],i["title"])