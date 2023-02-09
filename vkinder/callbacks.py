from typing import Union, List

from vkbottle.tools.dev.mini_types.base import BaseMessageMin
from vkbottle.bot import BotLabeler, MessageEvent, Message
from vkbottle_types.codegen.objects import UsersUserFull
from vkbottle import GroupEventType, CtxStorage
from vkbottle.dispatch.rules import ABCRule

from .config import api, SEARCH_USERS_PARAMS, GET_PHOTOS_PARAMS, SEARCH_USERS_FIELDS, USER_DATA_FIELDS
from .base import get_user, is_viewed, add_view, add_like
from .messages import not_found, end_search
from .keyboards import get_carousel_keyboard
from .utils import get_age, reversed_sex_table
from .base import User


ctx = CtxStorage()
callback_labeler = BotLabeler()


class PayloadRule(ABCRule[BaseMessageMin]):
    def __init__(self, payload: Union[dict, List[dict]]):
        if isinstance(payload, dict):
            payload = [payload]
        self.payload = payload

    async def check(self, event: BaseMessageMin) -> bool:
        payload = event.get_payload_json()
        command = {'cmd': payload.get('cmd')}
        return command in self.payload


async def get_user_photos(user_id: int) -> str:
    """To get user photos, see vkinder.config variable GET_PHOTOS_PARAMS
    :param user_id: vk_user_id
    :return: str attachment
    """
    photos_object = await api.photos.get_all(owner_id=user_id, **GET_PHOTOS_PARAMS)
    photos = photos_object.items
    return ','.join([f'photo{photo.owner_id}_{photo.id}' for photo in photos])


async def search_users(user: User) -> List[UsersUserFull]:
    """Search for users
    :param user: database user
    :return: List['UsersUserFull']
    """
    ctx_users = ctx.get('users')
    if ctx_users:
        return ctx_users

    params = {
        'sex': reversed_sex_table[user.sex_id],
        'hometown': user.city,
        'age_from': user.age,
        'age_to': user.age,
        'status': user.relation_id,
        'fields': SEARCH_USERS_FIELDS,
    }

    suitable_users = []

    search_params = SEARCH_USERS_PARAMS.copy()
    search_params.update(params)

    users_object = await api.users.search(**search_params)
    found_users = users_object.items
    for user_in_issuance in found_users:
        if user_in_issuance.verified:
            continue
        elif user_in_issuance.is_closed:
            continue
        elif user_in_issuance.blacklisted:
            continue
        elif user_in_issuance.blacklisted_by_me:
            continue
        elif user_in_issuance.is_friend:
            continue
        elif not user_in_issuance.can_write_private_message:
            continue
        elif is_viewed(user.user_id, user_in_issuance.id):
            continue
        suitable_users.append(user_in_issuance)
    return suitable_users


async def start_search_users(message: Message):
    """The first search function and sending the first message"""
    user = get_user(message.from_id)
    found_users = await search_users(user)
    if not found_users:
        await message.answer(not_found)
        return

    first_user_found = found_users[0]
    if len(found_users) < 2:
        await message_processing(first_user_found, message=message, last=True)
    else:
        await message_processing(first_user_found, message=message)
        ctx.set('users', found_users[1:])


async def message_processing(user: UsersUserFull, message: Union[MessageEvent, Message], change_message: bool = True,
                             liked: bool = False, last: bool = False) -> None:
    """Processor for preparing, sending or modifying a message
    :param user: 'UsersUserFull'
    :param message: MessageEvent or MessageEvent
    :param change_message: Whether to change the message (only 'MessageEvent', default True)
    :param liked: Does the user (default False)
    :param last: Whether the user is the last user on the list (default False)
    :return:
    """
    carousel_keyboard = get_carousel_keyboard(user.id, last=last, liked=liked)
    photos = await get_user_photos(user.id)
    text = await get_user_text(user)
    if isinstance(message, Message):
        await message.answer(text=text, attachment=photos, keyboard=carousel_keyboard)
        return

    if not isinstance(message, MessageEvent):
        return

    if change_message:
        await message.edit_message(text=text, attachment=photos, keyboard=carousel_keyboard)
    else:
        await message.send_message(text=text, attachment=photos, keyboard=carousel_keyboard)


async def get_user_text(user: UsersUserFull) -> str:
    """Returns a string with information about the user: Name, Last Name, Age """
    name = f'{user.first_name} {user.last_name}'
    age = get_age(user.bdate)
    return f'{name}\nВозраст: {age}'


@callback_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'cmd': 'open_link'}))
async def open_link(event: MessageEvent):
    link = event.object.payload['link']
    await event.open_link(link)


@callback_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'cmd': 'next'}))
async def next_user(event: MessageEvent):
    user = get_user(event.user_id)
    found_users = await search_users(user)
    if not found_users:
        await event.send_message(end_search)
        return
    first_user_found = found_users[1]
    add_view(event.user_id, first_user_found.id)
    if len(found_users) < 2:
        await message_processing(first_user_found, message=event, last=True)
        ctx.set('users', [])
        return

    await message_processing(first_user_found, message=event)
    ctx.set('users', found_users[2:])


@callback_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'cmd': 'like'}))
async def like_user(event: MessageEvent):
    # Processing of the likes, "change the message"
    liked_user_id = event.object.payload.get('user_id')
    liked_users = await api.users.get(liked_user_id, fields=USER_DATA_FIELDS)
    liked_user = liked_users[0]
    await message_processing(liked_user, message=event, liked=True)
    add_like(event.user_id, liked_user_id)

    # Sending a new message
    user = get_user(event.user_id)
    found_users = await search_users(user)
    if not found_users:
        await event.send_message(end_search)
        return

    first_user_found = found_users[0]
    add_view(event.user_id, first_user_found.id)
    if len(found_users) < 2:
        await message_processing(liked_user, message=event, change_message=False, last=True)
        ctx.set('users', [])
        return
    await message_processing(liked_user, message=event, change_message=False)
    ctx.set('users', found_users[1:])
