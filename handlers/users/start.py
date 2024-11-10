from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
import hashlib

from data.db_commands import OrderManager
from loader import dp, bot
from states.form import Form

# Constants
admin_id = 6823612962
CARD_NUMBER = "8600 5704 1707 9125"
CARD_HOLDER = "Ahmedova P"

# Temporary storage for order data
temp_data = {}
order_manager = OrderManager()

# Start command handler
@dp.message_handler(text=["/start", "🛒 Buyurtma berish"])
async def bot_start(message: types.Message):
    await message.answer(
        "Assalomu alaykum  https://t.me/sistersshoppp_1 dan buyurtma bermoqchi bo'lgan modelingizni(rasm) tashlang!",
        reply_markup=ReplyKeyboardRemove()
    )
    await Form.image.set()


# Image handler
@dp.message_handler(content_types=ContentType.ANY, state=Form.image)
async def image(message: types.Message, state: FSMContext):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_type = 'photo'
    elif message.content_type == "video":
        file_id = message.video.file_id
        file_type = 'video'
    else:
        await message.answer("Iltimos, faqat rasm yoki video tashlang!")
        return

    await state.update_data({
        'image': file_id,  # Store the file_id under 'image' key
        'file_type': file_type  # Store the file type
    })
    await message.answer("Razmeringizni kiriting")
    await Form.razmer.set()

# Size handler
@dp.message_handler(state=Form.razmer)
async def razmer(message: types.Message, state: FSMContext):
    razmer = message.text.upper()
    await state.update_data(razmer=razmer)
    await message.answer("Ismingizni kiriting")
    await Form.ism.set()


# Name handler
@dp.message_handler(state=Form.ism)
async def ism(message: types.Message, state: FSMContext):
    ism = message.text
    await state.update_data(ism=ism)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Nomer jo'natish 📱", request_contact=True))
    await message.answer("Telefon raqamingizni yuboring!", reply_markup=keyboard)
    await Form.nomer.set()


# Phone number handler
@dp.message_handler(state=Form.nomer, content_types=ContentType.ANY)
async def nomer(message: types.Message, state: FSMContext):
    try:
        nomer = message.contact.phone_number if message.contact else message.text
        if not nomer.startswith('+'):
            nomer = f'+{nomer}'

        await state.update_data(nomer=nomer)

        # Payment method selection keyboard
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(text="Naqt", callback_data="payment_naqt"),
            InlineKeyboardButton(text="Plastik", callback_data="payment_plastik")
        )
        await message.answer("To'lov turini tanlang:", reply_markup=keyboard)
        await Form.payment.set()
    except Exception as e:
        await message.answer("Telefon raqami noto'g'ri formatda. Iltimos qayta urinib ko'ring.")
        return


# Payment method handler
@dp.callback_query_handler(Text(startswith="payment_"), state=Form.payment)
async def process_payment_choice(callback_query: types.CallbackQuery, state: FSMContext):
    choice = callback_query.data.split("_")[1]

    if choice == "naqt":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text="Manzilni yuborish", request_location=True))
        await callback_query.message.answer("Manzilingizni yuboring!", reply_markup=keyboard)
        await Form.manzil.set()
    elif choice == "plastik":
        await callback_query.message.answer(
            f"<pre>{CARD_NUMBER}</pre>\n<b>{CARD_HOLDER}</b> nomiga to'lovni amalga oshiring va "
            "to'lov chekning skrinshotini yuboring.",
            parse_mode="HTML"
        )
        await Form.chek.set()

    await callback_query.answer()


# Payment screenshot handler
@dp.message_handler(state=Form.chek, content_types=ContentType.ANY)
async def process_chek_screenshot(message: types.Message, state: FSMContext):
    if message.content_type != 'photo':
        await message.answer("Iltimos, to'lov chekining rasmini yuboring!")
        return

    data = await state.get_data()
    user_data = {
        "ism": data.get("ism"),
        "razmer": data.get("razmer"),
        "nomer": data.get("nomer"),
        "file_id": data.get("image"),
        "user_id": message.from_user.id
    }


    if not all(user_data.values()):
        await message.answer("Ma'lumotlar to'liq emas! Iltimos, qaytadan urinib ko'ring.")
        await state.finish()
        return

    # Generate unique order ID
    order_id = hashlib.md5(str(user_data).encode()).hexdigest()[:10]
    temp_data[order_id] = user_data

    try:
        # Send payment receipt to admin
        inline_keyboard = InlineKeyboardMarkup()
        inline_keyboard.add(InlineKeyboardButton(
            text="Tasdiqlash ✅",
            callback_data=f"confirm_{order_id}"
        ))

        await bot.send_photo(
            chat_id=admin_id,
            photo=message.photo[-1].file_id,
            caption=(
                f"Yangi to'lov cheki yuborildi.\n"
                f"Ism: {user_data['ism']}\n"
                f"Razmer: {user_data['razmer']}\n"
                f"Telefon: {user_data['nomer']}"
            ),
            reply_markup=inline_keyboard
        )
        await message.answer("To'lov cheki Adminga yuborildi. Admin tasdiqlashini kuting!")
    except Exception as e:
        await message.answer("Xatolik yuz berdi. Iltimos qayta urinib ko'ring.")
        print(f"Error in payment processing: {e}")

    await state.finish()


# Payment confirmation handler
@dp.callback_query_handler(lambda c: c.data.startswith("confirm_"))
async def confirm_payment(callback_query: types.CallbackQuery):
    order_id = callback_query.data.split("_")[1]
    user_data = temp_data.get(order_id)

    if not user_data:
        await callback_query.answer("Ma'lumot topilmadi.", show_alert=True)
        return

    try:
        await callback_query.message.reply("To'lov tasdiqlandi!")
        # Send confirmation to admin


        # Send confirmation to client with continue button
        inline_keyboard = InlineKeyboardMarkup()
        inline_keyboard.add(InlineKeyboardButton(
            text="Davom etish",
            callback_data=f"continue_{order_id}"
        ))

        await bot.send_photo(
            chat_id=user_data["user_id"],
            photo=user_data["file_id"],
            caption=(
                f"Hurmatli mijoz to'lovingiz tasdiqlandi!\n"
                f"Ism: {user_data['ism']}\n"
                f"Razmer: {user_data['razmer']}\n"
                f"Telefon: {user_data['nomer']}"
            ),
            reply_markup=inline_keyboard
        )

        await callback_query.answer("To'lov tasdiqlandi!", show_alert=True)
    except Exception as e:
        await callback_query.answer("Xatolik yuz berdi.", show_alert=True)
        print(f"Error in payment confirmation: {e}")


# Continue process handler
@dp.callback_query_handler(lambda c: c.data.startswith("continue_"))
async def continue_process(callback_query: types.CallbackQuery, state: FSMContext):
    order_id = callback_query.data.split("_")[1]
    user_data = temp_data.get(order_id)

    if not user_data:
        await callback_query.answer("Ma'lumot topilmadi.", show_alert=True)
        return

    try:
        # Store all necessary data in state
        await state.update_data({
            'ism': user_data['ism'],
            'razmer': user_data['razmer'],
            'nomer': user_data['nomer'],
            'image': user_data['file_id'],  # Make sure we store the file_id
            'file_type': 'photo',  # Add file type
            'user_id': user_data['user_id']
        })

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text="Manzilni yuborish", request_location=True))

        await callback_query.message.answer("Manzilingizni yuboring!", reply_markup=keyboard)
        await Form.manzil.set()
        await callback_query.answer()
    except Exception as e:
        await callback_query.answer("Xatolik yuz berdi.", show_alert=True)
        print(f"Error in continue process: {e}")



# Location handler
@dp.message_handler(state=Form.manzil, content_types=ContentType.LOCATION)
async def manzil(message: types.Message, state: FSMContext):
    if not message.location:
        await message.answer("Iltimos, manzilingizni yuboring!")
        return

    try:
        data = await state.get_data()

        user_id = message.from_user.id
        user_link = f"tg://user?id={user_id}"

        inline_keyboard = InlineKeyboardMarkup()
        inline_keyboard.add(InlineKeyboardButton(
            text="Buyurtma keldi ✅",
            callback_data=f"ord_{user_id}_photo"
        ))

        caption = (
            f"Yangi buyurtma!\n"
            f"Ism: {data.get('ism')}\n"
            f"Razmer: {data.get('razmer')}\n"
            f"Telefon raqami: {data.get('nomer')}\n"
            f"[Foydalanuvchi bilan bog'lanish]({user_link})"
        )

        await bot.send_photo(
            chat_id=admin_id,
            photo=data.get("image"),
            caption=caption,
            reply_markup=inline_keyboard,
            parse_mode="Markdown"
        )

        # Remove temporary order data
        order_id = hashlib.md5(str(data).encode()).hexdigest()[:10]
        order_manager.delete_temp_order_data(order_id)

        await message.answer("Buyurtmangiz qabul qilindi, tez orada siz bilan bog'lanishadi!")
    except Exception as e:
        await message.answer("Xatolik yuz berdi.")
        print(f"Error in location handler: {e}")

    await state.finish()
