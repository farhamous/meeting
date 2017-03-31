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


menu_button = '/start'
cancel_button = '/cancel'
users = {}
with open('Province.json') as f:
    tmp = json.load(f)
    province = [i['name'].strip() for i in tmp]
    cities = {i['name']: [j['name'] for j in i['Cities']] for i in tmp}


PROVINCE, CITY= range(2)

def next_step(bot, update, step):
    i = update.message.chat_id
    reply_keyboard = []


    if step == PROVINCE:
        reply_keyboard = [[i] for i in province]
        text='استان محل زندگی خود را وارد کنید'

    elif step == CITY:
        reply_keyboard = [[i] for i in cities[users[i].province]]
        text = 'شهر محل سکونت خود را مشخص کنید'


    reply_keyboard.append([menu_button, cancel_button])
    bot.sendMessage(i,text=text, reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return step



def search_start(bot, update, user_data):
    print(user_data)
    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    i = update.message.chat_id
    # users[i] = user
    if not user:
        bot.sendMessage(i, text='شما در این سامانه ثبت نام نکرده اید. می توانید از طریق /register ثبت نام کرده و سپس به جستجو خود بپردازید')
        return ConversationHandler.END
    elif not user.city:
        bot.sendMessage(i,
                        text='برای جستجو در آگهی ها انتخاب شهر و استان الزامی است /register ثبت نام خود را تکمیل کرده و سپس به جستجو خود بپردازید')
        return ConversationHandler.END
        # return next_step(bot, update, PROVINCE)
    else:
        users = session.query(User).filter_by(city=user.city).all()
        founded_users = [user.first_name for user in users]
        bot.sendMessage(i, str(founded_users))
        return ConversationHandler.END
        # return next_step(bot, update, PROVINCE)





def search_province(bot, update, user_data):
    print(user_data)
    i = update.message.chat_id
    users[i].province = update.message.text
    session.commit()

    return next_step(bot, update, CITY)

def search_city(bot, update, user_data):
    print(user_data)
    i = update.message.chat_id
    users[i].city = update.message.text
    session.commit()
    return ConversationHandler.END


def cancel(bot, update):
    i = update.message.chat_id
    user = update.message.from_user
    bot.sendMessage(i, text='شما از ادامه منصرف شده اید')

    return ConversationHandler.END


handler = ConversationHandler(
    entry_points=[CommandHandler('search', search_start, pass_user_data=True)],
    allow_reentry=True,
    states={
        PROVINCE: [MessageHandler(Filters.text, search_province, pass_user_data=True)],
        CITY: [MessageHandler(Filters.text, search_city, pass_user_data=True)]
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
