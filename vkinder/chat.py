from vkbottle.bot import BotLabeler
from vkbottle.bot import Message

from .messages import hello, init_search
from .keyboards import search_keyboard
from .states import data_state_handler
from .config import api


chat_labeler = BotLabeler()


@chat_labeler.private_message(text=['начать', 'Начать'])
async def start_handler(message: Message):
    users = await api.users.get(message.from_id)
    user_info = users[0]
    await message.answer(hello.format(user_info.first_name), keyboard=search_keyboard)


@chat_labeler.private_message(text=['Поиск 🔎'])
async def search_handler(message: Message):
    users = await api.users.get(message.from_id)
    user_info = users[0]

    await message.answer(init_search.format(user_info.first_name))
    await data_state_handler(message)
