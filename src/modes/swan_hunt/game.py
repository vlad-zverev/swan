from vk_api.longpoll import Event
from vk_api.keyboard import VkKeyboard, VkKeyboardColor as Color
from .models import Hunter, Okhota
from ...api import Vk
from ...base_handler import Handler
from ...poll import PollSession


class SwanModeHandler(Handler):
    def __init__(self, vk: Vk):
        super().__init__(vk)
        self.games: dict[int, tuple[Okhota, Hunter]] = {}

    async def process(self, event: Event, session: PollSession):
        if event.user_id not in self.games:
            okhota = Okhota()
            hunter = Hunter(
                okhota=okhota,
                user_id=session.user.id,
                name=session.user.first_name,
                birth_year=session.user.birth_year,
                city=session.user.city,
            )
            self.games[event.user_id] = okhota, hunter
        okhota, hunter = self.games[event.user_id]
        await self.vk.set_typing_activity(event.user_id)
        await okhota.na_lebedei_till_death_once_a_year(hunter, decision=event.text)
        await self.post_round(okhota, hunter, event)

    async def post_round(self, okhota: Okhota, hunter: Hunter, event: Event):
        for message in okhota.messages:
            await self.vk.set_typing_activity(user_id=event.user_id, timeout=.5)
            self.vk.send_from_bot(user_id=event.user_id, message=message, keyboard=self.get_keyboard(hunter))
        okhota.messages.clear()
        if not hunter.alive:
            del self.games[event.user_id]

    def get_keyboard(self, hunter: Hunter):
        keyboard = VkKeyboard(one_time=False)
        if hunter.alive:
            themes = ['тренить', 'лечить']
            for theme in themes:
                keyboard.add_button(theme, Color.PRIMARY)
            keyboard.add_line()
            keyboard.add_button(' + '.join(themes), Color.POSITIVE)
            keyboard.add_line()
            keyboard.add_button('наложить на себя руки', Color.SECONDARY)
        else:
            keyboard.add_button('го', Color.PRIMARY)
        return keyboard.get_keyboard()
