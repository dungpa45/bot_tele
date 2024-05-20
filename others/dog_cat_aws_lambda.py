import json, traceback, os, io
import requests, re
from googletrans import Translator

TOKEN = os.environ["TOKEN"]
API_NINJA = os.environ["API_NINJA"]

def translate_vn(fact):
    translator = Translator()
    vn_fact = translator.translate(fact,dest='vi').text
    return vn_fact

def dict_to_text(dictionary):
    text = ''
    for key, value in dictionary.items():
        text += f"{key}: {value}\n"
    return text

def get_dog_url():
    res = requests.get('https://random.dog/woof.json')
    if res.status_code == requests.codes.ok:
        contents = res.json()
        image_url = contents['url']
        return image_url
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        return error

def get_cat_url():
    res = requests.get('https://api.thecatapi.com/v1/images/search')
    if res.status_code == requests.codes.ok:
        contents1 = res.json()
        image_file = contents1[0]['url']
        return image_file
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        return error

def get_image_dog_url():
    allowed_extension = ['jpg', 'JPG', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_dog_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url 

def send_photo(image_url,chat_id):
    response = requests.get(image_url)
    photo = io.BytesIO(response.content)
    files = {"photo": photo}
    tele_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}"
    requests.post(tele_url,files=files)

def send_text(text_input,chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    if "help" in text_input or "/help" in text_input or "/start" in text_input:
        payload = {'text': '''Gõ /dog,/Dog,/chó,/DOG, /cat,/Cat,/CAT,/mèo, để xem ảnh
        '''}
    else:
        payload = {'text': "hổng hiểu gì hết trơn :)))\nGõ /help hoặc /start nha"}
    requests.post(url,json=payload)

def send_non_text(kind,chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    if kind == "sticker":
        payload = {'text': "thả sticker làm gì hử :)))\nGõ /help hoặc /start đi"}
    elif kind == "animation":
        payload = {'text': "gửi ảnh gif cc à :)))\nĐm /help hoặc /start và làm theo"}
    requests.post(url,json=payload)

def send_error(error_text,chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    payload = {'text': error_text}
    requests.post(url,json=payload)

# def handle_text_input(chat_id,text_input):
dog_text = ["/dog","/Dog","/chó","/DOG"]
cat_text = ["/cat","/Cat","/CAT","/mèo","/pussy"]

def lambda_handler(event, context):
    print(event)
    try:
        body=json.loads(event['body'])
        print(body)
        chat_id = body['message']['chat']['id']
        if 'sticker' in body['message']:
            # sticker = body['message']['sticker']
            send_non_text('sticker',chat_id)
            return {"statusCode": 200}
        elif 'animation' in body['message']:
            # animation = body['message']['animation']
            send_non_text('animation',chat_id)
            return {"statusCode": 200}
        user_text=body['message'].get('text')
        print("Message part : {}".format(user_text))
        
        if user_text in dog_text:
            dog_img=get_image_dog_url()
            send_photo(dog_img,chat_id)
            return {"statusCode": 200}
        elif user_text in cat_text:
            cat_img=get_cat_url()
            send_photo(cat_img,chat_id)
            return {"statusCode": 200}
        else:
            send_text(user_text,chat_id)
            return {"statusCode": 200}
    except Exception:
        traceback.print_exc()
        error = traceback.format_exc()
        send_text(error,chat_id)
        return {
            "statusCode": 200
        }
    