# -*- coding: utf-8 -*-
"""
:authors: kanewi11
:license:  GPL-3.0 license, see LICENSE file

:copyright: (c) 2022 kanewi11
"""

__author__ = 'kanewi11'
__email__ = 'blacknekit11@gmail.com'
__all__ = ['run']

import logging

from vkbottle.bot import Bot

from .base import create_tables
from .chat import chat_labeler
from .callbacks import callback_labeler
from .states import states_labeler
from .callbacks import callback_labeler
from .config import state_dispenser, base_labeler, COMMUNITY_TOKEN, LOGS_DIR


LOGS_DIR.mkdir(exist_ok=True)

# Logs
loggers = ['vkinder', 'vkbottle']
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')
for logger_name in loggers:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)
    log_filepath = LOGS_DIR.joinpath(logger_name + '.log')
    handler = logging.FileHandler(log_filepath)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.warning('Start VKinder!')

labelers = [chat_labeler, states_labeler, callback_labeler, callback_labeler]
for labeler in labelers:
    base_labeler.load(labeler)

bot = Bot(token=COMMUNITY_TOKEN, labeler=base_labeler, state_dispenser=state_dispenser)


def run():
    create_tables()
    bot.run_forever()
