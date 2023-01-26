from vkbottle import Keyboard, KeyboardButtonColor as Color, Text, BaseMiddleware

SWAN_START_KEYBOARD = (
	Keyboard(one_time=True, inline=False)
	.add(Text('here we go'), color=Color.SECONDARY)
	.get_json()
)

SWAN_GAME_KEYBOARD = (
	Keyboard(one_time=True, inline=False)
	.add(Text('тренить'), color=Color.PRIMARY)
	.add(Text('лечить'), color=Color.PRIMARY)
	.row()
	.add(Text('тренить + лечить'), color=Color.POSITIVE)
	.row()
	.add(Text("наложить на себя руки"), color=Color.SECONDARY)
	.get_json()
)

SWAN_DIFFICULTIES_KEYBOARD = (
	Keyboard(one_time=True, inline=False)
	.add(Text('салага'), color=Color.SECONDARY)
	.add(Text('солдат'), color=Color.PRIMARY)
	.add(Text('боец'), color=Color.POSITIVE)
	.add(Text('легенда'), color=Color.NEGATIVE)
	.row()
	.add(Text('наложить на себя руки'), color=Color.SECONDARY)
	.get_json()
)

SUICIDE_KEYBOARD = (
	Keyboard(one_time=True, inline=False)
	.add(Text('наложить на себя руки'), color=Color.SECONDARY)
	.get_json()
)
