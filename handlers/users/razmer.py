from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from loader import dp
from states.form import Form


@dp.message_handler(state=Form.razmer)
async def razmer(message: types.Message, state: FSMContext):
    razmer = message.text
    await state.update_data(razmer=razmer)

    await message.answer("Ismingizni kiriting")
    await Form.ism.set()