from aiogram.fsm.state import State, StatesGroup, default_state


class UseGPT(StatesGroup):
    state1_user_request = State()


class UseTranslate(StatesGroup):
    state_start_translate = State()


class AdminPanel(StatesGroup):
    admin_send_message = State()
