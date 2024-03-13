import json, traceback, os, io
import requests, re, random, logging
import ipaddress, feedparser
import xmltodict
from googletrans import Translator
from requests.exceptions import HTTPError
from var_file import *
from weather import *

logger = logging.getLogger()
logger.setLevel("INFO")

def get_day_name(date_str):
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_str, '%d-%m-%Y')
    # Get the day name from the datetime object
    day_name = date_obj.strftime('%A')
    return day_name

def translate_vn(fact):
    translator = Translator()
    vn_fact = translator.translate(fact,dest='vi').text
    return vn_fact

def dict_to_text(dictionary):
    text = ''
    for key, value in dictionary.items():
        text += f"{key}: {value}\n"
    return text

def post_tele(chat_id,s_text):
    # s_text: content to send
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    payload = {'parse_mode':'Markdown','text': s_text}
    requests.post(url,json=payload)

def post_error(error_text,chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    payload = {'text': "API error :( \n)"+error_text}
    requests.post(url,json=payload)
    return {"statusCode": 200}

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

def get_n_send_quote(chat_id):
    res = requests.get(link_quote)
    if res.status_code == requests.codes.ok:
        data_quote = res.json()
        quote = data_quote["quote"]["body"]
        author = data_quote["quote"]["author"]
        message = '_"'+quote+'"_'+"\n\n"+'*'+author+'*'
        post_tele(chat_id,message)
    else:
        error = "StatusCode: " + str(res.status_code) +" "+ res.text
        post_error(error,chat_id)

# def send_quote(chat_id):
#     url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
#     quote = get_quote()
#     payload = {'parse_mode':'Markdown','text': quote}
#     requests.post(url,json=payload)

def get_n_send_fact(chat_id):
    res = requests.get(link_fact, headers={'X-Api-Key':API_NINJA})
    if res.status_code == requests.codes.ok:
        content = res.json()
        fact = content[0]['fact']
        vn_fact = translate_vn(fact)
        post_tele(chat_id, fact +"\n\n"+ vn_fact)
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        post_error(error,chat_id)

def get_n_send_useless_fact(chat_id):
    res = requests.get(link_uselessfact)
    if res.status_code == requests.codes.ok:
        content = res.json()
        useless = content["text"]
        vn_fact = translate_vn(useless)
        post_tele(chat_id, useless +"\n\n"+ vn_fact)
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        post_error(error,chat_id)

def send_text(text_input,chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    if "help" in text_input or "/help" in text_input or "/start" in text_input:
        payload = {'text': modau}
    elif "edited_mess" in text_input:
        payload = {'text': 'Đừng sửa tin nhắn, vì nó ko có ý nghĩa gì'}
    else:
        payload = {'text': "hổng hiểu gì hết trơn :)))\nGõ /help hoặc /start nha"}
    requests.post(url,json=payload)

def send_non_text(kind,chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    
    if kind == "sticker":
        payload = {'text': "thả sticker làm gì hử :)))\nGõ /help hoặc /start đi"}
    elif kind == "animation" or "photo":
        payload = {'text': "gửi ảnh gif cc à :)))\nĐm /help hoặc /start và làm theo"}
    requests.post(url,json=payload)
    send_meme(chat_id)

def send_meme(chat_id):
    url_sticker = f'https://api.telegram.org/bot{TOKEN}/sendSticker?chat_id={chat_id}'
    sticker = random.choice(meme_shiba)
    requests.post(url_sticker,json={"sticker":sticker})


def short_link(chat_id, text_input):
    data = {'url': text_input}
    payload=requests.post(link_shorten,data)
    short_url=payload.json()['result_url']
    print("The short url is : {}".format(short_url))
    # url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    # payload = {'text': short_url}
    # requests.post(url,json=payload)
    post_tele(chat_id,short_url)

def get_subnet(subnet):
    res = requests.get(link_subnet+subnet)
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
    # print(res)
    requests.post(url,json=payload)
    # post_tele(chat_id,res)

def validate_ip_address(ip_address):
    # Regular expression pattern for IP address validation
    pattern = r'^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$'
    # Check if the input matches the pattern
    if re.match(pattern, ip_address):
        return True
    else:
        return False

def info_meals(dictionary):
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
    res = requests.get(link_meals)
    if res.status_code == requests.codes.ok:
        l_res = res.json()
        data_meal = l_res["meals"][0]
        l_info_meal = info_meals(data_meal)
        send_photo(l_info_meal[1],chat_id,l_info_meal[0])
        # url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
        # payload = {'parse_mode':'Markdown','text': l_info_meal[2]}
        # requests.post(url,json=payload)
        post_tele(chat_id,l_info_meal[2])
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        # return error
        post_error(error,chat_id)

def info_drinks(dictionary):
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
    res = requests.get(link_cocktail)
    if res.status_code == requests.codes.ok:
        l_res = res.json()
        data_drink = l_res["drinks"][0]
        l_info_drink = info_drinks(data_drink)
        send_photo(l_info_drink[1],chat_id,l_info_drink[0])
        # url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
        # payload = {'parse_mode':'Markdown','text': l_info_drink[2]}
        # requests.post(url,json=payload)
        post_tele(chat_id,l_info_meal[2])
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        # return error
        post_error(error,chat_id)

def an_trua(chat_id):
    l_antrua = ['cơm rang', 'bún vịt', 'cơm rang ngan', 'bún đậu', 'xôi', 'bún chả',
                 'bánh mỳ', 'bún pò', 'cơm thố', 'phở pò','cơm trộn','nem nướng']
    mon = random.choice(l_antrua)
    # url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    # payload = {'parse_mode':'Markdown','text':mon}
    # requests.post(url,json=payload)
    post_tele(chat_id,mon)

def get_country(country):
    name = country['name']['common']
    full_name = country['name']['official']
    curr = country['currencies']
    curr_ = [key for key in curr.keys()][0]
    curr_name = curr[curr_]['name']
    region = country['region']
    sub_region = country['subregion']
    cap = ', '.join(country['capital'])
    icon_flag = country['flag']
    flag = country['flags']['png']
    l_lang = [val for key, val in country['languages'].items()]
    lang = ", ".join(l_lang)
    timezone = ", ".join(country["timezones"])
    try:
        bor = country["borders"]
        border = ", ".join(country["borders"])
    except Exception:
        border = ", khum"
    area = country['area']
    pop = country['population']
    map = country['maps']['googleMaps']
    startOfWeek = country['startOfWeek']
    try:
        curr_symbol = curr[curr_]['symbol']
        tien = f"Tiền: {curr_} ({curr_name}), ký hiệu: {curr_symbol}"
    except Exception:
        tien = f"Tiền: {curr_} ({curr_name}) symbol: khum có"
    text = f'''Tên: {name} {icon_flag}{icon_flag}
Tên chính thức: {full_name}
Khu vực: {region}, cụ thể: {sub_region}
Thủ đô: {cap}
Ngôn ngữ: {lang}
Múi giờ: {timezone}
Biên giới: {border}
Diện tích: {area} km2
Dân số: {pop}
{tien}
Vị trí trên map: {map}
Quốc kỳ: {flag}
startOfWeek: {startOfWeek}'''
    return text

def send_country(chat_id):
    res = requests.get(link_country)
    if res.status_code == requests.codes.ok:
        l_res = res.json()
        country = random.choice(l_res)
        text_info = get_country(country)
        # url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
        # payload = {'parse_mode':'Markdown','text': text_info}
        # requests.post(url,json=payload)
        post_tele(chat_id,text_info)
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        # return error
        post_error(error,chat_id)

def get_news(num):
    news_feed = feedparser.parse(link_new_rss)
    entry = news_feed["entries"]
    l_news = random.sample(entry,num)
    text_info = ""
    for n in l_news:
        text_info += n['title']+"\n"+n['link']+"\n\n"
    return text_info

def send_news(chat_id,user_text):
    l_rep_sai = ["Nhập số <=10 cơ mà má","Nhập lại số <=10 đê :)"]
    if "/news" == user_text:
        text_info = get_news(1)
    else:
        vesau = user_text.split(" ")[1]
        try:
            num = int(vesau)
            if num > 10:
                text_info = random.choice(l_rep_sai)
                send_meme(chat_id)
            else:
                text_info = get_news(num)
        except ValueError:
            text_info = random.choice(l_rep_sai)
            send_meme(chat_id)
    # url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}'
    # payload = {'parse_mode':'Markdown','text': text_info}
    # requests.post(url,json=payload)
    post_tele(chat_id,text_info)

def send_goldprice(chat_id):
    res_sjc = requests.get(link_vang_sjc)
    res_btmc = requests.get(link_vang_btmc)
    if res_btmc.status_code == requests.codes.ok and res_sjc.status_code == requests.codes.ok:
        l_gold_price = res_btmc.json()['DataList']["Data"][:10]
        n=1
        for gold in l_gold_price:
            ten_vang = gold["@n_"+str(n)]
            if ten_vang == "TRANG SỨC BẰNG VÀNG RỒNG THĂNG LONG 999.9 (Vàng BTMC)":
                print(gold)
                message = "🌎 Giá thế giới: " +gold["@pt_"+str(n)] + "VND\n\nVàng bảo tín minh châu:\nGiá mua: "+gold["@pb_"+str(n)]+" VND\nGía bán: "+gold["@ps_"+str(n)]+" VND\n\n"
                break
            else:
                n+=1
                continue
        d_vang = xmltodict.parse(res_sjc.content)
        l_vang_city = d_vang['root']['ratelist']['city']
        for vang in l_vang_city:
            if vang['@name'] == "Hà Nội":
                message2 = vang["item"]["@type"]+":\nGiá mua: "+vang["item"]["@buy"]+".000 VND\nGía bán: "+vang["item"]["@sell"]+".000 VND"
        post_tele(chat_id,message+message2)
    else:
        error = "StatusCode: " + str(res_btmc.status_code) +" "+ res_btmc.text
        error2 = "StatusCode: " + str(res_sjc.status_code) +" "+ res_sjc.text
        post_error(error+error2,chat_id)

def send_xsmb(chat_id):
    res = requests.get(link_xsmb)
    if res.status_code == requests.codes.ok:
        response = res.json()
        kq = response['results']
        date = response['time']
        dayname = get_day_name(date)
        head="Kết quả xổ số miền bắc *("+ dayname +" "+date+"*)\n\n"
        mess=''
        for k,v in kq.items():
            s = ' - '.join(str(x) for x in v)
            mess += k +": "+ s + "\n"
        message = head+mess+"\nĐề: *"+kq["ĐB"][0][-2:]+"*"
        post_tele(chat_id,message)
    else:
        error = "StatusCode: " + res.status_code +" "+ res.text
        post_error(error,chat_id)

def lambda_handler(event, context):
    logger.info(json.dumps(event))
    
    try:
        body=json.loads(event['body'])
        print("duoi day la body")
        logger.info(json.dumps(body))

        if "edited_message" in body:
            chat_id = body['edited_message']['chat']['id']
            send_text("edited_mess",chat_id)
            return {"statusCode": 200}
        else:
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
            get_n_send_quote(chat_id)
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
        elif user_text in ["/country","/quocgia"]:
            send_country(chat_id)
            return {"statusCode": 200}
        elif "/news" in user_text:
            send_news(chat_id,user_text)
            return {"statusCode": 200}
            return {"statusCode": 200}
        elif "/weather" in user_text:
            send_weather(chat_id)
            return {"statusCode": 200}
        elif "/gold" in user_text:
            send_goldprice(chat_id)
            return {"statusCode": 200}            
        elif "/xsmb" in user_text:
            send_xsmb(chat_id)
            return {"statusCode": 200}            
        else:
            send_text(user_text,chat_id)
            return {"statusCode": 200}
    except Exception:
        traceback.print_exc()
        error = traceback.format_exc()
        # send_text(error,chat_id)
        print("loi day")
        print(error)
        return {"statusCode": 200}