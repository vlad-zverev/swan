from vk_api.longpoll import Event

from .game import Hunter, Okhota
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
            self.start_game(event, okhota)
        else:
            okhota, hunter = self.games[event.user_id]
            if okhota.started:
                await self.here_we_go(event, okhota, hunter)
            else:
                await self.modify_difficulty_and_run(event, okhota, hunter)

    async def here_we_go(self, event: Event, okhota: Okhota, hunter: Hunter):
        okhota.na_lebedei_till_death_once_a_year(hunter, decision=event.text)
        await self.post_round(okhota, hunter, event)

    def start_game(self, event: Event, okhota: Okhota):
        message = 'вы вошли в симулятор удушения лебедей\nвыберите уровень сложности.........'
        self.vk.send_from_bot(user_id=event.user_id, message=message, keyboard=okhota.initial_keyboard())

    async def modify_difficulty_and_run(self, event: Event, okhota: Okhota, hunter: Hunter):
        if event.text not in okhota.DIFFICULTIES:
            return self.start_game(event, okhota)
        okhota.difficulty = event.text
        okhota.started = True
        await self.here_we_go(event, okhota, hunter)

    async def post_round(self, okhota: Okhota, hunter: Hunter, event: Event):
        count = len(okhota.messages)
        for index, message in enumerate(okhota.messages):
            await self.vk.set_typing_activity(user_id=event.user_id, timeout=.5)
            keyboard = okhota.get_keyboard(hunter) if count - index == 1 else None
            self.vk.send_from_bot(user_id=event.user_id, message=message, keyboard=keyboard)
        okhota.messages.clear()
        if not hunter.alive:
            del self.games[event.user_id]
