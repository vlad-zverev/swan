import asyncio
import logging
from typing import Type

from vk_api.longpoll import Event

from .api import Vk
from .base_handler import Handler
from .models import Mode
from .modes import *
from .poll import PollSession, PollHandler


class EventsHandler:
    MODES: dict[Mode, Type[Handler]] = {
        Mode.ECHO: EchoModeHandler,
        Mode.SWAN: SwanModeHandler,
    }

    def __init__(self, vk: Vk, poll: PollHandler, mode: Mode = Mode.ECHO):
        self.vk = vk
        self.poll = poll
        self.handler = self.MODES[mode](vk)

    async def process_event(self, event: Event, session: PollSession):
        if self.vk.is_event_need_response(event):
            message = event.text.lower()
            logging.info(f'New message: {message}')
            await self.handler.process(event, session)

    async def handle_events(self):
        logging.info('Start handling events...')
        while True:
            with self.poll.condition:
                while self.poll.events.empty():
                    self.poll.condition.wait()
                event = self.poll.last_event()
                session = self.poll.sessions[event.user_id]
                await self.process_event(event, session)

    def run(self):
        try:
            asyncio.run(self.handle_events())
        except asyncio.exceptions.CancelledError:
            logging.info('Successfully stopped handling events')
        exit(0)
