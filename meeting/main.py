from meeting import config

from sqlalchemy_utils.functions import create_database, database_exists
if not database_exists(config.sqlalchemy_url):
    create_database(config.sqlalchemy_url)



from telegram.ext import Updater
import logging

from meeting import start, not_found, register, search

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error(bot, update, error):
    print('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(config.bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(start.handler)
    dp.add_handler(register.handler)
    dp.add_handler(search.handler)
    dp.add_handler(not_found.handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    print('now running bot')
    main()
