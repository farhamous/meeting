from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram.bot import Bot
from telegram.update import Update
import telegram
import time
from meeting.db import User, session
import json
import os
import jdatetime

from meeting import province, cities

GENDER, STATE, FIRST_NAME, LAST_NAME, MOBILE, PROVINCE, CITY, PICTURE, COMMENT = range(9)
back_button = 'برگشت'
menu_button = '/start'
agree_button = 'قبول'
cancel_button = '/cancel'
finish_msg = 'پایان'
agree_msg = 'شروع ثبت نام'
users = {}

def next_step(bot, update, step, user_data):
    i = update.message.chat_id
    reply_keyboard = []

    if step == GENDER:
        reply_keyboard = [['دختر', 'پسر']]
        text = "جنسیت؟"

    if step == STATE:
        reply_keyboard = [
            ['مجرد', 'متاهل'],
            ['متارکه', 'همسر متوفا'],
        ]
        text = "وضعیت"

    if step == FIRST_NAME:
        text='نام کوچک شما؟'

    elif step == LAST_NAME:
        text='نام خانوادگی شما؟'

    elif step == MOBILE:

        contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)

        reply_keyboard = [[contact_keyboard]]
        text='شماره موبایل خود را وارد کنید یا شماره خود را با زدن دکمه پایین ارسال کنید'

    elif step == PROVINCE:
        reply_keyboard = [[i] for i in province]
        text='استان محل زندگی خود را وارد کنید'

    elif step == CITY:
        user = user_data['db_user']
        reply_keyboard = [[i] for i in cities[user.province]]
        text = 'شهر محل سکونت خود را مشخص کنید'

    elif step == PICTURE:
        text = 'تصویر خود را بارگذاری کنید'

    elif step == COMMENT:
        text='توضیحات اضافی خود را وارد کنید'

    reply_keyboard.append([menu_button, cancel_button])

    update.message.reply_text(text=text, reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return step


def register_start(bot, update, user_data):
    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    i = update.message.chat_id
    if user:
        user.last_update = int(time.time())
        session.commit()
        update.message.reply_text( text='شما قبلا در این سامانه ثبت نام کرده اید ادامه این فرآیند پروفایل شما را به روز می کند در صورت انصراف می توانید /cancel را بزنید')

    else:
        user = User()
        user.chat_id = i
        user.telegram_id = telegram_user.id
        user.username = telegram_user.username if telegram_user.username else ''
        user.first_name = telegram_user.first_name if telegram_user.first_name else ''
        user.last_name = telegram_user.last_name if telegram_user.last_name else ''
        user.register_date = int(time.time())
        user.last_update = int(time.time())
        session.add(user)
        session.commit()

    user_data['db_user'] = user

    return next_step(bot, update, GENDER, user_data=user_data)



def register_gender(bot, update, user_data):
    user = user_data['db_user']
    user.gender = update.message.text
    session.commit()
    return next_step(bot, update, STATE, user_data=user_data)

def register_state(bot, update, user_data):
    user = user_data['db_user']
    user.state = update.message.text
    session.commit()
    return next_step(bot, update, FIRST_NAME, user_data=user_data)

def register_first_name(bot, update, user_data):

    user = user_data['db_user']
    user.first_name = update.message.text
    session.commit()
    return next_step(bot, update, LAST_NAME, user_data=user_data)

def register_last_name(bot, update, user_data):

    user = user_data['db_user']
    user.last_name = update.message.text
    session.commit()
    return next_step(bot, update, MOBILE, user_data=user_data)

def register_mobile(bot, update, user_data):

    user = user_data['db_user']
    if update.message.contact:
        user.mobile = update.message.contact.phone_number
    else:
        user.mobile = update.message.text
    session.commit()
    return next_step(bot, update, PROVINCE, user_data=user_data)

def register_province(bot, update, user_data):
    user = user_data['db_user']
    user.province = update.message.text
    session.commit()

    return next_step(bot, update, CITY, user_data=user_data)

def register_city(bot, update, user_data):
    user = user_data['db_user']
    user.city = update.message.text
    session.commit()
    return next_step(bot,update, PICTURE, user_data=user_data)


def register_picture(bot, update, user_data):
    i = update.message.chat_id
    user = user_data['db_user']
    if update.message.photo:
        try:
            os.makedirs('picture')
        except:
            pass

        file_id = update.message.photo[1].file_id
        newFile = bot.get_file(file_id)
        tmp = os.path.join('picture', '{}'.format(i))
        newFile.download(tmp)


    return next_step(bot, update, COMMENT, user_data=user_data)


def register_comment(bot, update, user_data):

    user = user_data['db_user']
    user.comment = update.message.text

    session.commit()
    update.message.reply_text(text=finish_msg)
    return ConversationHandler.END


def cancel(bot, update):

    update.message.reply_text( text='شما از ادامه منصرف شده اید')

    return ConversationHandler.END


handler = ConversationHandler(
    entry_points=[CommandHandler('register', register_start, pass_user_data=True)],
    allow_reentry=True,
    states={
        GENDER: [MessageHandler(Filters.text, register_gender, pass_user_data=True)],
        STATE: [MessageHandler(Filters.text, register_state, pass_user_data=True)],
        FIRST_NAME: [MessageHandler(Filters.text, register_first_name, pass_user_data=True)],
        LAST_NAME: [MessageHandler(Filters.text, register_last_name, pass_user_data=True)],
        MOBILE: [MessageHandler(Filters.text | Filters.contact, register_mobile, pass_user_data=True)],
        PROVINCE: [MessageHandler(Filters.text, register_province, pass_user_data=True)],
        CITY: [MessageHandler(Filters.text, register_city, pass_user_data=True)],
        PICTURE: [MessageHandler(Filters.text| Filters.photo, register_picture, pass_user_data=True)],
        COMMENT: [MessageHandler(Filters.text, register_comment, pass_user_data=True)]
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
