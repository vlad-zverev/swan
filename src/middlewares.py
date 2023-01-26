import logging

from vkbottle import BaseMiddleware
from vkbottle.bot import Message, rules
from vkbottle_types.objects import UsersUserFull

from .keyboards import SWAN_START_KEYBOARD
from .globals import bot, cache


class NoBotMiddleware(BaseMiddleware[Message]):
    async def pre(self):
        if self.event.from_id < 0:
            self.stop('Groups are not allowed to use bot')


class RegistrationMiddleware(BaseMiddleware[Message]):

    def __init__(self, event, view):
        super().__init__(event, view)
        self.cached = False

    async def pre(self):
        user_info = cache.get(self.event.from_id)
        if user_info is None:
            user = (await bot.api.users.get(self.event.from_id, fields=['bdate', 'city', 'sex']))[0]
            cache.set(self.event.from_id, {'user': user, 'calls': 1})
            self.cached = False
        else:
            self.cached = True
            user: UsersUserFull = user_info['user']
            calls = user_info['calls'] + 1
            cache.set(self.event.from_id, {'user': user, 'calls': calls})
            logging.info(f"{calls} message from {user.first_name}")
        self.send({'user': user})

    async def post(self):
        logging.info(f"User{' ' if self.cached else ' not '}cached")


class InfoMiddleware(BaseMiddleware[Message]):
    async def post(self):
        if not self.handlers:
            logging.warning('Message missed by handlers')
            await self.event.answer('не понял тебя......', keyboard=SWAN_START_KEYBOARD)

        logging.info(
            'Message processed:\n\n'
            f'View - {self.view}\n\n'
            f'Handlers - {self.handlers}'
        )


class MetadataRule(rules.ABCRule[Message]):

    async def check(self, message: Message) -> dict:
        chats_info = await message.ctx_api.messages.get_conversations_by_id(message.peer_id)
        return {'chat': chats_info.items[0]}


bot.labeler.message_view.register_middleware(NoBotMiddleware)
bot.labeler.message_view.register_middleware(RegistrationMiddleware)
bot.labeler.message_view.register_middleware(InfoMiddleware)
