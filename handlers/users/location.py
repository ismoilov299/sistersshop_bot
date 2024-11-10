from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from handlers.users.start import admin_id
from loader import dp, bot
from states.form import Form


@dp.message_handler(state=Form.manzil, content_types=ContentType.ANY)
async def manzil(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ism = data.get("ism")
    razmer = data.get("razmer")
    nomer = data.get("nomer")
    file_id = data.get("image")
    file_type = data.get("file_type", 'photo')

    lat = message.location.latitude
    lon = message.location.longitude
    user_id = message.from_user.id
    user_link = f"tg://user?id={user_id}"
    user_full_name = message.from_user.full_name

    callback_data = f"ord_{user_id}_{file_type}"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton(
        text="Buyurtma keldi ✅",
        callback_data=callback_data
    ))

    try:
        if file_type == 'photo':
            await bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=f"Yangi buyurtma!\n"
                        f"Ism: {ism}\n"
                        f"Razmer: {razmer}\n"
                        f"Telefon raqami: {nomer}\n"
                        f'Telegram: <a href="{user_link}">{user_full_name}</a>',
                parse_mode="html",
                reply_markup=inline_keyboard
            )
        else:
            await bot.send_video(
                chat_id=admin_id,
                video=file_id,
                caption=f"Yangi buyurtma!\n"
                        f"Ism: {ism}\n"
                        f"Razmer: {razmer}\n"
                        f"Telefon raqami: {nomer}\n"
                        f'Telegram: <a href="{user_link}">{user_full_name}</a>',
                parse_mode="html",
                reply_markup=inline_keyboard
            )

        await bot.send_location(chat_id=admin_id, longitude=lon, latitude=lat)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text="🛒 Buyurtma berish"))

        await message.answer("Buyurtmangiz qabul qilindi!", reply_markup=keyboard)
        await state.finish()

    except Exception as e:
        print(f"Error: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")
        await state.finish()