from datetime import datetime
import random
from asyncio import sleep


class Character:
    alive: bool = True


class Hunter(Character):
    health_points = 100
    dushitelnyi_skill = 1

    def __init__(
            self, okhota: 'Okhota',
            user_id: int,
            birth_year: int = 1997,
            name: str = 'Душитель',
            city: str = 'Moscow-City',
    ):
        self.emit = okhota.emit
        self.name = name
        self.city = city
        self.user_id = user_id
        self.birth_year = birth_year
        self.age = datetime.now().year - birth_year
        self.death_age = random.randint(self.age + 10, self.age + 30)
        self.natural_causes_of_death = ['инсульт', 'рак', 'инфаркт']
        self.anatomy_part_of_body = ['жопы', 'мозга']
        self.suicide_methods = ['повешенья', 'утопления', 'прыжка с крыши', 'выстрела в висок']

    def __str__(self):
        return f'{self.name}'

    def trenirovatsya_v_udushenii(self) -> None:
        improve = random.randint(2, 4)
        self.dushitelnyi_skill += improve
        self.emit(f'ты теперь лучше душишь на {improve} очков, теперь у тебя аж {self.dushitelnyi_skill}')

    def est_tabletku(self) -> None:
        power_of_peel = random.randint(3, 10)
        if power_of_peel < 5:
            rank = 'так себе'
        elif power_of_peel >= 7:
            rank = 'хороша'
        else:
            rank = 'норм'
        self.health_points += power_of_peel
        self.emit(f'таблетка была {rank} и дала {power_of_peel} здоровья')

    async def zadushit(self, zhertva: 'Zhertva') -> bool:
        name = random.choice(zhertva.NAMES)
        self.emit(
            f'тебе противостоит лебедь с шейной прочностью {zhertva.sheinaya_prochnost} '
            f'и силой клюва {zhertva.sila_klyuva}'
        )
        if zhertva.sheinaya_prochnost >= self.dushitelnyi_skill:
            self.health_points -= zhertva.sila_klyuva + random.randint(-2, 2)
            if self.health_points < 0:
                self.health_points = 0
            self.emit(f'{zhertva} {name} выжил и надавал тебе пиздюлей..... иди потренируйся ещё.....')
            self.emit(f'у тебя осталось {self.health_points}/100 здоровья')
            self.dushitelnyi_skill += 1
        else:
            zhertva.alive = False
            self.dushitelnyi_skill += 2
            self.emit(f'ты официально убийца, {name} отправился в мир иной')
            await self.cook_chkmerooli(zhertva)
        return not zhertva.alive

    async def cook_chkmerooli(self, zhertva):
        self.emit('готовим чкмерули')
        while zhertva.prozharena < 10:
            self.podzharit(zhertva, sila_ognya=random.randint(1, 4))
            self.emit(f'cooking, жертва прожарена на {zhertva.prozharena}/10')
            await sleep(0.1)
        self.emit('все к столу')
        self.propivat_skill()

    def podzharit(self, zhertva, sila_ognya):
        zhertva.prozharena += sila_ognya

    def propivat_skill(self):
        poilo = {
            'пивом': 1,
            'вином': 2,
            'портвухой': 3,
            'водкой': 4,
            'абсентом': 5,
            'настойкой': 7,
        }
        napitok = random.choice(list(poilo.keys()))
        self.dushitelnyi_skill -= poilo[napitok] if self.dushitelnyi_skill - poilo[napitok] > 0 else 0
        self.emit(
            f"но застолье с {napitok} лишило тебя {poilo[napitok]} очков навыка, "
            f"теперь ты душишь на {self.dushitelnyi_skill}"
        )

    def check_killed(self) -> bool:
        if self.health_points <= 0:
            self.alive = False
            self.emit('здоровья погибшим')
            self.emit('это была насильственная смерть')
            return True

    def check_death(self) -> bool:
        if self.age >= self.death_age:
            reason = f'{random.choice(self.natural_causes_of_death)} {random.choice(self.anatomy_part_of_body)}'
            self.alive = False
            self.emit(f'душительница умерла от естественных причин ({reason}) в возрасте {self.death_age}')
            return True


class Zhertva(Character):
    prozharena = 0
    NAMES = ['Лёня', 'Витя', 'Игорь', 'Вова', 'Гена', 'Илья']

    def __init__(self):
        self.name = random.choice(self.NAMES)
        self.sheinaya_prochnost = random.randint(5, 10)
        self.sila_klyuva = random.randint(10, 15)

    def __str__(self):
        return 'лебедь'


class Okhota:
    messages: list[str] = []

    def __init__(self):
        self.kills_counter = 0
        self.year = datetime.now().year

    def emit(self, event: str):
        self.messages.append(event)

    @property
    def is_future(self):
        return self.year > datetime.now().year

    async def na_lebedei_till_death_once_a_year(self, hunter: 'Hunter', decision: str) -> bool:
        if self.is_future:
            proshel = 'прошел год.......\n'
            uzhe = 'уже '
        else:
            self.emit('вы вошли в симулятор удушения лебедей\n')
            proshel = ''
            uzhe = ''
        self.emit(
            f'\n {proshel} {hunter} {uzhe}возрастом около {hunter.age}, '
            f'сейчас {self.year}-й год....\n '
            f'здоровье {hunter.health_points}/100, '
            f'сила удушения {hunter.dushitelnyi_skill} \n'
        )
        if decision == 'тренить':
            hunter.trenirovatsya_v_udushenii()
        elif decision == 'лечить':
            hunter.est_tabletku()
        elif decision == 'наложить на себя руки':
            self.emit(f'suicided методом {random.choice(hunter.suicide_methods)}.......')
            self.emit(f'\nбудет похоронен на одном из кладбищ города {hunter.city}')
            hunter.alive = False
            return False
        elif decision == 'тренить + лечить':
            self.emit('для разблокировки этой функции жду 0.01 BTC на адрес 1MDgSo2ko9Y7cQshbXw2RHgZ5PkuzGrH5E')
        elif decision.lower() == 'го':
            print('стартуем')
        else:
            self.emit('ты упустил шанс и ничего не прокачал, жми кнопки в след раз.........')

        zhertva = Zhertva()
        if await hunter.zadushit(zhertva):
            self.kills_counter += 1
        if hunter.check_death() or hunter.check_killed():
            self.emit(
                f'охота окончена, за свою {hunter.age}-летнюю жизнь {hunter} задушила {self.kills_counter} лебедей, '
                f'на дворе {self.year}-й год.....'
            )
            self.emit(f'\nбудет похоронен на одном из кладбищ города {hunter.city}')
            return False
        self.emit(
            'теперь жми на кнопки\n'
            '- чтоб тренироваться в удушении \n'
            '- чтоб съесть лекарства \n'
            '- чтоб наложить на себя руки\n'
        )
        self.year += 1
        hunter.age += 1
        return True
