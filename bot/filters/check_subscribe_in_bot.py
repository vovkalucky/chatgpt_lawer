import types

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import BaseFilter
#from aiogram.types import Message
from aiogram import types
from bot.lexicon.lexicon_ru import LEXICON_RU
from bot.config_data.config import load_config
from bot.models.methods import check_subscribe

config = load_config()


class PayChecker(BaseFilter):
    async def __call__(self, msg: types.Message | types.CallbackQuery) -> bool:
        subscribe_status = await check_subscribe(msg)
        print(subscribe_status)
        if subscribe_status:
            return True
        await msg.answer(LEXICON_RU['no_subscription'])
        return False


# async def check_pay(msg: types.Messa) -> bool:
#     try:
#         user = await check_subscribe(msg):
#
#         return user.status != "left"
#     except TelegramBadRequest:
#         return False