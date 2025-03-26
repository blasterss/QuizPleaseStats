import asyncpg
import os

async def on_startup(dp):
    dp['db'] = await asyncpg.create_pool(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Закрытие подключения к базе данных при остановке бота
async def on_shutdown(dp):
    await dp['db'].close()
