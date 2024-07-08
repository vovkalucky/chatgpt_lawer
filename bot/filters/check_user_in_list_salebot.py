import asyncio

import requests
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.keyboards.user_keyboards import get_pay_kb
from bot.lexicon.lexicon_ru import LEXICON_RU
from bot.config_data.config import load_config

config = load_config()


class SubUserInList(BaseFilter):
    async def __call__(self, msg: Message, bot: Bot) -> bool:
        in_list_of_pay = await check_user_in_list("539172", msg.from_user.id)
        sub = await check_sub(bot, config.tg_bot.group_id, msg.from_user.id)
        print(in_list_of_pay)
        print(sub)
        if in_list_of_pay or sub:
            return True
        await msg.answer(LEXICON_RU['no_subscription'])
        return False


async def check_user_in_list(list_id: int, user_id: int) -> bool:
    try:
        response = requests.get(f"https://chatter.salebot.pro/api/eb0010347900a3d068dd9c5c80e4044d/get_clients?list={list_id}")
        clients = response.json()['clients']
        platform_ids = [int(client['platform_id']) for client in clients]
        print(platform_ids)
        if user_id in platform_ids:
            return True
        else:
            return False
    except TelegramBadRequest:
        return False

async def check_sub(bot: Bot, channel_id: int, user_id: int) -> bool:
    try:
        user = await bot.get_chat_member(channel_id, user_id)
        return user.status != "left"
    except TelegramBadRequest:
        return False

# if __name__ == '__main__':
#     try:
#         asyncio.run(check_user_in_list(538884, 1873052013))
#     except KeyboardInterrupt:
#         print("Stop bot")