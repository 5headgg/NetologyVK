from datetime import datetime
from vkbottle.bot import Bot, BotLabeler
from chat import chat_labeler
from callbacks import callback_labeler
from config import state_dispenser, COMMUNITY_TOKEN
from states import states_labeler
from models import create_tables, get_all_users
import asyncio

bot_labeler = BotLabeler()
labelers = (chat_labeler, states_labeler, callback_labeler)
for labeler in labelers:
    bot_labeler.load(labeler)

bot = Bot(token=COMMUNITY_TOKEN, labeler=bot_labeler, state_dispenser=state_dispenser)


async def check_user_actions():
    while True:
        users = await get_all_users()
        for user in users:
            await bot.api.messages.send(user_id=user.user_id,
                                        message='До свидания!',
                                        random_id=int(datetime.now().timestamp() * 1000))
        await asyncio.sleep(5)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(create_tables(), bot.run_polling(), check_user_actions()))


if __name__ == '__main__':
    main()
