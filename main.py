"""
Telegram Tanyslyk Bot (Leonardo Daivinchik klony)
Dorediji: Python 3 + Aiogram 3.x + aiosqlite
100% Mugt serwerlerde (Render, Railway, Fly.io, Termux) isleyar.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

from database import init_db
from handlers import router

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "8636080548:AAF0ncAxbjcctPInOgiFmgiBG_vG9bfad0M")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Bot basladylayar...")

    # Maglumat bazasyny doretmek / barlaamak
    await init_db()

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Boty isletmek (Polling)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot saklandy.")
