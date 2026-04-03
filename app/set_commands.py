from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Перезапустить бота"),
        BotCommand(command="status", description="Инфо о скане")
    ]
    await bot.set_my_commands(commands)