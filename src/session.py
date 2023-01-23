from queue import Queue, Empty
from threading import Lock
from typing import Optional

from vk_api.longpoll import Event
from vk_api.vk_api import VkApiMethod

from .models import *


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
