import os

from vkbottle import CtxStorage
from vkbottle.bot import Bot

from .game import GameProcessor

bot = Bot(os.environ['BOT_TOKEN'])
cache = CtxStorage()
game = GameProcessor(bot)
