from telegram.bot import Bot
from telegram.update import Update
from telegram.ext import CommandHandler
from meeting.db import User, session
import time

def list(bot:Bot, update:Update, args):

    users = session.query(User).filter_by().all()
    for user in users:
        user_data = "{name} {city} {gender}".format(name=user.first_name, city=user.city, gender=user.gender)
        bot.sendMessage(chat_id=update.message.chat_id, text=user_data)




handler = CommandHandler("user_list", list, pass_args=True)