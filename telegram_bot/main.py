import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from handlers import router

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=Config.TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_routers(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
