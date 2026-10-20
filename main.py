"""
Telegram Tanyslyk Bot (Leonardo Daivinchik klony)
Modern Admin Dolandyrys Paneli + Awto-Oyaryjy (Self-Pinger)
100% Mugt Render Web Service we Kompyuter ucin tayyar!
"""

import asyncio
import logging
import os
import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from database import init_db, get_stats, get_recent_users
from handlers import router

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "8636080548:AAF0ncAxbjcctPInOgiFmgiBG_vG9bfad0M")
PORT = int(os.getenv("PORT", 8080))
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

async def handle_ping(request):
    """Render barlagy we Canly Web Admin Dashboard"""
    stats = await get_stats()
    recent = await get_recent_users(5)
    
    recent_html = "".join([
        f"<tr><td style='padding:10px;border-bottom:1px solid #334155;'>👤 {u['name']} ({u['age']})</td>"
        f"<td style='padding:10px;border-bottom:1px solid #334155;'>{u['city']}</td>"
        f"<td style='padding:10px;border-bottom:1px solid #334155;'>{'@' + u['username'] if u.get('username') else 'Ýok'}</td>"
        f"<td style='padding:10px;border-bottom:1px solid #334155;'>{'🚫 Banned' if u.get('is_banned') else ('⭐ VIP' if u.get('is_vip') else '✅ Işjeň')}</td></tr>"
        for u in recent
    ])

    html = f"""
    <!DOCTYPE html>
    <html lang="tk">
    <head>
        <meta charset="UTF-8">
        <title>Daivinchik Bot - Live Admin Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            .header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; border-bottom: 1px solid #1e293b; padding-bottom: 16px; }}
            .status {{ background: #059669; color: white; padding: 4px 12px; border-radius: 99px; font-size: 12px; font-weight: bold; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }}
            .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 18px; }}
            .card-title {{ font-size: 12px; color: #94a3b8; margin-bottom: 6px; text-transform: uppercase; font-weight: 600; }}
            .card-value {{ font-size: 28px; font-weight: 800; color: #38bdf8; }}
            table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 16px; overflow: hidden; }}
            th {{ background: #334155; text-align: left; padding: 12px 10px; font-size: 13px; color: #cbd5e1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1 style="margin:0; font-size: 22px;">🤖 Daivinchik Bot Admin Dashboard</h1>
                    <p style="margin:4px 0 0; color: #94a3b8; font-size: 13px;">Live Server & Maglumat Bazasy</p>
                </div>
                <div class="status">● 24/7 IŞJEŇ</div>
            </div>

            <div class="grid">
                <div class="card">
                    <div class="card-title">Jemi Ulanyjylar</div>
                    <div class="card-value">{stats['total_users']}</div>
                </div>
                <div class="card">
                    <div class="card-title">Oglanlar / Gyzlar</div>
                    <div class="card-value" style="font-size:20px; color:#a855f7;">👨 {stats['male_users']} | 👩 {stats['female_users']}</div>
                </div>
                <div class="card">
                    <div class="card-title">Jemi Like-lar</div>
                    <div class="card-value" style="color:#f43f5e;">❤️ {stats['total_likes']}</div>
                </div>
                <div class="card">
                    <div class="card-title">Gabat Gelmeler (Matches)</div>
                    <div class="card-value" style="color:#10b981;">🎉 {stats['total_matches']}</div>
                </div>
            </div>

            <div class="card">
                <h3 style="margin-top:0; font-size:16px;">👥 Soňky Goşulan 5 Anketa</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Ady / Ýaşy</th>
                            <th>Şäheri</th>
                            <th>Username</th>
                            <th>Ýagdaýy</th>
                        </tr>
                    </thead>
                    <tbody>
                        {recent_html if recent else "<tr><td colspan='4' style='padding:16px;text-align:center;color:#64748b;'>Häzirlikçe ulanyjy ýok. Telegramdan /start basyň!</td></tr>"}
                    </tbody>
                </table>
            </div>
            
            <p style="text-align:center; color:#64748b; font-size:12px; margin-top:24px;">
                💡 Maslahat: Telegramda <b>/admin</b> komandasyny ýazyp hemme zady göni telefondan dolandyryp bilersiňiz!
            </p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"🌐 Web Admin Dashboard {PORT} portda açyldy!")

async def self_ping_keep_alive():
    """AWTO-OÝARYJY: Her 8 minutdan özüni çagyryp, Render-i 24/7 oýa saklaýar!"""
    await asyncio.sleep(30)
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    target_url = render_url if render_url else f"http://127.0.0.1:{PORT}"
    
    print(f"⏰ Awto-Oýaryjy işe goşuldy: {target_url}")
    while True:
        try:
            await asyncio.sleep(480) # 8 minut
            async with aiohttp.ClientSession() as session:
                async with session.get(target_url, timeout=10) as resp:
                    print(f"🔄 Awto-oýaryjy: Serwer 24/7 oýa saklandy (Status: {resp.status})")
        except Exception:
            pass

async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Daivinchik boty başladylýar...")

    await init_db()

    if os.getenv("PORT"):
        await start_web_server()
        asyncio.create_task(self_ping_keep_alive())

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Bot üstünlikli işe girizildi! Telegramdan /start ýa-da /admin basyň.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot saklandy.")
