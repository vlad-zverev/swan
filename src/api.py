import logging
from asyncio import sleep
from typing import Optional

from dotenv import dotenv_values
from vk_api import VkApi
from vk_api.longpoll import Event, VkEventType
from vk_api.vk_api import VkApiMethod

from .models import *


class Vk:
    def __init__(self):
        secrets = dotenv_values('env/secrets.env')
        if not secrets:
            raise Exception("Add file 'env/secrets.env' with 'LOGIN', 'PASSWORD', 'TOKEN' and 'TOKEN_APP'")
        self.__auth = VkAuthConfig(**secrets)
        self.config = VkConfig(**dotenv_values('env/vk.env'))
        self.bot = VkApi(token=self.__auth.TOKEN_APP)
        self.bot_api: VkApiMethod = self.bot.get_api()
        self.user = VkApi(
            self.__auth.LOGIN,
            self.__auth.PASSWORD,
            token=self.__auth.TOKEN,
            auth_handler=lambda: (input('2FA: '), True),
        )
        self.api: VkApiMethod = self.user.get_api()

    def get_wall(self, owner_id: int = None) -> dict:
        return self.api.wall.get(owner_id=owner_id or self.config.HUMORESKI)

    def get_user_info(self, user_id: int) -> Optional[VkUserInfo]:
        users = self.api.users.get(
            user_id=user_id,
            fields=['city', 'sex', 'bdate'],
        )
        if not users:
            logging.error(f'No user with id {user_id}')
            return
        user = users[0]
        return VkUserInfo(
            id=user['id'],
            first_name=user['first_name'],
            city=user['city']['title'] if 'city' in user else 'Moscow-City',
            sex=VkUserSex(user['sex'] if 'sex' in user else 2),
            birth_year=int(user['bdate'][-4:]) if 'bdate' in user else 2000,
        )

    async def set_typing_activity(self, user_id: int, timeout: float = 1) -> None:
        self.bot_api.messages.setActivity(
            user_id=user_id,
            type='typing'
        )
        logging.info('Bot typing...')
        await sleep(timeout)

    def send_from_bot(self, user_id: int, message: str, keyboard: Optional[dict] = None):
        self.bot_api.messages.send(
            user_id=user_id,
            message=message,
            keyboard=keyboard,
            random_id=0,
        )
        logging.info(f'Message sent: {message}')

    @staticmethod
    def is_event_need_response(event: Event) -> bool:
        return event.type == VkEventType.MESSAGE_NEW and event.to_me
