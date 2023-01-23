from vk_api.longpoll import Event

from ..base_handler import Handler
from ..poll import PollSession


class EchoModeHandler(Handler):
    async def process(self, event: Event, session: PollSession):
        await self.vk.set_typing_activity(event.user_id)
        message = f'echo {event.text.lower()}, {session.user.first_name}'
        self.vk.send_from_bot(event.user_id, message)
