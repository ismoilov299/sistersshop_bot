from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Botni ishga tushurish"),
            types.BotCommand("cancel", "Barcha ammalarni bekor qiladi"),
            types.BotCommand("help", "Yordam"),
        ]
    )
