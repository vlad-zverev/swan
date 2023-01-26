import logging
import os
import sys

logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'DEBUG'),
    format='%(asctime)s %(levelname)s (%(levelno)s) %(message)s',
    stream=sys.stdout,
)

from src import bot

bot.run_forever()
