from telegram.bot import Bot
from telegram.update import Update
from telegram.ext import CommandHandler
from meeting.db import User, session

def start(bot:Bot, update:Update, args):

    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    if user:
        if user.username == telegram_user.username:
            bot.sendMessage(chat_id=update.message.chat_id, text='welcome {}'.format(user.first_name))
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text='you modified your account setting.')

    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="hello guest")



handler = CommandHandler("start", start, pass_args=True)