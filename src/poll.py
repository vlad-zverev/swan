import logging
from queue import Queue, Empty
from threading import Lock
from threading import Thread
from typing import Optional

from vk_api.longpoll import Event
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.vk_api import VkApiMethod

from .models import *
from .vk import Vk


class PollSession:
    def __init__(self, api: VkApiMethod, user_info: VkUserInfo, event: Event):
        self.api = api
        self.user_info = user_info
        self._lock = Lock()
        self.events = Queue()
        self.add_event(event)

    def add_event(self, event: Event) -> None:
        with self._lock:
            self.events.put(event)

    def last_event(self) -> Optional[Event]:
        try:
            with self._lock:
                return self.events.get_nowait()
        except Empty:
            return


class PollHandler:
    def __init__(self, vk: 'Vk'):
        self.vk = vk
        self.long_poll = VkLongPoll(vk.bot)
        self.skip_events = [VkEventType.MESSAGES_COUNTER_UPDATE]
        self.poll_thread: Optional[Thread] = None
        self._sessions: dict[int, PollSession] = {}
        self.lock = Lock()

    @property
    def sessions(self):
        with self.lock:
            return self._sessions

    def register_event(self, event: Event) -> Optional[PollSession]:
        user_id = event.user_id if 'user_id' in event.__dict__ else None
        if not user_id:
            logging.error(f"No user_id in event: {event.type.name}")
            return
        logging.debug(f'New event: <user_id={user_id}; type={event.type.name}>')
        if user_id not in self.sessions:
            user_info = self.vk.get_user_info(user_id)
            if not user_info:
                logging.error(f"Can't register event without user info: {event}")
                return
            session = PollSession(self.vk.api, user_info, event)
            with self.lock:
                self._sessions[user_id] = session
        else:
            session = self.sessions[user_id]
            session.add_event(event)
        return session

    def poll(self):
        logging.info('Start VK polling...')
        for event in self.long_poll.listen():
            if event.type in self.skip_events:
                continue
            session = self.register_event(event)
            if not session:
                logging.warning(f'Missed event: {event.type.name}')
                continue

    def run(self) -> None:
        thread = Thread(target=self.poll, daemon=True)
        thread.start()
        self.poll_thread = thread
