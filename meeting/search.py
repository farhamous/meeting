from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import logging
from telegram.bot import Bot
from telegram.update import Update
import telegram
import time
from meeting.db import User, session
import json
import os
import jdatetime

from meeting import province, cities

menu_button = '/start'
cancel_button = '/cancel'
search_button = 'جستجو'

START, STATE, PROVINCE, CITY, DO = range(5)

def next_step(bot, update, step, user_data):
    i = update.message.chat_id
    reply_keyboard = [[search_button]]

    if step == STATE:
        reply_keyboard += [
            ['مجرد', 'متاهل'],
            ['متارکه', 'همسر متوفا'],
        ]
        text = "وضعیت"


    elif step == PROVINCE:
        reply_keyboard += [[i] for i in province]
        text='استان محل زندگی خود را وارد کنید'

    elif step == CITY:
        user = user_data['db_user']
        reply_keyboard += [[i] for i in cities[user_data['search_filter']['province']]]
        text = 'شهر محل سکونت خود را مشخص کنید'

    elif step == DO:
        reply_keyboard = []
        text = 'نتایج جستجو'

    reply_keyboard.append([menu_button, cancel_button])

    update.message.reply_text(text=text, reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return step



def search_start(bot, update, user_data):
    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    user_data['db_user'] = user
    i = update.message.chat_id
    # users[i] = user
    if not user:
        update.message.reply_text( text='شما در این سامانه ثبت نام نکرده اید. می توانید از طریق /register ثبت نام کرده و سپس به جستجو خود بپردازید')
        return ConversationHandler.END
    elif not user.city:
        update.message.reply_text( text='برای جستجو انتخاب شهر و استان الزامی است /register ثبت نام خود را تکمیل کرده و سپس به جستجو خود بپردازید')
        return ConversationHandler.END
    else:
        return next_step(bot, update, STATE, user_data=user_data)



def search_state(bot, update, user_data):
    if update.message.text == 'جستجو':
        return search_do(bot, update, user_data=user_data)
    user_data['search_filter']={}
    user_data['search_filter']['state'] = update.message.text

    return next_step(bot, update, PROVINCE, user_data=user_data)


def search_province(bot, update, user_data):
    if update.message.text == 'جستجو':
        return search_do(bot, update, user_data=user_data)

    user_data['search_filter']['province'] = update.message.text

    return next_step(bot, update, CITY, user_data=user_data)

def search_city(bot, update, user_data):
    print('in city')
    if update.message.text == 'جستجو':
        return search_do(bot, update, user_data=user_data)

    user_data['search_filter']['city'] = update.message.text
    return search_do(bot, update, user_data=user_data)


def search_do(bot, update, user_data):
    print("in search")
    user = user_data['db_user']
    search_filter = user_data.get('search_filter',{})
    if user.gender == 'دختر':
        search_filter['gender'] = 'پسر'
    elif user.gender == 'پسر':
        search_filter['gender'] = 'دختر'
    else:
        search_filter['gender'] = 'تعیین نشده'
    print(user.id, search_filter)
    users = session.query(User).filter_by(**search_filter).all()
    for user in users:
        # founded_users = [user.first_name for user in users]
        update.message.reply_text("""نام:{0}
        توضیحات:{1}""".format(user.first_name, user.comment))

    return ConversationHandler.END

def cancel(bot, update):
    i = update.message.chat_id
    user = update.message.from_user
    update.message.reply_text(text='شما از ادامه منصرف شده اید')

    return ConversationHandler.END



handler = ConversationHandler(
    entry_points=[CommandHandler('search', search_start, pass_user_data=True)],
    allow_reentry=True,
    states={
        STATE: [MessageHandler(Filters.text, search_state, pass_user_data=True)],
        PROVINCE: [MessageHandler(Filters.text, search_province, pass_user_data=True)],
        CITY: [MessageHandler(Filters.text, search_city, pass_user_data=True)],
        DO: [MessageHandler(Filters.text, search_do, pass_user_data=True)],

    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
