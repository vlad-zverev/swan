import logging
import random
from asyncio import sleep
from datetime import datetime

from vkbottle.bot import Bot, Message
from vkbottle_types.objects import UsersUserFull

from .consts import *
from .keyboards import *


class GameProcessor:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.sessions: dict[int, tuple[Okhota, Hunter]] = {}

    async def process(self, user_info: UsersUserFull, message: Message):
        if user_info.id not in self.sessions:
            okhota = Okhota()
            hunter = Hunter(
                okhota=okhota,
                user_id=user_info.id,
                name=user_info.first_name,
                birth_year=int(user_info.bdate[-4:]) if user_info.bdate else 2000,
                city=user_info.city.title,
            )
            self.sessions[user_info.id] = okhota, hunter
        else:
            okhota, hunter = self.sessions[user_info.id]
        await self.here_we_go(message, okhota, hunter)

    async def here_we_go(self, message: Message, okhota: 'Okhota', hunter: 'Hunter'):
        okhota.na_lebedei_till_death_once_a_year(hunter, decision=message.text)
        await self.post_round(message, okhota, hunter)

    async def post_round(self, message: Message, okhota: 'Okhota', hunter: 'Hunter'):
        count = len(okhota.messages)
        for index, text in enumerate(okhota.messages):
            keyboard = SWAN_GAME_KEYBOARD if count - index == 1 and hunter.alive else None
            await sleep(.5)
            await message.answer(text, keyboard=keyboard)
        okhota.messages.clear()
        if not hunter.alive:
            del self.sessions[message.from_id]
            self.bot.state_dispenser.delete(message.from_id)


class Points(int):
    MIN = 0
    MAX = 100

    def _trim_by_limits(self, res):
        return self.__class__(min(max(res, self.MIN), self.MAX))

    def __add__(self, other):
        res = super(Points, self).__add__(other)
        return self._trim_by_limits(res)

    def __sub__(self, other):
        res = super(Points, self).__sub__(other)
        return self._trim_by_limits(res)


class Zhertva:
    NAMES = ['Лёня', 'Витя', 'Игорь', 'Вова', 'Гена', 'Илья']

    def __init__(self, difficulty: str):
        self.name = random.choice(self.NAMES)
        self.sheinaya_prochnost = random.randint(*DifficultyRanges.sheinaya_prochnost[difficulty])
        self.sila_klyuva = random.randint(*DifficultyRanges.sila_klyuva[difficulty])
        self.prozharena = Points(0)
        self.alive: bool = True

    def __str__(self):
        return f'лебедь {self.name}'


class Hunter:
    NATURAL_CAUSES_OF_DEATH = ['инсульт', 'рак', 'инфаркт']
    ANATOMY_PART_OF_BODY = ['жопы', 'мозга']
    SUICIDE_METHODS = ['повешенья', 'утопления', 'прыжка с крыши', 'выстрела в висок']
    POILO = {
        'энерджайзером': 3,
        'кофейком': 2,
        'цитрусовым соком': 1,
        'пивом': -1,
        'вином': -2,
        'портвухой': -3,
        'водкой': -4,
        'абсентом': -5,
        'настойкой': -10,
    }

    def __init__(
            self, okhota: 'Okhota',
            user_id: int,
            birth_year: int = 1997,
            name: str = 'Душитель',
            city: str = 'Moscow-City',
    ):
        self.okhota = okhota
        self.send = okhota.send
        self.name = name
        self.city = city
        self.user_id = user_id
        self.birth_year = birth_year
        self.age = datetime.now().year - birth_year
        self.death_age = random.randint(self.age + 15, self.age + 30)
        self.suicide_method = random.choice(self.SUICIDE_METHODS)
        self.cause_of_death = f'{random.choice(self.NATURAL_CAUSES_OF_DEATH)} {random.choice(self.ANATOMY_PART_OF_BODY)}'

        self.health_points = Points(100)
        self.dushitelnyi_skill = Points(1)
        self.alive: bool = True

    def __str__(self):
        return f'{self.name}'

    def trenirovatsya_v_udushenii(self) -> None:
        improve = random.randint(*DifficultyRanges.trenirovka[self.okhota.difficulty])
        self.dushitelnyi_skill += improve
        self.send(f'ты теперь лучше душишь на {improve} очков, теперь у тебя аж {self.dushitelnyi_skill}')

    def est_tabletku(self) -> None:
        power_of_peel = random.randint(*DifficultyRanges.power_of_peel[self.okhota.difficulty])
        if power_of_peel < 5:
            rank = 'так себе'
        elif power_of_peel >= 7:
            rank = 'хороша'
        else:
            rank = 'норм'
        self.health_points += power_of_peel
        self.send(f'таблетка была {rank} и дала {power_of_peel} здоровья')

    def zadushit(self, zhertva: 'Zhertva') -> bool:
        self.send(
            f'тебе противостоит лебедь с шейной прочностью {zhertva.sheinaya_prochnost} '
            f'и силой клюва {zhertva.sila_klyuva}'
        )
        if zhertva.sheinaya_prochnost > self.dushitelnyi_skill:
            self.health_points -= zhertva.sila_klyuva
            self.send(f'{zhertva} выжил и надавал тебе пиздюлей..... иди потренируйся ещё.....')
            self.send(f'у тебя осталось {self.health_points}/100 здоровья')
            loss = random.randint(*DifficultyRanges.fight_skill_loss[self.okhota.difficulty])
            self.dushitelnyi_skill -= loss
            self.send(
                f'битва негативно сказалась на твоих когнитивных способностях.....'
                f'теперь ты душишь на {loss} очков хуже...... '
                f'твой душительный скилл равен {self.dushitelnyi_skill}......'
            )
        else:
            zhertva.alive = False
            self.send(f'ты официально убийца, {zhertva.name} отправился в мир иной')
            improve = random.randint(*DifficultyRanges.fight_skill_improve[self.okhota.difficulty])
            self.dushitelnyi_skill += improve
            self.send(
                f'в битве ты научился душить еще на {improve} очков лучше...... '
                f'теперь твой душительный скилл {self.dushitelnyi_skill}......'
            )
            self.cook_chkmerooli(zhertva)
        return not zhertva.alive

    def cook_chkmerooli(self, zhertva: 'Zhertva') -> None:
        self.send('готовим чкмерули...')
        while zhertva.prozharena < 100:
            self.podzharit(zhertva, sila_ognya=random.randint(10, 30))
            self.send(f'cooking, жертва прожарена на {zhertva.prozharena}/100')
        self.send('все к столу')
        self.propivat_skill()

    def podzharit(self, zhertva: 'Zhertva', sila_ognya: int) -> None:
        zhertva.prozharena += sila_ognya

    def propivat_skill(self) -> None:
        napitok = random.choice(list(self.POILO.keys()))
        points = self.POILO[napitok]
        self.dushitelnyi_skill += points
        change = 'придало тебе сил и прибавило' if points > 0 else 'лишило тебя'
        self.send(
            f"но застолье с {napitok} {change} {abs(points)} очков навыка, "
            f"теперь ты душишь на {self.dushitelnyi_skill}"
        )

    def check_killed(self) -> bool:
        if self.health_points <= 0:
            self.alive = False
            self.send('здоровья погибшим')
            self.send('это была насильственная смерть')
            return True
        return False

    def check_natural_death(self) -> bool:
        if self.age >= self.death_age:
            self.alive = False
            self.send(f'душительница умерла от естественных причин ({self.cause_of_death}) в возрасте {self.death_age}')
            return True
        return False

    def check_death(self) -> bool:
        return self.check_natural_death() or self.check_killed() or not self.alive

    def suicide(self):
        self.send(f'suicided методом {self.suicide_method}.......')
        self.alive = False

    def necrologue(self):
        self.send(f'будет похоронен на одном из кладбищ города {self.city}')


class Okhota:
    messages: list[str] = []

    def __init__(self, difficulty: str = None):
        self.kills_counter = 0
        self.year = datetime.now().year
        self.started = False
        self.difficulty = difficulty or random.choice(DIFFICULTIES)

    def send(self, event: str):
        self.messages.append(event)

    @property
    def is_future(self):
        return self.year > datetime.now().year

    def na_lebedei_till_death_once_a_year(self, hunter: Hunter, decision: str) -> None:
        self.start_new_round(hunter)
        self.call_command(hunter, decision)
        if hunter.alive:
            self.hunt(hunter)
        self.end_round(hunter)

    def start_new_round(self, hunter: Hunter):
        (proshel, uzhe) = ('прошел год....... ', ' уже ') if self.is_future else ('', ' ')
        self.send(
            f'{proshel}{hunter}{uzhe}возрастом около {hunter.age}, '
            f'сейчас {self.year}-й год....\n '
            f'здоровье {hunter.health_points}/100, '
            f'сила удушения {hunter.dushitelnyi_skill} \n'
        )

    def call_command(self, hunter: Hunter, decision: str) -> None:
        {
            'тренить': hunter.trenirovatsya_v_udushenii,
            'лечить': hunter.est_tabletku,
            'наложить на себя руки': hunter.suicide,
            'тренить + лечить': self.train_and_cure,
            'here we go': self.start_game,
        }.get(decision, self.wrong_command)()

    @staticmethod
    def start_game():
        logging.info('Стартуем...')

    def train_and_cure(self):
        self.send('для разблокировки этой функции жду 0.01 BTC на адрес 1MDgSo2ko9Y7cQshbXw2RHgZ5PkuzGrH5E')

    def wrong_command(self):
        pass

    def hunt(self, hunter: Hunter):
        zhertva = Zhertva(self.difficulty)
        if hunter.zadushit(zhertva):
            self.kills_counter += 1

    def end_round(self, hunter: Hunter):
        if hunter.check_death():
            self.send(
                f'охота окончена, за свою {hunter.age}-летнюю жизнь {hunter} '
                f'задушила {self.kills_counter} лебедей, '
                f'на дворе {self.year}-й год.....'
            )
            hunter.necrologue()
        else:
            self.send(
                'теперь жми на кнопки\n'
                '- чтоб тренироваться в удушении \n'
                '- чтоб съесть лекарства \n'
                '- чтоб наложить на себя руки\n'
            )
            self.year += 1
            hunter.age += 1
