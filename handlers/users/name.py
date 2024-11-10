from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from states.form import Form


@dp.message_handler(state=Form.ism)
async def ism(message: types.Message, state: FSMContext):
    ism = message.text
    await state.update_data(ism=ism)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Nomer jo'natish 📱", request_contact=True))
    await message.answer("Telefon raqamingizni yuboring!", reply_markup=keyboard)
    await Form.nomer.set()