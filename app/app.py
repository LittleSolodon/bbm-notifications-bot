import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.routers import router
from app.services.polling.manager import PollingManager
import httpx
from app import set_commands
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    bot = Bot(os.getenv("BOT_TOKEN"))

    polling_manager = PollingManager(bot)
    dp = Dispatcher(storage=MemoryStorage(), polling_manager=polling_manager)
    dp.include_router(router)
    await set_commands.set_commands(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())