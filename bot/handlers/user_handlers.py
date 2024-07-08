import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
from aiogram import types
from aiogram import F
from aiogram import Bot
from aiogram.fsm.state import default_state
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram import Router
from openai import PermissionDeniedError

from bot.filters.check_requests import Check_requests
from bot.lexicon.lexicon_ru import LEXICON_RU
from bot.external_services.chatgpt4 import OpenaiSession
from bot.models.methods import minus_request_count, sql_add_user

#работа с машиной состояний
from bot.states.states import UseGPT
from aiogram.fsm.context import FSMContext

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)

# Устанавливаем логгеру уровень `WARNING`
logger.setLevel(logging.WARNING)

# Добавляем handler к логгеру
logger.addHandler(TimedRotatingFileHandler(f'logs/bot_logs.log', when='D', backupCount=4))

# Инициализируем роутер уровня модуля
router: Router = Router()


@router.message(Command(commands=['start']))
@router.callback_query(lambda callback_query: callback_query.data == 'back')
async def process_start_command(message: types.Message | types.CallbackQuery, state: FSMContext) -> None:
    #print(message.model_dump_json())
    #await message.answer(message.model_dump_json())
    if isinstance(message, types.CallbackQuery):
        await message.message.answer_photo(FSInputFile("ava.jpg"), caption=LEXICON_RU['/start'])
        await message.answer()
    else:
        await message.answer_photo(FSInputFile("ava.jpg"), caption=LEXICON_RU['/start'])
        await sql_add_user(message)
    await state.clear()


@router.message(Command(commands=['gpt']))
async def process_gpt_command(message: types.Message | types.CallbackQuery, state: FSMContext) -> None:
    try:
        session = OpenaiSession()
        await state.update_data(session=session)
        await message.answer(text=LEXICON_RU['gpt_start_dialog'])
        await state.set_state(UseGPT.state1_user_request)
    except PermissionDeniedError:
        await message.answer(text="Запрос из вашей страны не поддерживается")


@router.message(Command(commands=['cancel']), UseGPT.state1_user_request)
async def context_clear(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    session: OpenaiSession = data['session']
    await session.clear_context()
    await state.clear()
    await message.answer(text=LEXICON_RU['/cancel'])


#@router.message(F.text, UseGPT.state1_user_request, RequestChecker()) #, SubChecker()
@router.message(F.text, UseGPT.state1_user_request, Check_requests())
async def send_message(message: types.Message, bot: Bot, state: FSMContext) -> None:
    #logger.info(f"Пользователь {message.from_user.username}(id={message.from_user.id}) спрашивает: {message.text}")
    content = message.text
    data = await state.get_data()
    session: OpenaiSession = data['session']
    await session.add_message_to_thread(content)
    await session.run_assistant()
    waiting_message: types.Message = await message.answer(text=LEXICON_RU['loading_model'])
    await bot.send_chat_action(message.chat.id, 'typing')  # Эффект набора сообщения "Печатает..."
    try:
        result = await session.wait_run_assistant()
        if result == 'completed':
            answer_gpt = session.response_gpt()
            await minus_request_count(message)
            await waiting_message.edit_text(await answer_gpt)
    except asyncio.TimeoutError:
    # Обработка случая, когда статус не изменился в течение timeout (сек)
        await waiting_message.edit_text(text=LEXICON_RU['no_response'])




