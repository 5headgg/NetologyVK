from vkbottle.bot import Message
from states import check_user
from keyboards import search_keyboard
from vkbottle.bot import BotLabeler


chat_labeler = BotLabeler()


@chat_labeler.private_message(text=['Начать', 'начать'])
async def start(message: Message):
    await message.answer(f'Нажми на кнопку "Поиск"', keyboard=search_keyboard)


@chat_labeler.private_message(text=['Поиск'])
async def search(message: Message):
    await message.answer('Проверяю данные...')
    await check_user(message)
