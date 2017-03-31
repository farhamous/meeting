from telegram.bot import Bot
from telegram.update import Update
from telegram.ext import CommandHandler
from meeting.db import User, session

hello_guest_text = """سلام
شما هنوز پروفایل خود را در این ربات کامل نکرده اید"""

guide_text ="""می توانید با استفاده از /register پروفایل خود را کامل کنید 
یا با استفاده از  /search جستجو کنید"""

def start(bot:Bot, update:Update, args):


    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    if user:
        if user.username == telegram_user.username:
            bot.sendMessage(chat_id=update.message.chat_id, text='سلام {} '.format(user.first_name))
            bot.sendMessage(chat_id=update.message.chat_id, text=guide_text)

        else:
            bot.sendMessage(chat_id=update.message.chat_id, text='you modified your account setting.')

    else:
        bot.sendMessage(chat_id=update.message.chat_id, text=hello_guest_text)
        bot.sendMessage(chat_id=update.message.chat_id, text=guide_text)



handler = CommandHandler("start", start, pass_args=True)