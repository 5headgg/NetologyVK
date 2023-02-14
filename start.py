from vkbottle.bot import Bot, BotLabeler
from chat import chat_labeler
from callbacks import callback_labeler
from config import state_dispenser, COMMUNITY_TOKEN
from states import states_labeler
from models import create_tables


def main():
    create_tables()

    bot_labeler = BotLabeler()
    labelers = (chat_labeler, states_labeler, callback_labeler)
    for labeler in labelers:
        bot_labeler.load(labeler)

    bot = Bot(token=COMMUNITY_TOKEN, labeler=bot_labeler, state_dispenser=state_dispenser)
    bot.run_forever()


if __name__ == '__main__':
    main()
