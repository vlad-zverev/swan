import logging
from queue import Queue, Empty
from threading import Thread, Lock, Condition
from typing import Optional

from vk_api.longpoll import Event, VkLongPoll, VkEventType

from .api import Vk
from .models import *


class PollSession:
    def __init__(self, user: VkUserInfo):
        self.user = user


class PollHandler:
    def __init__(self, vk: 'Vk'):
        self.vk = vk
        self.long_poll = VkLongPoll(vk.bot)
        self.skip_events = [VkEventType.MESSAGES_COUNTER_UPDATE]
        self.poll_thread: Optional[Thread] = None
        self.events = Queue()
        self.lock = Lock()
        self.condition = Condition()
        self._sessions: dict[int, PollSession] = {}

    def add_event(self, event: Event) -> None:
        with self.lock:
            self.events.put(event)
        with self.condition:
            self.condition.notify_all()

    def last_event(self) -> Optional[Event]:
        try:
            with self.lock:
                return self.events.get_nowait()
        except Empty:
            return

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
            session = PollSession(user_info)
            with self.lock:
                self._sessions[user_id] = session
        else:
            session = self.sessions[user_id]
            self.add_event(event)
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
