from aiogram.fsm.state import State, StatesGroup


class AddQuery(StatesGroup):
    waiting_for_tag = State()
    waiting_for_value = State()
    waiting_for_edit = State()
    editing = State()
    waiting_for_delete = State()
