from vkbottle import CtxStorage
from vkbottle.bot import Message
from vkbottle.bot import BotLabeler
from vkbottle import BaseStateGroup

from .messages import send_age, send_city, search_options, unfamiliar_city, send_only_numbers, age_limit, searching
from .config import api, state_dispenser, AGE_FROM, AGE_TO, USER_DATA_FIELDS
from .utils import get_age, reversed_sex_table, sex_table, relation_table
from .base import is_there_a_user, add_new_user
from .callbacks import start_search_users


states_labeler = BotLabeler()
ctx = CtxStorage()


class UserInfoState(BaseStateGroup):
    USER_DATA = 0
    AGE = 1
    CITY = 2


@states_labeler.private_message(state=UserInfoState.AGE)
async def age_handler(message: Message):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer(send_only_numbers)
    else:
        age = int(text)
        if AGE_FROM <= age <= AGE_TO:
            ctx.set('age', age)
        else:
            await message.answer(age_limit)
    await state_dispenser.delete(message.peer_id)
    await data_state_handler(message)


@states_labeler.private_message(state=UserInfoState.CITY)
async def city_handler(message: Message):
    text = message.text.strip()
    cities = await api.database.get_cities(country_id=1, q=text)
    if cities.items:
        ctx.set('city', text.title())
    else:
        await message.answer(unfamiliar_city)

    await state_dispenser.delete(message.peer_id)
    await data_state_handler(message)


async def check_user_data(message: Message, user_id: int) -> bool:
    users = await api.users.get(user_id, fields=USER_DATA_FIELDS)
    user_info = users[0]

    age = ctx.get('age')
    if user_info.city:
        ctx.set('city', user_info.city.title)

    city = ctx.get('city')

    bod = user_info.bdate
    if bod:
        broken_bod = bod.strip('.')
        if len(broken_bod) == 3:
            ctx.set('age', get_age(bod))

    if not age:
        await message.answer(send_age)
        await state_dispenser.set(message.peer_id, UserInfoState.AGE)
        return False

    if not city:
        await message.answer(send_city)
        await state_dispenser.set(message.peer_id, UserInfoState.CITY)
        return False

    relation_object = user_info.relation
    relation_id = relation_object.value
    relation_text = relation_table[relation_id]

    sex_object = user_info.sex
    sex_id = sex_object.value
    reversed_sex_id = reversed_sex_table[sex_id]
    sex_text = sex_table[reversed_sex_id]
    add_new_user(user_id, age, sex_id, relation_id, city)
    ctx.delete('age')
    ctx.delete('city')
    await message.answer(search_options.format(city, age, sex_text, relation_text))
    return True


async def data_state_handler(message: Message):
    user_id = message.from_id
    if not is_there_a_user(user_id):
        have_all_data = await check_user_data(message, user_id)
        if not have_all_data:
            return

    await message.answer(searching)
    await start_search_users(message)
