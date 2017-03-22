import sys
import os
here = os.path.abspath(os.path.dirname(__file__))
package_root = os.path.abspath(os.path.dirname(here))

from configparser import ConfigParser
config = ConfigParser()

if len(sys.argv) != 2 or not sys.argv[1].endswith(".ini"):
    raise Exception("no config file")

config.read(sys.argv[1])
config.set('main', 'here', package_root)
bot_token = config['main']['bot.token']
sqlalchemy_url = config['main']['sqlalchemy.url']
