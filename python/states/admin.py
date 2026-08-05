from aiogram.fsm.state import State, StatesGroup


class Admin(StatesGroup):
    main = State()
    users = State()
    queries = State()
    limits = State()
    waiting_for_limits = State()
    logs = State()
    log_format = State()
