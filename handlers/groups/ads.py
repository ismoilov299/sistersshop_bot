import asyncio

from aiogram import types
from aiogram.types import ContentType
from loader import dp
from datetime import datetime, timedelta

from datetime import datetime, timedelta


@dp.message_handler(content_types=ContentType.ANY, chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def ads(message: types.Message):
    if message.text and message.text.startswith('@'):
        try:
            # Xabarni o'chirish
            await message.delete()

            # Foydalanuvchini 5 daqiqaga cheklash
            until_date = datetime.now() + timedelta(minutes=5)

            # Foydalanuvchini vaqtinchalik cheklash
            await message.chat.restrict(
                user_id=message.from_user.id,
                permissions=types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False
                ),
                until_date=until_date
            )

            # Ogohlantirish xabarini yuborish
            warn_msg = await message.answer(
                f"@{message.from_user.username} reklama tashlangani uchun:\n"
                f"1. Xabar o'chirildi\n"
                f"2. 5 daqiqaga yozish cheklandi!"
            )

            # Ogohlantirish xabarini 10 soniyadan keyin o'chirish
            await asyncio.sleep(10)
            await warn_msg.delete()

        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")
            await message.reply("Xatolik yuz berdi.")
    else:
        print(message.text)
        # await message.answer("Reklama")