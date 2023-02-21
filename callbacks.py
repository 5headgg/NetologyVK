from vkbottle.dispatch.rules import ABCRule
from vkbottle import GroupEventType
from models import is_viewed, add_view, add_like, add_new_or_update_user
from vkbottle.bot import BotLabeler, MessageEvent, Message
from keyboards import get_user_keyboard
from vkbottle.tools.dev.mini_types.base import BaseMessageMin
from service import get_age, reversed_sex
from config import api, ctx

callback_labeler = BotLabeler()


class PayloadRule(ABCRule[BaseMessageMin]):
    def __init__(self, payload):
        if isinstance(payload, dict):
            payload = [payload]
        self.payload = payload

    async def check(self, event: BaseMessageMin) -> bool:
        payload = event.get_payload_json()
        command = {'cmd': payload.get('cmd')}
        return command in self.payload


async def search_users():
    ctx_users = ctx.get('users')
    if ctx_users:
        return ctx_users
    users = []
    fields = [
        'is_closed',
        'blacklisted',
        'can_write_private_message',
        'bdate',
        'verified'
    ]

    users_object = await api.users.search(offset=0, count=1000, has_photo=True, sex=reversed_sex[ctx.get('sex')],
                                          hometown=ctx.get('city'), age_from=ctx.get('age'), age_to=ctx.get('age'),
                                          status=ctx.get('relation'), fields=fields)
    found_users = users_object.items
    for user in found_users:
        if not (user.is_closed or user.blacklisted or user.is_friend or user.can_write_private_message
                or await is_viewed(ctx.get('user_id'), user.id)):
            users.append(user)
    return users


async def search(message):
    found_users = await search_users()
    if not found_users:
        await message.answer('Никого не найдено!')
        return

    first_user_found = found_users[0]
    if len(found_users) < 2:
        await send_user(first_user_found, message=message, last=True)
    else:
        await send_user(first_user_found, message=message)
        ctx.set('users', found_users[1:])


async def send_user(user, message, change_message=True, liked=False, last=False):
    name = f'{user.first_name} {user.last_name}'
    age = get_age(user.bdate)
    text = f'{name}\n{age} лет.'

    user_keyboard = get_user_keyboard(user.id, last=last, liked=liked)

    photos_object = await api.photos.get_all(owner_id=user.id, count=3, skip_hidden=1)
    photos = ','.join([f'photo{photo.owner_id}_{photo.id}' for photo in photos_object.items])

    if isinstance(message, Message):
        await message.answer(text=text, attachment=photos, keyboard=user_keyboard)
        return

    if change_message:
        await message.edit_message(message=text, attachment=photos, keyboard=user_keyboard)
        return
    await message.send_message(message=text, attachment=photos, keyboard=user_keyboard)


@callback_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'cmd': 'open_link'}))
async def open_link(event: MessageEvent):
    await add_new_or_update_user(ctx.get('user_id'))
    link = event.object.payload['link']
    await event.open_link(link)


@callback_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'cmd': 'next'}))
async def next_user(event: MessageEvent):
    await add_new_or_update_user(ctx.get('user_id'))
    found_users = await search_users()
    if not found_users:
        await event.send_message('Больше в поиске никого нет 😟')
        return

    user_id = event.object.payload.get('user_id')
    sent_user = await api.users.get(user_id, fields=['city', 'sex', 'relation', 'bdate'])
    await send_user(sent_user[0], message=event, liked=True)

    first_user_found = found_users[1]
    await add_view(event.user_id, first_user_found.id)
    if len(found_users) < 2:
        await send_user(first_user_found, message=event, last=True, change_message=False)
        ctx.set('users', [])
        return

    await send_user(first_user_found, message=event, change_message=False)
    ctx.set('users', found_users[2:])


@callback_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'cmd': 'like'}))
async def like_user(event: MessageEvent):
    await add_new_or_update_user(ctx.get('user_id'))
    liked_user_id = event.object.payload.get('user_id')
    liked_users = await api.users.get(liked_user_id, fields=['sex', 'city', 'bdate', 'relation'])
    liked_user = liked_users[0]
    await send_user(liked_user, message=event, liked=True)
    await add_like(event.user_id, liked_user_id)

    found_users = await search_users()
    if not found_users:
        await event.send_message('Больше в поиске никого нет 😟')
        return

    first_user_found = found_users[0]
    await add_view(event.user_id, first_user_found.id)

    if len(found_users) < 2:
        await send_user(liked_user, message=event, change_message=False, last=True)
        ctx.set('users', [])
        return
    await send_user(first_user_found, message=event, change_message=False)
    ctx.set('users', found_users[1:])
