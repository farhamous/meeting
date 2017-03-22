from telegram.bot import Bot
from telegram.update import Update
from telegram.ext import MessageHandler

def echo(bot, update:Update):
    i = update.message.chat_id
    bot.sendMessage(i, text='Not Implemented')

handler = MessageHandler(None, echo)