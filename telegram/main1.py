import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
from database import on_startup, on_shutdown
from handlers import setup_handlers

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

setup_handlers(dp)

# Запуск бота
async def main():
    await on_startup(dp)
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown(dp)

if __name__ == '__main__':
    asyncio.run(main())