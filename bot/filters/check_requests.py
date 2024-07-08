from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.lexicon.lexicon_ru import LEXICON_RU
from bot.models.methods import check_user_request_count


class Check_requests(BaseFilter):
    async def __call__(self, msg: Message, bot: Bot) -> bool:
        request_count = await check_user_request_count(msg)
        if request_count > 0:
            return True
        await msg.answer(LEXICON_RU['response_null'])
        return False