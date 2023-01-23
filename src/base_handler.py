from abc import abstractmethod

from vk_api.longpoll import Event

from .api import Vk
from .poll import PollSession


class Handler:
    def __init__(self, vk: Vk):
        self.vk = vk

    @abstractmethod
    async def process(self, event: Event, session: PollSession) -> None:
        pass
