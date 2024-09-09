import time
import telebot
from telebot import types
import requests
import datetime
from selenium import webdriver
import bs4
from bs4 import Tag
from telebot.types import Message, CallbackQuery
from selenium.webdriver.common.keys import Keys

# Подключение к боту по его токену
bot = telebot.TeleBot('7035250317:AAEPaM6iCk-9XIblyGnwT1ivt33QMxT5goc', 'Markdown')

# Стейт для хранения введёных юзером данных 
user_states = {}

# Раздел с переменными для отправки пользователю
now = datetime.date.today()
img_ID = 'https://disk.yandex.ru/i/HasrGr0KwUOWEw'
img_options = 'https://disk.yandex.ru/i/AHLgCMkaGK4gWg'
img_code = 'https://disk.yandex.ru/i/Oyri6wqOqrtcSQ'
img_profil = 'https://disk.yandex.ru/i/-psAJNSikLhyUA'
media_group_ID = [types.InputMediaPhoto(img_options), types.InputMediaPhoto(img_code)]

ID_box = '/html/body/div[1]/div[1]/div[2]/div[1]/div[3]/div[2]/input'
Code_box_1 = '/html/body/div[1]/div[1]/div[2]/div[1]/div[4]/div[2]/input'
Button_Log_In = '/html/body/div[1]/div[1]/div[2]/div[1]/div[5]'

user_notification = '/html/body/div[2]/div/div/div/div/div/span[2]'

Code_box_2 = '//*[@id="root"]/div/div[2]/div/div[4]/div[2]/input'
Button_code = '//*[@id="root"]/div/div[2]/div/div[5]'

Value = True

# Обработка команды старт
@bot.message_handler(commands=['start']) 
def main(message:Message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    code_button = types.InlineKeyboardButton("Активировать код", callback_data='active_commands')
    info_button = types.InlineKeyboardButton("Получить информацию", callback_data='info')
    list_codes_button = types.InlineKeyboardButton("Получить список кодов", callback_data='code_list')
    get_credentionals = types.InlineKeyboardButton("Где получить данные", callback_data='where_get_credentionals')
    markup.add(code_button, info_button, list_codes_button, get_credentionals)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}. Готовы начать?'.format(message.from_user), reply_markup=markup)


# Активация кодов
@bot.callback_query_handler(func=lambda call: call.data == "active_commands")
def activate_code(query:CallbackQuery):
    bot.send_message(query.message.chat.id, text="Для активации кодов необходимо указать ваши данные для входа")           
    message = bot.send_message(query.message.chat.id, text='Укажите ID своего аккаута:')
    bot.register_next_step_handler(message, await_user_id)

# Функции для получения введённых пользователем данных и их отображения
def await_user_id(message:Message):
    user_states.update({'ID-пользователя':message.text})
    message = bot.send_message(message.chat.id, text='Введите код:')
    bot.register_next_step_handler(message, await_user_code)

def await_user_code(message:Message):
   user_states.update({'Код подтверждения': message.text})
   resultStr = '*Данные для входа* \n'
   for user_cred in user_states:
        resultStr += f'{user_cred}: {user_states[user_cred]} \n'
   bot.send_message(message.chat.id, text=resultStr)
   
   gcodeArr, _ = parse_gift_keys()

   global browser
   url = 'https://cdkey.lilith.com/afk-global'
   browser = webdriver.Chrome()
   browser.get(url)

   browser.find_element(by='xpath', value=ID_box).send_keys(user_states.get('ID-пользователя'))
   browser.find_element(by='xpath', value=Code_box_1).send_keys(user_states.get('Код подтверждения'))
   browser.find_element(by='xpath', value=Button_Log_In).click()

   time.sleep(1)
   user_message = browser.find_element(by='xpath', value=user_notification)


   if user_message.get_attribute('innerHTML').splitlines()[0] == 'Login Successful':
        code_input = browser.find_element(by='xpath', value=Code_box_2)
        check_code_btn =  browser.find_element(by='xpath', value=Button_code)
        for key in gcodeArr:
            code_input.send_keys(key)
            check_code_btn.click()
            code_input.click()
            code_input.send_keys(Keys.CONTROL + "a")
            code_input.send_keys(Keys.DELETE)
            continue
        
        bot.send_message(message.chat.id, text='Награды направлены на почту')
        browser.close()
   else:
        bot.send_message(message.chat.id, text='Ошибка авторизации...')
        browser.close()   


# Получение информации
@bot.callback_query_handler(func=lambda call: call.data == "info")
def get_info(query:CallbackQuery):
    bot.send_message(query.message.chat.id, text='Инфа жоская')

# Где искать данные для входа
@bot.callback_query_handler(func=lambda call: call.data == "where_get_credentionals")
def how_get_credentionals(query:CallbackQuery):
    bot.send_photo(query.message.chat.id, img_profil, caption='Заходим в профиль игрока')
    bot.send_photo(query.message.chat.id, img_ID, caption='ID аккаунта(не меняется)')
    bot.send_photo(query.message.chat.id, img_options, caption='Узнать код подтверждения можно в настройках')
    bot.send_photo(query.message.chat.id, img_code, caption='При нажатии на одноименную кнопку вам высветится временный код подтверждения')

# Получение списка кодов
@bot.callback_query_handler(func=lambda call: call.data == "code_list")
def get_code_list(query:CallbackQuery): 
    bot.send_message(query.message.chat.id, text= f"Список актуальных кодов на, {now}")

    codeArr, revardArr = parse_gift_keys()

    if len(codeArr) == len(revardArr):
        resultDict = dict(zip(codeArr, revardArr))

        resultParseStr = ''
        for key in resultDict: 
            resultParseStr += f'`{key}` | *{resultDict[key]}* \n'

        if resultParseStr != '':
                bot.send_message(query.message.chat.id, text=resultParseStr)
    else:
        bot.send_message(query.message.chat.id, text='Упс... Произошла ошибка')



def parse_gift_keys():
    result = requests.get('https://guidesgame.ru/publ/guides/afk_arena/afk_arena_kody_vozmeshhenija/316-1-0-1502')
    parser = bs4.BeautifulSoup(result.content, 'lxml')
    gCodeContent = parser.find_all('span', {'class':'gcode'})
    revardContent = parser.find_all('td', {'class':'unselectable'})

    gcodeArr = []
    for gcode in gCodeContent:
        gcode:Tag
        gcodeArr.append(gcode.contents[0])

    revardArr = []
    for revard in revardContent:
        revard:Tag
        revardArr.append(revard.contents[0])

    return gcodeArr, revardArr

bot.polling(none_stop=True)
