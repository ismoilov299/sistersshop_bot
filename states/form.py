from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    image = State()
    razmer = State()
    ism = State()
    nomer = State()
    payment = State()
    manzil = State()
    chek = State()
