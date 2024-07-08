from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.lexicon.lexicon_ru import LEXICON_RU
from bot.config_data.config import load_config

config = load_config()


class SubChecker(BaseFilter):
    async def __call__(self, msg: Message, bot: Bot) -> bool:
        sub = await check_sub(bot, config.tg_bot.group_id, msg.from_user.id)
        if sub:
            return True
        await msg.answer(LEXICON_RU['subscribe_channel'])
        return False


async def check_sub(bot: Bot, channel_id: int, user_id: int) -> bool:
    try:
        user = await bot.get_chat_member(channel_id, user_id)
        return user.status != "left"
    except TelegramBadRequest:
        return False