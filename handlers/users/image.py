from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from loader import dp
from states.form import Form


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
        'image': file_id,
        'file_type': file_type
    })

    await message.answer("Razmeringizni kiriting")
    await Form.razmer.set()