import os
import logging
from pathlib import Path

from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler


BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR.joinpath('logs')

# comm token in Vk
COMMUNITY_TOKEN = os.getenv('COMM_TOKEN')
# User token
USER_TOKEN = os.getenv('USER_TOKEN')

# db adress
DSN = 'sqlite:///vkinder.db'

AGE_FROM = 16
AGE_TO = 50




USER_DATA_FIELDS = [
    'sex',
    'city',
    'bdate',
    'relation',
]


SEARCH_USERS_PARAMS = {
    'offset': 0,
    'count': 1000,
    'city': None,
    'sex': None,
    'age_from': None,
    'age_to': None,
    'has_photo': 1,
    'status': None,
}


SEARCH_USERS_FIELDS = [
    'is_friend',
    'is_closed',
    'blacklisted',
    'blacklisted_by_me',
    'can_write_private_message',
    'bdate',
    'verified',
]


GET_PHOTOS_PARAMS = {
    'count': 3,
    'skip_hidden': 1
}

# vkbottle API
api = API(USER_TOKEN)

# vkbottle Labeler
base_labeler = BotLabeler()

# vkbottle StateDispenser
state_dispenser = BuiltinStateDispenser()
