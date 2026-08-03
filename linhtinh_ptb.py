"""
Linhtinh bot — python-telegram-bot version, chạy trên AWS Lambda.
Entry point: lambda_handler
"""

import json, random, logging, traceback, io, re, ipaddress, feedparser, requests
from datetime import datetime
from googletrans import Translator
from bs4 import BeautifulSoup
from tabulate import tabulate

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from var_file import *
from gold_visualizer import GoldScraper, visualize_gold_sjc
from petrol_scraper import scrape_petrol_prices
from petrol_visualizer import visualize_petrol_prices

logger = logging.getLogger()
logger.setLevel("INFO")

# ── Helpers (giữ nguyên logic từ linhtinh_aws_lambda.py) ─────────────────────

def translate_vn(text):
    try:
        return Translator().translate(text, dest='vi').text
    except Exception:
        return text

def dict_to_text(d):
    return ''.join(f"{k}: {v}\n" for k, v in d.items())

def validate_ip_address(ip):
    pattern = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}(\/\d{1,2})?$'
    return bool(re.match(pattern, ip))

def get_subnet(subnet):
    res = requests.get(link_subnet+subnet)
    if res.status_code == requests.codes.ok:
        content = res.json()
        return content["address"]
    else:
        error = "StatusCode: " + str(res.status_code) +" "+ res.text
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

def get_weather_text():
    try:
        w = requests.get(link_weather).json()
        wid = w["weather"][0]["id"]
        temp = int(w["main"]["temp"] - 273.15)
        feels = int(w["main"]["feels_like"] - 273.15)
        desc = w["weather"][0]["description"]
        humidity = w["main"]["humidity"]
        text = f"Thời tiết Hà Nội\nNhiệt độ: *{temp}°C* (cảm giác {feels}°C)\nĐộ ẩm: {humidity}%\nTrời: {desc}"
    except Exception as e:
        text = f"❌ Lỗi thời tiết: {e}"
    try:
        air = requests.get(link_air).json()
        aqi = air["data"]["current"]["pollution"]["aqius"]
        text += f"\nAQI: *{aqi}*"
    except Exception as e:
        text += f"\n❌ Lỗi AQI: {e}"
    return text

def get_news_text(num, link):
    feed = feedparser.parse(link)
    entries = random.sample(feed["entries"], min(num, len(feed["entries"])))
    return "\n\n".join(f"{e['title']}\n{e['link']}" for e in entries)

def info_meals(d):
    m, meas = {}, {}
    for k, v in d.items():
        if v in ['', ' ', None]: continue
        if 'strIngredient' in k: m[k] = v
        elif 'strMeasure' in k: meas[k.replace('strMeasure', 'strIngredient')] = v
    nguyen_lieu = dict_to_text({m.get(k, k): v for k, v in meas.items()})
    text = f'Tên: {d["strMeal"]}\nLoại: {d["strCategory"]}\nKhu vực: {d["strArea"]}\n\nNguyên liệu:\n{translate_vn(nguyen_lieu)}\nYoutube: {d["strYoutube"]}'
    guide = f'*Hướng dẫn:* {translate_vn(d["strInstructions"])}\n\nNguồn: {d["strSource"]}'
    return d["strMealThumb"], text, guide

def info_drinks(d):
    m, meas = {}, {}
    for k, v in d.items():
        if v in ['', ' ', None]: continue
        if 'strIngredient' in k: m[k] = v
        elif 'strMeasure' in k: meas[k.replace('strMeasure', 'strIngredient')] = v
    nguyen_lieu = dict_to_text({m.get(k, k): v for k, v in meas.items()})
    text = f'Tên: {d["strDrink"]}\nLoại: {d["strCategory"]}\nAlcoholic: {d["strAlcoholic"]}\nCốc: {d["strGlass"]}\n\nNguyên liệu:\n{translate_vn(nguyen_lieu)}'
    guide = f'*Hướng dẫn:* {translate_vn(d["strInstructions"])}'
    return d["strDrinkThumb"], text, guide

def get_country_text(c):
    curr_ = list(c['currencies'].keys())[0]
    curr_info = c['currencies'][curr_]
    try: tien = f"Tiền: {curr_} ({curr_info['name']}), ký hiệu: {curr_info['symbol']}"
    except: tien = f"Tiền: {curr_} ({curr_info['name']})"
    try: border = ", ".join(c["borders"])
    except: border = "khum"
    return f'''Tên: {c['name']['common']} {c['flag']}
Tên chính thức: {c['name']['official']}
Khu vực: {c['region']}, {c['subregion']}
Thủ đô: {', '.join(c['capital'])}
Ngôn ngữ: {', '.join(c['languages'].values())}
Múi giờ: {', '.join(c['timezones'])}
Biên giới: {border}
Diện tích: {c['area']} km2 | Dân số: {c['population']}
{tien}
Map: {c['maps']['googleMaps']}
Quốc kỳ: {c['flags']['png']}'''

# ── PTB Command Handlers ──────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(modau)

async def cmd_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get(link_quote)
        res.raise_for_status()
        q = res.json()["quote"]
        await update.message.reply_text(f'_"{q["body"]}"_\n\n*{q["author"]}*', parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"API lỗi: {e}")

async def cmd_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = requests.get(link_fact, headers={'X-Api-Key': API_NINJA})
    if res.ok:
        fact = res.json()[0]['fact']
        await update.message.reply_text(fact + "\n\n" + translate_vn(fact))
    else:
        await update.message.reply_text(f"API lỗi: {res.status_code}")

async def cmd_uselessfact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = requests.get(link_uselessfact)
    if res.ok:
        text = res.json()["text"]
        await update.message.reply_text(text + "\n\n" + translate_vn(text))
    else:
        await update.message.reply_text(f"API lỗi: {res.status_code}")

async def cmd_meal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = requests.get(link_meals)
    if res.ok:
        img, text, guide = info_meals(res.json()["meals"][0])
        await context.bot.send_photo(update.effective_chat.id, photo=img, caption=text)
        await update.message.reply_text(guide, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"API lỗi: {res.status_code}")


async def cmd_cocktail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = requests.get(link_cocktail)
    if res.ok:
        img, text, guide = info_drinks(res.json()["drinks"][0])
        await context.bot.send_photo(update.effective_chat.id, photo=img, caption=text)
        await update.message.reply_text(guide, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"API lỗi: {res.status_code}")

async def cmd_an_trua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mon = random.choice(l_antrua)
    keyboard = [[InlineKeyboardButton("🔄 Gợi ý khác", callback_data="antrua_refresh")]]
    await update.message.reply_text(mon, reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_antrua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(random.choice(l_antrua), reply_markup=InlineKeyboardMarkup([[
        InlineKeyboardButton("🔄 Gợi ý khác", callback_data="antrua_refresh")
    ]]))

async def cmd_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = requests.get(link_country)
    if res.ok:
        await update.message.reply_text(get_country_text(random.choice(res.json())))
    else:
        await update.message.reply_text(f"API lỗi: {res.status_code}")

async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num = int(context.args[0]) if context.args else 1
        if not 1 <= num <= 10:
            await update.message.reply_text("Nhập số từ 1-10 thôi nha")
            return
    except ValueError:
        await update.message.reply_text("Nhập số từ 1-10 thôi nha")
        return
    await update.message.reply_text(get_news_text(num, link_vnexpress_new))

async def cmd_aws(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num = int(context.args[0]) if context.args else 1
        if not 1 <= num <= 10:
            await update.message.reply_text("Nhập số từ 1-10 thôi nha")
            return
    except ValueError:
        await update.message.reply_text("Nhập số từ 1-10 thôi nha")
        return
    await update.message.reply_text(get_news_text(num, link_aws_new))

async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_weather_text(), parse_mode="Markdown")

async def cmd_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get(link_vne_finance)
        res.raise_for_status()
        data = res.json()['data']
        update_time = datetime.strptime(data['updated_at'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M')
        gold = data['data']['gold']
        rows = []
        for k, v in gold['new'].items():
            o = gold['old'][k]
            db = round(v['buy'] - o['buy'], 2); ds = round(v['sell'] - o['sell'], 2)
            label = v['label'].replace("Vàng nhẫn SJC 99,99  1 chỉ, 2 chỉ, 5 chỉ", "Vàng nhẫn SJC 99,99")
            if label == "Giá vàng thế giới":
                rows.append([label, f"{round(v['buy'])}$ {'+' if db>0 else ''}{db}$", f"{round(v['sell'])}$ {'+' if ds>0 else ''}{ds}$"])
            else:
                rows.append([label, f"{v['buy']/1000} {'+' if db>0 else ''}{db}K", f"{v['sell']/1000} {'+' if ds>0 else ''}{ds}K"])
        table = tabulate(rows, headers=["Loại", "Mua", "Bán"], tablefmt="simple")
        await update.message.reply_text(f'<pre>{table}</pre>\ncập nhật: {update_time}\n\nBiểu đồ: /gold_chart', parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Lỗi giá vàng: {e}")

async def cmd_gold_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raw = GoldScraper().fetch_data()
        processed = GoldScraper().process_data(raw)
        buf = visualize_gold_sjc(processed)
        if buf:
            await context.bot.send_photo(update.effective_chat.id, photo=buf)
    except Exception as e:
        await update.message.reply_text(f"Lỗi biểu đồ vàng: {e}")

async def cmd_xang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = scrape_petrol_prices()
    if data['status'] == 'success':
        prices = data['retail_prices']
        time_update = data.get('date_label') or datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M')
        rows = [["Mặt hàng", "Giá (đ)", "Thay đổi"]]
        for item in prices:
            rows.append([item['name'], f"{item['price']:,}".replace(',', '.'), item['change']])
        table = tabulate(rows, headers="firstrow", tablefmt="simple", disable_numparse=True)
        await update.message.reply_text(f'<pre>{table}</pre>\ncập nhật: {time_update}\n\nBiểu đồ: /xang_chart', parse_mode="HTML")
    else:
        await update.message.reply_text(f"Lỗi giá xăng: {data.get('message')}")

async def cmd_xang_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        buf = visualize_petrol_prices()
        if buf:
            await context.bot.send_photo(update.effective_chat.id, photo=buf)
        else:
            await update.message.reply_text("Không có dữ liệu biểu đồ xăng.")
    except Exception as e:
        await update.message.reply_text(f"Lỗi biểu đồ xăng: {e}")

async def cmd_xsmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date = context.args[0] if context.args else None
        url = f"{link_xsmb}?date={date}" if date else link_xsmb
        res = requests.get(url)
        res.raise_for_status()
        kq = res.json()['results']
        display_date = date or datetime.now().strftime('%d-%m-%Y')
        mess = f"Kết quả XSMB *({display_date})*\n\n"
        for k, v in kq.items():
            mess += k + ": " + (' - '.join(str(x) for x in v) if v else 'Chưa có') + "\n"
        db = kq.get("Đặc biệt", [])
        if db: mess += f"\nĐề: *{db[0][-2:]}*"
        await update.message.reply_text(mess, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"XSMB lỗi: {e}")

async def cmd_tygia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get(link_vne_finance)
        res.raise_for_status()
        ex = res.json()['data']['data']['ex_rate']
        currencies = [('usd','Đô Mỹ'),('eur','Euro'),('gbp','Bảng Anh'),('jpy','Yên Nhật'),
                      ('krw','Won Hàn'),('cny','Tệ TQ'),('sgd','Đô Sing'),('thb','Bạt Thái'),
                      ('aud','Đô Úc'),('cad','Đô Canada')]
        rows = [[f"{c.upper()} ({n})", ex[c]['cash'], ex[c]['transfer'], ex[c]['sell']] for c, n in currencies]
        update_time = datetime.fromisoformat(ex['usd']['date_label']).strftime('%Y-%m-%d %H:%M')
        table = tabulate(rows, headers=['Ngoại tệ','TM','CK','Bán'], tablefmt='simple', disable_numparse=True)
        await update.message.reply_text(f'<pre>{table}</pre>\ncập nhật: {update_time}', parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Lỗi tỷ giá: {e}")

async def cmd_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = requests.get(link_transfermark, headers=header)
    if res.ok:
        soup = BeautifulSoup(res.content, "html.parser")
        table = soup.find("table", class_="items")
        if table:
            rows = []
            for row in table.find_all("tr"):
                cells = [c.get_text(strip=True) for c in row.find_all(["td","th"])]
                if len(cells) > 3:
                    rows.append([cells[0], cells[3], cells[5], cells[8]])
            rows.pop(0)
            table_str = tabulate(rows, headers=["#","Player","Age","Value"], tablefmt="simple")
            await update.message.reply_text(f'```\n{table_str}```', parse_mode="Markdown")
        else:
            await update.message.reply_text("Không tìm thấy dữ liệu.")
    else:
        await update.message.reply_text(f"Lỗi: {res.status_code}")

# ── Non-command handlers ──────────────────────────────────────────────────────

async def handle_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(valid_ip_or_cidr(update.message.text))

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.post(link_shorten, data={"url": update.message.text})
        r.raise_for_status()
        await update.message.reply_text(r.json()['result_url'])
    except Exception as e:
        await update.message.reply_text(f"Lỗi rút gọn link: {e}")

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("thả sticker làm gì hử :)))\nGõ /help nha")
    sticker = random.choice(meme_shiba)
    await context.bot.send_sticker(update.effective_chat.id, sticker=sticker)

async def handle_edited(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("Đừng sửa tin nhắn, vì nó ko có ý nghĩa gì")

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("hổng hiểu gì hết trơn :)))\nGõ /help hoặc /start nha")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_chat:
        await context.bot.send_message(update.effective_chat.id, f"Có lỗi xảy ra: {context.error}")

# ── App builder (reuse across Lambda invocations) ─────────────────────────────

def build_app():
    app = Application.builder().token(TOKEN).updater(None).build()

    app.add_handler(CommandHandler(["start", "help"], cmd_start))
    app.add_handler(CommandHandler("quote", cmd_quote))
    app.add_handler(CommandHandler("fact", cmd_fact))
    app.add_handler(CommandHandler("uselessfact", cmd_uselessfact))
    app.add_handler(CommandHandler("meal", cmd_meal))
    app.add_handler(CommandHandler("cocktail", cmd_cocktail))
    app.add_handler(CommandHandler(["an_trua", "antrua", "trua_nay_an_gi"], cmd_an_trua))
    app.add_handler(CommandHandler(["country", "quocgia"], cmd_country))
    app.add_handler(CommandHandler("news", cmd_news))
    app.add_handler(CommandHandler("aws", cmd_aws))
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler(["gold", "vang", "gia_vang"], cmd_gold))
    app.add_handler(CommandHandler("gold_chart", cmd_gold_chart))
    app.add_handler(CommandHandler(["xang", "xang_dau", "petrol"], cmd_xang))
    app.add_handler(CommandHandler("xang_chart", cmd_xang_chart))
    app.add_handler(CommandHandler("xsmb", cmd_xsmb))
    app.add_handler(CommandHandler(["tygia", "ty_gia", "exchange"], cmd_tygia))
    app.add_handler(CommandHandler("football_price", cmd_football))

    app.add_handler(CallbackQueryHandler(callback_antrua, pattern="^antrua_refresh$"))

    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_edited))
    app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    app.add_handler(MessageHandler(filters.Entity("url"), handle_url))
    app.add_handler(MessageHandler(filters.Regex(r'^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$'), handle_ip))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))
    app.add_handler(MessageHandler(filters.COMMAND, handle_unknown))

    app.add_error_handler(error_handler)
    return app

ptb_app = build_app()

# ── Lambda handler ────────────────────────────────────────────────────────────

async def _set_commands():
    await ptb_app.bot.set_my_commands([
        BotCommand("quote",         "Câu quote truyền cảm hứng"),
        BotCommand("fact",          "Sự thật thú vị"),
        BotCommand("uselessfact",   "Sự thật vô tri"),
        BotCommand("meal",          "Gợi ý món ăn + công thức"),
        BotCommand("cocktail",      "Công thức pha chế cocktail"),
        BotCommand("an_trua",       "Gợi ý món ăn trưa"),
        BotCommand("country",       "Thông tin quốc gia ngẫu nhiên"),
        BotCommand("news",          "Tin tức VnExpress (vd: /news 3)"),
        BotCommand("aws",           "Tin tức AWS (vd: /aws 2)"),
        BotCommand("weather",       "Thời tiết + AQI Hà Nội"),
        BotCommand("gold",          "Giá vàng mới nhất"),
        BotCommand("gold_chart",    "Biểu đồ giá vàng"),
        BotCommand("xang",          "Giá xăng dầu mới nhất"),
        BotCommand("xang_chart",    "Biểu đồ giá xăng"),
        BotCommand("xsmb",          "Kết quả xổ số miền Bắc"),
        BotCommand("tygia",         "Tỷ giá ngoại tệ so với VND"),
        BotCommand("football_price","Giá trị cầu thủ bóng đá"),
        BotCommand("help",          "Xem danh sách lệnh"),
    ])

_commands_set = False

def lambda_handler(event, context):
    import asyncio
    global _commands_set
    try:
        body = json.loads(event['body'])
        logger.info(json.dumps(body))

        async def process():
            global _commands_set
            async with ptb_app:
                if not _commands_set:
                    await _set_commands()
                    _commands_set = True
                await ptb_app.process_update(Update.de_json(body, ptb_app.bot))

        asyncio.get_event_loop().run_until_complete(process())
    except Exception:
        logger.error(traceback.format_exc())
    return {"statusCode": 200}


# ── Local polling (python3 linhtinh_ptb.py) ───────────────────────────────────

if __name__ == "__main__":
    import asyncio

    async def run_polling():
        async with ptb_app:
            await _set_commands()
            await ptb_app.updater.start_polling()
            await ptb_app.start()
            print("Bot đang chạy... Ctrl+C để dừng")
            await ptb_app.updater.idle()

    # Rebuild app with updater for polling
    from telegram.ext import Application
    poll_app = Application.builder().token(TOKEN).build()
    # copy handlers
    for group, handlers in ptb_app.handlers.items():
        for h in handlers:
            poll_app.add_handler(h, group)
    poll_app.add_error_handler(error_handler)

    async def main():
        async with poll_app:
            await poll_app.bot.set_my_commands([
                BotCommand("quote","Câu quote"), BotCommand("fact","Sự thật thú vị"),
                BotCommand("meal","Gợi ý món ăn"), BotCommand("an_trua","Ăn trưa gì"),
                BotCommand("news","Tin VnExpress"), BotCommand("aws","Tin AWS"),
                BotCommand("weather","Thời tiết HN"), BotCommand("gold","Giá vàng"),
                BotCommand("xang","Giá xăng"), BotCommand("xsmb","XSMB"),
                BotCommand("tygia","Tỷ giá"), BotCommand("help","Danh sách lệnh"),
            ])
            await poll_app.updater.start_polling()
            await poll_app.start()
            print("Bot đang chạy... Ctrl+C để dừng")
            await poll_app.updater.idle()

    asyncio.run(main())
