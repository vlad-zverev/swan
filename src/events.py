import asyncio
import logging
from abc import abstractmethod
from asyncio import sleep
from typing import Type

from vk_api.longpoll import VkEventType, Event

from .models import *
from .vk import Vk
from .poll import PollSession, PollHandler


class Handler:
    def __init__(self, vk: Vk):
        self.vk = vk

    @abstractmethod
    async def process(self, event: Event, session: PollSession) -> None:
        pass


class EchoModeHandler(Handler):
    async def process(self, event: Event, session: PollSession):
        await self.vk.set_typing_activity(event.user_id)
        message = f'echo {event.text.lower()}, {session.user_info.first_name}'
        self.vk.send_from_bot(event.user_id, message)


class EventsHandler:
    MODES: dict[Mode, Type[Handler]] = {
        Mode.ECHO: EchoModeHandler,
    }

    def __init__(self, vk: Vk, poll: PollHandler, mode: Mode = Mode.ECHO):
        self.vk = vk
        self.poll = poll
        self.mode = mode
        self.handler: Handler = self.MODES[mode](vk)

    async def process_event(self, event: Event, session: PollSession):
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            message = event.text.lower()
            logging.info(f'New message: {message}')
            await self.handler.process(event, session)

    async def handle_events(self):
        logging.info('Start handling events...')
        while True:
            tasks = []
            for _, session in self.poll.sessions.items():
                event = session.last_event()
                if event:
                    tasks.append(asyncio.ensure_future(self.process_event(event, session)))
            tasks.append(asyncio.ensure_future(sleep(.1)))
            await asyncio.gather(*tasks)

    def run(self):
        try:
            asyncio.run(self.handle_events())
        except asyncio.exceptions.CancelledError:
            logging.info('Successfully stopped')
        exit(0)
