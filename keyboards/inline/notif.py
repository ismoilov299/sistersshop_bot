from aiogram import types

from loader import bot, dp


@dp.callback_query_handler(lambda c: c.data.startswith("ord_"))
async def process_order_callback(callback_query: types.CallbackQuery):
    try:
        data_parts = callback_query.data.split('_')
        if len(data_parts) != 4:
            raise ValueError("Button_data_invalid")

        _, user_id, file_id, file_type = data_parts

        if file_type == 'photo':
            await bot.send_photo(
                chat_id=user_id,
                photo=file_id,
                caption="Sizning buyurtmangiz keldi! 📦"
            )
        else:
            await bot.send_video(
                chat_id=user_id,
                video=file_id,
                caption="Sizning buyurtmangiz keldi! 📦"
            )

        await bot.answer_callback_query(callback_query.id, text="Xabar mijozga yuborildi ✅")

        # Removing the inline keyboard
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )
    except ValueError as e:
        print(f"Button_data_invalid: {e}")
        await bot.answer_callback_query(callback_query.id, text="Xatolik yuz berdi ❌", show_alert=True)
    except Exception as e:
        print(f"Error in callback: {e}")
        await bot.answer_callback_query(callback_query.id, text="Xatolik yuz berdi ❌", show_alert=True)
