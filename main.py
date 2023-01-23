import logging
import sys
from os import getenv

from src import Vk, PollHandler, EventsHandler, Mode

logging.basicConfig(
    level=getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s %(levelname)s (%(levelno)s) %(message)s',
    stream=sys.stdout,
)

vk = Vk()

poll = PollHandler(vk)
poll.run()

events = EventsHandler(vk, poll, Mode.SWAN)
events.run()
