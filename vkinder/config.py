import os
import logging
from pathlib import Path

from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler


# Base directory and log directory
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR.joinpath('logs')

# Your community token in VKontakte
COMMUNITY_TOKEN = os.getenv('COMMUNITY_TOKEN')

# In this link the necessary scope is already passed, replace client_id to get the token
# https://oauth.vk.com/authorize?client_id=1&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,photos,offline&response_type=token&v=5.131&state=123456
USER_TOKEN = os.getenv('USER_TOKEN')

# DSN - data source name (db address)
DSN = 'sqlite:///vkinder.db'

# Age restrictions
AGE_FROM = 16
AGE_TO = 50

# Search options and fields

# Fields for retrieving user data
USER_DATA_FIELDS = [
    'sex',
    'city',
    'bdate',
    'relation',
]

# Options for finding VK users
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

# Fields that must be present when searching for VK users
SEARCH_USERS_FIELDS = [
    'is_friend',
    'is_closed',
    'blacklisted',
    'blacklisted_by_me',
    'can_write_private_message',
    'bdate',
    'verified',
]

# Parameters for receiving photos of a VK user
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
