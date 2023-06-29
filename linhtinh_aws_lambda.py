import json, traceback, os, io
import requests, re, random
import ipaddress
from googletrans import Translator
from requests.exceptions import HTTPError

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


def send_photo(image_url,chat_id,cap=None):
    response = requests.get(image_url)
    photo = io.BytesIO(response.content)
    files = {"photo": photo}
    if cap is None:
        tele_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}"
    else:
        tele_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}&caption={cap}"
    try:
        r=requests.post(tele_url,files=files)
        r.raise_for_status()
    except HTTPError as e:
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
        payload = {'text': "Có lỗi rồi:\n" + e.response.text}
        requests.post(url,json=payload)

def get_quote():
    res = requests.get("https://favqs.com/api/qotd")
    if res.status_code == requests.codes.ok:
        data_quote = res.json()
        quote = data_quote["quote"]["body"]
        author = data_quote["quote"]["author"]
        message = '_"'+quote+'"_'+"\n\n"+'*'+author+'*'
        return message
    else:
        error = "StatusCode: " + str(res.status_code) +" "+ res.text
        return error

def send_quote(chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    quote = get_quote()
    payload = {'parse_mode':'Markdown','text': quote}
    requests.post(url,json=payload)

def get_n_send_fact(chat_id):
    res = requests.get('https://api.api-ninjas.com/v1/facts?limit=1', headers={'X-Api-Key':API_NINJA})
    if res.status_code == requests.codes.ok:
        content = res.json()
        fact = content[0]['fact']
        vn_fact = translate_vn(fact)
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
        payload = {'parse_mode':'Markdown','text': fact +"\n\n"+ vn_fact}
        requests.post(url,json=payload)
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        return error

def get_n_send_useless_fact(chat_id):
    res = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
    if res.status_code == requests.codes.ok:
        content = res.json()
        useless = content["text"]
        vn_fact = translate_vn(useless)
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
        payload = {'parse_mode':'Markdown','text': useless +"\n\n"+ vn_fact}
        requests.post(url,json=payload)
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        return error

def send_text(text_input,chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    if "help" in text_input or "/help" in text_input or "/start" in text_input:
        payload = {'text': 
'''Gõ /quote để xem một câu quote
Gõ /fact để xem fact /uselessfact xem face vô tri
Gõ /meal để xem một món ăn ngẫu nhiên
Gõ /cocktail để xem một cốc têu ngẫu nhiên
Gõ /an_trua /antrua để coi ăn cái chi
Nhập đường link bất kỳ sẽ cho ra một link rút gọn'''}
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

def short_link(chat_id, text_input):
    data = {'url': text_input}
    payload=requests.post('https://cleanuri.com/api/v1/shorten',data)
    short_url=payload.json()['result_url']
    print("The short url is : {}".format(short_url))
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    payload = {'text': short_url}
    requests.post(url,json=payload)

def get_subnet(subnet):
    res = requests.get('https://networkcalc.com/api/ip/'+subnet)
    if res.status_code == requests.codes.ok:
        content = res.json()
        return content["address"]
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        return error

def valid_ip_or_cidr(ip):
    try:
        ipaddress.IPv4Address(ip)
        print('valid as address')
        data = get_subnet(ip)
        text_data = dict_to_text(data)
        return text_data
    except Exception:
        try:
            ipaddress.IPv4Network(ip)
            print('valid as network')
            data = get_subnet(ip)
            text_data = dict_to_text(data)
            return text_data
        except Exception:
            print('invalid as both an address and network')
            exceptdata = traceback.format_exc().splitlines()
            data = exceptdata[-1]
            return data

def send_network_info(text_input,chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    res = valid_ip_or_cidr(text_input)
    payload = {'text': res}
    requests.post(url,json=payload)

def validate_ip_address(ip_address):
    # Regular expression pattern for IP address validation
    pattern = r'^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$'
    # Check if the input matches the pattern
    if re.match(pattern, ip_address):
        return True
    else:
        return False

def info_meals(dictionary):
    # text = ''
    m={}
    d={}
    for key, value in dictionary.items():   
        if value in ['',' ',None]:
            continue
        else:   
            if 'strIngredient' in key:
                m.update({key:value})
            elif 'strMeasure' in key:
                new_key = key.replace('strMeasure','strIngredient')
                d.update({new_key:value})
    new_d = dict((m.get(k, k), v) for (k, v) in d.items())
    nguyen_lieu = dict_to_text(new_d)
    try:
        text = f'''Tên: {dictionary["strMeal"]}
Loại: {dictionary["strCategory"]} 
Khu vực: {dictionary["strArea"]}
\nNguyên liệu:
{translate_vn(nguyen_lieu)}
Link Youtube: {dictionary["strYoutube"]}'''
        img_link = dictionary["strMealThumb"]
        eng_guide = dictionary["strInstructions"]
        vi_guide = translate_vn(eng_guide)
        guide = f'''*Hướng dẫn:* {vi_guide}
\nNguồn: {dictionary['strSource']}'''
    except Exception:
        traceback.print_exc()
    return [text,img_link,guide]

def send_meals(chat_id):
    res = requests.get("https://www.themealdb.com/api/json/v1/1/random.php")
    if res.status_code == requests.codes.ok:
        l_res = res.json()
        data_meal = l_res["meals"][0]
        l_info_meal = info_meals(data_meal)
        print(l_info_meal[0])
        # url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
        # payload = {'parse_mode':'Markdown','text': text_meal}
        # requests.post(url,json=payload)
        send_photo(l_info_meal[1],chat_id,l_info_meal[0])
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
        payload = {'parse_mode':'Markdown','text': l_info_meal[2]}
        requests.post(url,json=payload)
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        return error

def info_drinks(dictionary):
    # text = ''
    m={}
    d={}
    for key, value in dictionary.items():   
        if value in ['',' ',None]:
            continue
        else:   
            if 'strIngredient' in key:
                m.update({key:value})
            elif 'strMeasure' in key:
                new_key = key.replace('strMeasure','strIngredient')
                d.update({new_key:value})
    new_d = dict((m.get(k, k), v) for (k, v) in d.items())
    nguyen_lieu = dict_to_text(new_d)
    try:
        text = f'''Tên: {dictionary["strDrink"]}
Loại: {dictionary["strCategory"]} 
Alcoholic: {dictionary["strAlcoholic"]}
Cốc: {dictionary["strGlass"]}
\nNguyên liệu:
{translate_vn(nguyen_lieu)}'''
        img_link = dictionary["strDrinkThumb"]
        eng_guide = dictionary["strInstructions"]
        vi_guide = translate_vn(eng_guide)
        guide = f'''*Hướng dẫn:* {vi_guide}'''
    except Exception:
        traceback.print_exc()
    return [text,img_link,guide]

def send_cocktail(chat_id):
    res = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php")
    if res.status_code == requests.codes.ok:
        l_res = res.json()
        data_drink = l_res["drinks"][0]
        l_info_drink = info_drinks(data_drink)
        print(l_info_drink[0])
        # url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
        # payload = {'parse_mode':'Markdown','text': text_drink}
        # requests.post(url,json=payload)
        send_photo(l_info_drink[1],chat_id,l_info_drink[0])
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
        payload = {'parse_mode':'Markdown','text': l_info_drink[2]}
        requests.post(url,json=payload)
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        return error

def an_trua(chat_id):
    l_antrua = ['cơm rang', 'bún vịt', 'phở vịt quay', 'bún đậu', 'xôi', 'bún chả'
                 'bánh mỳ', 'bún pò', 'cơm thố', 'phở pò','cơm trộn','nem nướng']
    mon = random.choice(l_antrua)
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    payload = {'parse_mode':'Markdown','text':mon}
    requests.post(url,json=payload)

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
        if validate_ip_address(user_text):
            send_network_info(user_text,chat_id)
            return {"statusCode": 200}
        if "https://" in user_text or "http://" in user_text:
            short_link(chat_id,user_text)
            return {"statusCode": 200}
        elif "/quote" in user_text:
            send_quote(chat_id)
            return {"statusCode": 200}
        elif "/fact" in user_text:
            get_n_send_fact(chat_id)
            return {"statusCode": 200}
        elif "/uselessfact" in user_text:
            get_n_send_useless_fact(chat_id)
            return {"statusCode": 200}
        elif "/meal" in user_text:
            send_meals(chat_id)
            return {"statusCode": 200}
        elif "/cocktail" in user_text:
            send_cocktail(chat_id)
            return {"statusCode": 200}
        elif user_text in ["/trua_nay_an_gi","/an_trua","/antrua"]:
            an_trua(chat_id)
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
    