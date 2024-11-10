from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from loader import dp
from states.form import Form


@dp.message_handler(state=Form.nomer, content_types=ContentType.ANY)
async def nomer(message: types.Message, state: FSMContext):
    try:
        nomer = message.contact.phone_number
    except AttributeError:
        nomer = message.text


    if not nomer.startswith('+'):
        nomer = f'+{nomer}'

    await state.update_data(nomer=nomer)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Manzilni yuborish", request_location=True))
    await message.answer("Manzilingizni yuboring!", reply_markup=keyboard)
    await Form.manzil.set()