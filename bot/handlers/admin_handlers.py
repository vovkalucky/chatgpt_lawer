from aiogram import types

#работа с машиной состояний
from bot.states.states import AdminPanel
from aiogram.fsm.context import FSMContext

from bot.keyboards.admin_keyboards import *
from aiogram.filters import Command
from aiogram import F, Router
from bot.lexicon.lexicon_ru import LEXICON_RU
from bot.models.methods import check_user_request_count, get_users, count_user_for_period, count_premium_users
from bot.config_data.config import load_config
config = load_config()

#Инициализируем роутер уровня модуля
router: Router = Router()


@router.message(Command(commands=['admin']), F.from_user.id.in_(config.tg_bot.admin_ids))
async def admin_menu(message: types.Message) -> None:
    await message.answer(text=LEXICON_RU['admin_menu'], reply_markup=get_admin_menu_kb())


@router.callback_query(lambda callback_query: callback_query.data == 'admin_response', F.from_user.id.in_(config.tg_bot.admin_ids))
async def admin_check_request(callback: types.CallbackQuery) -> None:
    count_request = await check_user_request_count(callback)
    await callback.message.answer(text=f"У вас осталось запросов к ChatGPT: {count_request}", reply_markup=get_admin_menu_kb())
    await callback.answer()


@router.callback_query(lambda callback_query: callback_query.data == 'admin_users', F.from_user.id.in_(config.tg_bot.admin_ids))
async def admin_get_users(callback: types.CallbackQuery) -> None:
    count_users, all_users = await get_users()
    await callback.message.answer(text=f"Пользователей: {count_users}\n\n <b>id(username), дата регистрации, осталось запросов</b>")
    all_users_dict = ""
    for i in range(0, count_users):
        all_users_dict += f"{i+1}) {all_users[i][0]}({all_users[i][1]}), {all_users[i][2][0:10]}, {all_users[i][3]}\n"
    await callback.message.answer(text=f"{all_users_dict}", reply_markup=get_admin_menu_kb())
    await callback.answer()


@router.callback_query(lambda callback_query: callback_query.data == 'admin_send_message', F.from_user.id.in_(config.tg_bot.admin_ids))
async def admin_write_message(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=LEXICON_RU['admin_send_message'])
    await state.set_state(AdminPanel.admin_send_message)


@router.message(F.from_user.id.in_(config.tg_bot.admin_ids), AdminPanel.admin_send_message)
async def admin_send_message(message: types.Message, state: FSMContext, bot) -> None:
    text = message.text
    count, active_users = await get_users()
    ids_active_users = [user[0] for user in active_users]
    print(ids_active_users)
    for i in ids_active_users:
        try:
            await bot.send_message(i, text)
        except:
            await message.answer(f"❌ Пользователю {i} рассылка не совершена!")
    await message.answer("✅ Рассылка завершена!")
    await state.clear()


@router.callback_query(lambda callback_query: callback_query.data == 'analytic', F.from_user.id.in_(config.tg_bot.admin_ids))
async def admin_analytic(callback: types.CallbackQuery) -> None:
    count_of_users, all_users = await get_users()
    users_today = await count_user_for_period(1)
    users_week = await count_user_for_period(7)
    users_month = await count_user_for_period(30)
    users_premium_acc = await count_premium_users()
    await callback.message.answer(text=f"<b>🎂 Дата создания бота:</b> 11.12.2023\n"
                                       f"<b>👥 Число подписчиков:</b> {count_of_users}\n\n"
                                       f"<b>Подписчиков за сутки:</b> {users_today}\n"
                                       f"<b>Подписчиков за неделю:</b> {users_week}\n"
                                       f"<b>Подписчиков за месяц:</b> {users_month}\n"
                                       f"<b>⭐ Подписчиков с премиум аккаунтом:</b> {users_premium_acc}")
    await callback.answer()