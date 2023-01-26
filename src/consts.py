from vkbottle import BaseStateGroup


class State(BaseStateGroup):
    IN_CHOOSE_DIFFICULTY = 'difficulty'
    IN_FIGHT = 'fight'


class DifficultyRanges:
    sheinaya_prochnost = {
        'салага': (3, 4),
        'солдат': (4, 5),
        'боец': (5, 6),
        'легенда': (7, 10),
    }
    sila_klyuva = {
        'салага': (7, 9),
        'солдат': (9, 12),
        'боец': (10, 14),
        'легенда': (12, 15),
    }
    trenirovka = {
        'салага': (7, 9),
        'солдат': (5, 8),
        'боец': (5, 7),
        'легенда': (3, 5),
    }
    power_of_peel = {
        'салага': (6, 10),
        'солдат': (5, 9),
        'боец': (4, 8),
        'легенда': (3, 7),
    }
    fight_skill_loss = {
        'салага': (1, 2),
        'солдат': (1, 2),
        'боец': (1, 3),
        'легенда': (2, 3),
    }
    fight_skill_improve = {
        'салага': (2, 4),
        'солдат': (1, 3),
        'боец': (1, 2),
        'легенда': (1, 2),
    }


DIFFICULTIES = (
    'салага',
    'солдат',
    'боец',
    'легенда',
)
EXIT_COMMAND = 'наложить на себя руки'

ADMINS = [
	281596962,  # Vlad
	758212111,  # Artyom
]
