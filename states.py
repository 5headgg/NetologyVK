from vkbottle import BaseStateGroup
from vkbottle.bot import Message
from vkbottle.bot import BotLabeler
from models import add_new_or_update_user
from service import get_age, reversed_sex, relation
from callbacks import search
from config import api, state_dispenser, ctx


sex = {
    0: 'любой',
    1: 'женский',
    2: 'мужской'
}

states_labeler = BotLabeler()


class UserState(BaseStateGroup):
    AGE = 1
    CITY = 2


@states_labeler.private_message(state=UserState.AGE)
async def age_handler(message: Message):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer('Отправьте цифры!')
    else:
        age = int(text)
        if 0 < age < 100:
            ctx.set('age', age)
        else:
            await message.answer('Введите возраст!')
    await state_dispenser.delete(message.peer_id)
    await check_user(message)


@states_labeler.private_message(state=UserState.CITY)
async def city_handler(message: Message):
    text = message.text.strip()
    cities = await api.database.get_cities(country_id=1, q=text)
    if cities.items:
        ctx.set('city', text.title())
    else:
        await message.answer('Нет такого города, попробуйте заново...')

    await state_dispenser.delete(message.peer_id)
    await check_user(message)


async def check_user_data(message: Message, user_id):
    users = await api.users.get(user_id, fields=['sex', 'city', 'bdate', 'relation'])
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
        await message.answer('Отправьте возраст.')
        await state_dispenser.set(message.peer_id, UserState.AGE)
        return False

    if not city:
        await message.answer('Отправьте город.')
        await state_dispenser.set(message.peer_id, UserState.CITY)
        return False

    relation_object = user_info.relation
    relation_id = relation_object.value
    relation_text = relation[relation_id]
    sex_object = user_info.sex
    sex_id = sex_object.value
    reversed_sex_id = reversed_sex[sex_id]
    sex_text = sex[reversed_sex_id]
    ctx.set('user_id', user_id)
    ctx.set('sex', sex_id)
    ctx.set('relation', relation_id)
    ctx.set('age', age)
    ctx.set('city', city)
    await add_new_or_update_user(user_id)
    await message.answer(f'Ищем по данным:\n\n'
                         f'🏳️‍🌈 Пол - {sex_text}\n'
                         f'🔞 Возраст - {age}\n'
                         f'🏢 Город - {city}\n'
                         f'👨‍👩‍👧‍👦 Семейное положение - {relation_text}')
    return True


async def check_user(message: Message):
    user_id = message.from_id

    user_data = await check_user_data(message, user_id)
    if not user_data:
        return

    await message.answer('Идет поиск...')
    await search(message)
