from telegram.bot import Bot
from telegram.update import Update
from telegram.ext import CommandHandler
from meeting.db import User, session
import time

welcome_text = """
سلام
این یک ربات همسر یابی است
شما در این ربات می توانید پروفایل را ایجاد کرده و در سایر پروفایل ها جستجو کنید"""

hello_guest_text = """سلام
شما هنوز پروفایل خود را در این ربات کامل نکرده اید"""

guide_text ="""می توانید با استفاده از /register پروفایل خود را کامل کنید 
یا با استفاده از  /search جستجو کنید
با /user_list می توانید لیست تمام افراد را ببینید
"""

def start(bot:Bot, update:Update, args):
    bot.sendMessage(chat_id=update.message.chat_id, text=welcome_text)
    telegram_user = update.message.from_user
    i = update.message.chat_id
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    if user:
        if user.username == telegram_user.username:
            bot.sendMessage(chat_id=update.message.chat_id, text='سلام {} '.format(user.first_name))
            bot.sendMessage(chat_id=update.message.chat_id, text=guide_text)

        else:
            bot.sendMessage(chat_id=update.message.chat_id, text='you modified your account setting.')

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

        bot.sendMessage(chat_id=update.message.chat_id, text=hello_guest_text)
        bot.sendMessage(chat_id=update.message.chat_id, text=guide_text)



handler = CommandHandler("start", start, pass_args=True)