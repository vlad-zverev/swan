from vkbottle.bot import Message
from vkbottle_types.objects import UsersUserFull

from .consts import *
from .globals import bot, game
from .keyboards import *


@bot.on.message(text='here we go')
async def start(message: Message):
    await bot.state_dispenser.set(message.from_id, State.IN_CHOOSE_DIFFICULTY)
    text = 'вы вошли в симулятор удушения лебедей\nвыберите уровень сложности.........'
    await message.answer(text, keyboard=SWAN_DIFFICULTIES_KEYBOARD)


@bot.on.message(text=EXIT_COMMAND)
async def suicide(message: Message, user: UsersUserFull):
    await bot.state_dispenser.delete(message.from_id)
    if user.id in game.sessions:
        await game.process(user, message)
    await message.answer('земля пухом', keyboard=SWAN_START_KEYBOARD)


@bot.on.message(state=State.IN_CHOOSE_DIFFICULTY)
async def choose_difficulty(message: Message):
    if message.text in DIFFICULTIES:
        await bot.state_dispenser.set(message.from_id, State.IN_FIGHT)
        await message.answer(f'удачи, {message.text}!', keyboard=SWAN_GAME_KEYBOARD)
    else:
        await message.answer(f'ты снова меня не понял...... тыкай кнопки', keyboard=SWAN_DIFFICULTIES_KEYBOARD)


@bot.on.message(state=State.IN_FIGHT)
async def fight(message: Message, user: UsersUserFull):
    await game.process(user, message)
