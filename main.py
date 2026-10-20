"""
Telegram Tanyslyk Bot (Leonardo Daivinchik klony)
Render.com Free Web Service we Kompyuter ucin 100% tayyar!
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from database import init_db
from handlers import router

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "8636080548:AAF0ncAxbjcctPInOgiFmgiBG_vG9bfad0M")
PORT = int(os.getenv("PORT", 8080))

# Render.com Free Web Service barlagy üçin ýönekeý jogap:
async def handle_ping(request):
    return web.Response(text="Daivinchik Bot is alive and running 24/7! 🚀")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"🌐 Render.com üçin Web serwer {PORT} portda açyldy!")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Bot başladylýar...")

    # Maglumat bazasyny taýýarlamak
    await init_db()

    # Eger Render-de (PORT bar bolsa), web serweri hem işe goşýarys
    if os.getenv("PORT"):
        await start_web_server()

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Boty işletmek (Polling)
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Bot üstünlikli işe girizildi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot saklandy.")
