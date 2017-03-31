from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram.bot import Bot
from telegram.update import Update
import telegram
import time
from meeting.db import User, session
import json
import os
import jdatetime

with open('Province.json') as f:
    tmp = json.load(f)
    province = [i['name'].strip() for i in tmp]
    cities = {i['name']: [j['name'] for j in i['Cities']] for i in tmp}

GENDER, FIRST_NAME, LAST_NAME, MOBILE, PROVINCE, CITY, PICTURE, COMMENT = range(8)
back_button = 'برگشت'
menu_button = '/start'
agree_button = 'قبول'
cancel_button = '/cancel'
finish_msg = 'پایان'
agree_msg = 'شروع ثبت نام'
users = {}

def next_step(bot, update, step):
    i = update.message.chat_id
    reply_keyboard = []

    if step == GENDER:
        text = "جنسیت؟"

    if step == FIRST_NAME:
        text='نام کوچک شما؟'

    elif step == LAST_NAME:
        text='نام خانوادگی شما؟'

    elif step == MOBILE:

        contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)

        reply_keyboard = [[contact_keyboard]]
        text='شماره موبایل شما؟ یا شماره خود را با زدن دکمه پایین ارسال کنید'

    elif step == PROVINCE:
        reply_keyboard = [[i] for i in province]
        text='استان محل زندگی خود را وارد کنید'

    elif step == CITY:
        reply_keyboard = [[i] for i in cities[users[i].province]]
        text = 'شهر محل سکونت خود را مشخص کنید'

    elif step == PICTURE:
        text = 'تصویر خود را بارگذاری کنید'

    elif step == COMMENT:
        text='توضیحات اضافی خود را وارد کنید'

    reply_keyboard.append([menu_button, cancel_button])
    bot.sendMessage(i,text=text, reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return step


def register_start(bot, update):
    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    i = update.message.chat_id
    if user:
        bot.sendMessage(i, text='شما قبلا در این سامانه ثبت نام کرده اید ادامه این فرآیند پروفایل شما را به روز می کند در صورت انصراف می توانید /cancel را بزنید')
        users[i] = user
    else:
        user = User()
        user.chat_id = i
        user.telegram_id = telegram_user.id
        user.username = telegram_user.username if telegram_user.username else ''
        user.first_name = telegram_user.first_name if telegram_user.first_name else ''
        user.last_name = telegram_user.last_name if telegram_user.last_name else ''
        users[i] = user
        session.add(user)
        session.commit()

    return next_step(bot, update, FIRST_NAME)



def register_first_name(bot, update):

    i = update.message.chat_id
    users[i].first_name = update.message.text
    session.commit()
    return next_step(bot, update, LAST_NAME)

def register_last_name(bot, update):

    i = update.message.chat_id
    users[i].last_name = update.message.text
    session.commit()
    return next_step(bot, update, MOBILE)

def register_mobile(bot, update):

    i = update.message.chat_id
    if update.message.contact:
        users[i].mobile = update.message.contact.phone_number
    else:
        users[i].mobile = update.message.text
    session.commit()
    return next_step(bot, update, PROVINCE)

def register_province(bot, update):

    i = update.message.chat_id
    users[i].province = update.message.text
    session.commit()

    return next_step(bot, update, CITY)

def register_city(bot, update):

    i = update.message.chat_id
    users[i].city = update.message.text
    session.commit()
    return next_step(bot,update, PICTURE)


def register_picture(bot, update):
    i = update.message.chat_id
    if update.message.photo:
        try:
            os.makedirs('picture')
        except:
            pass

        file_id = update.message.photo[1].file_id
        newFile = bot.get_file(file_id)
        tmp = os.path.join('picture', '{}'.format(i))
        newFile.download(tmp)


    return next_step(bot, update, COMMENT)


def register_comment(bot, update):
    i = update.message.chat_id
    if update.message.text == back_button:
        return next_step(bot, update, CITY)
    else:
        users[i].comment = update.message.text

    session.add(users[i])
    session.commit()
    bot.sendMessage(i,text=finish_msg)
    return ConversationHandler.END


def cancel(bot, update):
    i = update.message.chat_id
    user = update.message.from_user
    bot.sendMessage(i, text='شما از ادامه منصرف شده اید')

    return ConversationHandler.END


handler = ConversationHandler(
    entry_points=[CommandHandler('register', register_start)],
    allow_reentry=True,
    states={
        FIRST_NAME: [MessageHandler(Filters.text, register_first_name)],
        LAST_NAME: [MessageHandler(Filters.text, register_last_name)],
        MOBILE: [MessageHandler(Filters.text | Filters.contact, register_mobile)],
        PROVINCE: [MessageHandler(Filters.text, register_province)],
        CITY: [MessageHandler(Filters.text, register_city)],
        PICTURE: [MessageHandler(Filters.text| Filters.photo, register_picture)],
        COMMENT: [MessageHandler(Filters.text, register_comment)]
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
