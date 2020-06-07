import generate_poems
import stats
import telebot
from telebot import types
import random
import os

#------ webhook libs
# import logging
# import ssl
# from aiohttp import web

# Get this token from a BotFather
TOKEN = 'YOUR_BOT_TOKEN'

#----- WEBHOOK CONFIG

# WEBHOOK_HOST = 'ip adress of host'
# WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
# WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
#
# WEBHOOK_SSL_CERT = '/path/to/cert.cert'  # Path to the ssl certificate
# WEBHOOK_SSL_PRIV = '/path/to/private.key'  # Path to the ssl private key
#
# WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
# WEBHOOK_URL_PATH = "/{}/".format(TOKEN)
#
# logger = telebot.logger
# telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(TOKEN)


#------- ALSO WEBHOOK CONFIG
# app = web.Application()


# async def handle(request):
#     if request.match_info.get('token') == bot.token:
#         request_body_dict = await request.json()
#         update = telebot.types.Update.de_json(request_body_dict)
#         bot.process_new_updates([update])
#         return web.Response()
#     else:
#         return web.Response(status=403)
#
#
# app.router.add_post('/{token}/', handle)


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*[types.KeyboardButton(choice) for choice in ['Да', 'Нет']])
    ans = bot.send_message(message.chat.id,
                           "Здравствуй! Сыграем в игру?",
                           reply_markup=keyboard)
    bot.register_next_step_handler(ans, startCheck)


def startCheck(message):
    if message.text == 'Да':
        acceptedStart(message)
    elif message.text == 'Нет':
        declinedStart(message)
    else:
        wrongInput(message)

# Gives an opportunity to view stats though
def declinedStart(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*[types.KeyboardButton(choice) for choice in ['Да', 'Нет']])
    ans = bot.send_message(message.chat.id, "Может быть, хотите посмотреть статистику?", reply_markup=keyboard)
    bot.register_next_step_handler(ans, viewStats)


def viewStats(message):
    if message.text == 'Да':
        getTotalStats(message, None)
    elif message.text == 'Нет':
        declined(message)
    else:
        wrongInput(message)


def declined(message):
    bot.send_message(message.chat.id, "Очень жаль, возвращайтесь!")
    askForStart(message)


def acceptedStart(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*[types.KeyboardButton(choice) for choice in ['Москва', 'Пермь', 'другой']])
    city = bot.send_message(message.chat.id, "Отлично! Для статистики, нам необходимо "
                                             "кое-что о Вас узнать! Из какого Вы города?", reply_markup=keyboard)
    bot.register_next_step_handler(city, getCity)

# Gets city name, if it is not 'Пермь' or 'Москва'
def getCity(city):
    if city.text == 'другой':
        getCityName(city)
    else:
        meta = {}
        getSex(city, meta)


def getCityName(message):
    # meta is a dict with personal info and personal stats
    meta = {}
    city = bot.send_message(message.chat.id, "Введите Ваш город")
    bot.register_next_step_handler(city, getSex, meta)


def getSex(message, meta):
    meta['city'] = message.text.lower()
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*[types.KeyboardButton(choice) for choice in ['М', 'Ж']])
    sex = bot.send_message(message.chat.id, "Какого Вы пола?", reply_markup=keyboard)
    bot.register_next_step_handler(sex, getAge, meta)


def getAge(sex, meta):
    meta['sex'] = sex.text
    age = bot.send_message(sex.chat.id, "Введите, пожалуйста, ваш возраст")
    bot.register_next_step_handler(age, givePoems, meta)


def givePoems(message, meta):
    if 'total' not in meta.keys():
        # handle error with wrong input
        try:
            meta['age'] = int(message.text)
        except:
            bot.send_message(message.chat.id, "Кажется, вы ввели не свой возраст...")
            askForStart(message)
            return None
        meta['total'] = 1
        meta['correct'] = 0
    else:
        meta['total'] += 1
    original, generated = generate_poems.getTwoPoems()
    poems_long = [original, generated]
    poems = []
    # cut poems to leave 8 lines
    for poem in poems_long:
        lines = poem.split('\n')
        if len(lines) > 12:
            lines = lines[:8]
        poem = '\n'.join(lines)
        poems.append(poem)
    order = [0, 1]
    # shuffle order randomly
    random.shuffle(order)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*[types.KeyboardButton(choice) for choice in ['1', '2']])
    ans = bot.send_message(message.chat.id,
                           "Какое из стихотворений - оригинальное стихотворение Хлебникова?\n\n 1) " + poems[order[0]] +
                           '\n\n2) ' + poems[order[1]],
                           reply_markup=keyboard)
    bot.register_next_step_handler(ans, giveFeedback, order, meta)


def giveFeedback(message, order, meta):
    reply_accuracy = False
    # check accuracy
    if int(message.text) - 1 == order.index(0):
        reply_accuracy = True
    if reply_accuracy:
        bot.send_message(message.chat.id, "Да, все верно!")
        meta['correct'] += 1
    else:
        bot.send_message(message.chat.id, "К сожалению, вы ошиблись:(")
    askForRetry(message, meta)


def askForRetry(message, meta):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*[types.KeyboardButton(choice) for choice in
                   ['Играть еще', 'Смотреть общую статистику (Статистика обновится, когда вы закончите играть)', 'Смотреть мою статистику', 'С меня хватит!']])
    ans = bot.send_message(message.chat.id, "Что теперь?", reply_markup=keyboard)
    bot.register_next_step_handler(ans, proceedRetry, meta)


def proceedRetry(message, meta):
    if message.text == 'Играть еще':
        givePoems(message, meta)
    elif message.text == 'Смотреть мою статистику':
        getMyStats(message, meta)
    elif message.text == 'Смотреть общую статистику (Статистика обновится, когда вы закончите играть)':
        getTotalStats(message, meta)
    else:
        bot.send_message(message.chat.id, 'Спасибо за игру! Возвращайтесь!')
        stats.putUser(meta)


def getMyStats(message, meta):
    bot.send_message(message.chat.id, f'Верных ответов: {meta["correct"]} \nВсего ответов: {meta["total"]}')
    askForRetry(message, meta)

@bot.message_handler(commands=['stats'])
def getTotalStats(message, meta):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*[types.KeyboardButton(choice) for choice in ['Где лучше знают Хлебникова?',
                                                               'Статистика угадываний по возрасту',
                                                               'Статистика угадываний по полу',
                                                               'Общая статистика'
                                                               ]])

    ans = bot.send_message(message.chat.id, "Выберите, что хотите посмотреть", reply_markup=keyboard)
    if not meta:
        ans = bot.send_message(message.chat.id, 'Для новой игры, введите /start')
    bot.register_next_step_handler(ans, chooseStats, meta)


def chooseStats(message, meta):
    if message.text == 'Где лучше знают Хлебникова?':
        stats.getCitiesStats()
        showStats(message, 'resources/img/city_stats.png', meta)
    elif message.text == 'Статистика угадываний по возрасту':
        stats.getAgeStats()
        showStats(message, 'resources/img/age_stats.png', meta)
    elif message.text == 'Статистика угадываний по полу':
        stats.getSexStats()
        showStats(message, 'resources/img/sex_stats.png', meta)
    elif message.text == 'Общая статистика':
        stats.getTotalStats()
        showStats(message, 'resources/img/total_stats.png', meta)
    else:
        if message.text == '/start':
            start(message)
        else:
            wrongInput(message)


def showStats(message, chart_name, meta):
    bot.send_message(message.chat.id, 'Статистика по графику:')
    with open(chart_name, 'rb') as pic:
        bot.send_photo(message.chat.id, pic)
    os.remove('./'+chart_name)
    if meta:
        askForRetry(message, meta)
    else:
        getTotalStats(message, meta)

def wrongInput(message):
    bot.send_message(message.chat.id, 'Я вас не понял.')
    askForStart(message)

def askForStart(message):
    bot.send_message(message.chat.id, 'Хотите сыграть? Нажмите /start')

bot.polling(none_stop=True)


#-------ALSO WEBHOOK CONFIG
# bot.remove_webhook()
#
# bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
#                 certificate=open(WEBHOOK_SSL_CERT, 'r'))
#
# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
#
# web.run_app(
#     app,
#     host=WEBHOOK_LISTEN,
#     port=WEBHOOK_PORT,
#     ssl_context=context,
# )
