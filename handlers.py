"""
FSM, Daivinchik logikasy we Modern Admin Dolandyryş Paneli
"""

import os
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb

router = Router()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

class Registration(StatesGroup):
    age = State()
    gender = State()
    target_gender = State()
    city = State()
    name = State()
    photo = State()
    bio = State()

class FeedState(StatesGroup):
    browsing = State()
    send_comment = State()

class AdminStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_broadcast = State()
    waiting_for_ban_id = State()
    waiting_for_vip_id = State()

# ==================== MODERN ADMIN DOLANDYRYŞ PANELI ====================

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        stats = await db.get_stats()
        text = (
            "👑 **MODERN ADMIN DOLANDYRYŞ PANELI**\n\n"
            "Salam, Hormatly Admin! Aşakdaky düwmeler arkaly boty dolandyryp bilersiňiz:"
        )
        await message.answer(text, reply_markup=kb.admin_main_keyboard())
    else:
        await message.answer(
            "🔒 **Admin Paneline Giriş**\n\n"
            "Admin parolyňyzy ýazyň (Standart parol: `admin123`):"
        )
        await state.set_state(AdminStates.waiting_for_password)

@router.message(AdminStates.waiting_for_password)
async def process_admin_password(message: Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        if message.from_user.id not in ADMIN_IDS:
            ADMIN_IDS.append(message.from_user.id)
        await state.clear()
        await message.answer(
            "🔓 **Giriş Üstünlikli!** Siziň ID-ňiz admin sanawyna goşuldy.\n\n"
            "👑 **MODERN ADMIN DOLANDYRYŞ PANELI**",
            reply_markup=kb.admin_main_keyboard()
        )
    else:
        await message.answer("❌ Nädogry parol! Gaýtadan synanyşyň ýa-da /start basyň.")

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: CallbackQuery):
    stats = await db.get_stats()
    text = (
        "📊 **BOTYŇ CANLY STATISTIKASY**\n\n"
        f"👥 **Jemi Agzalar:** {stats['total_users']} sany\n"
        f"👨 **Oglanlar:** {stats['male_users']}\n"
        f"👩 **Gyzlar:** {stats['female_users']}\n"
        f"🟢 **Işjeň Ulanyjylar:** {stats['active_users']}\n"
        f"🚫 **Bloklanan (Banned):** {stats['banned_users']}\n\n"
        f"❤️ **Jemi Like-lar:** {stats['total_likes']}\n"
        f"🎉 **Özara Gabat Gelmeler (Matches):** {stats['total_matches']}\n"
    )
    await call.message.edit_text(text, reply_markup=kb.admin_main_keyboard())
    await call.answer()

@router.callback_query(F.data == "admin_recent")
async def cb_admin_recent(call: CallbackQuery):
    users = await db.get_recent_users(5)
    if not users:
        await call.answer("Häzirlikçe ulanyjy ýok!", show_alert=True)
        return
    
    text = "👥 **SOŇKY GOŞULAN 5 ANKETA (MODERASIÝA):**\n\n"
    for u in users:
        username = f"@{u['username']}" if u.get('username') else "Ýok"
        status = "🚫 Bloklanan" if u.get('is_banned') else ("⭐ VIP" if u.get('is_vip') else "✅ Işjeň")
        text += (
            f"👤 **{u['name']}**, {u['age']} ýaş, {u['city']}\n"
            f"🆔 ID: `{u['telegram_id']}` | {username}\n"
            f"Ýagdaýy: {status}\n"
            f"Bio: {u['bio']}\n"
            f"---------------------------\n"
        )
    await call.message.edit_text(text, reply_markup=kb.admin_main_keyboard())
    await call.answer()

@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "📢 **HEMMELERE HAT UGRATMAK (RASSYLKA)**\n\n"
        "Hemme ulanyjylara ugratmak isleýän hatyňyzy, reklamaňyzy ýa-da bildirişiňizi ýazyň:\n"
        "(Suratly ýa-da diňe tekst bolup biler)",
        reply_markup=kb.admin_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_broadcast)
    await call.answer()

@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    user_ids = await db.get_all_active_users()
    await message.answer(f"⏳ Hat {len(user_ids)} sany ulanyja ugradylýar...")

    success = 0
    blocked = 0

    for uid in user_ids:
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=uid,
                    photo=message.photo[-1].file_id,
                    caption=message.caption or ""
                )
            else:
                await bot.send_message(chat_id=uid, text=message.text)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            blocked += 1

    await state.clear()
    await message.answer(
        f"✅ **Rassylka Tamamlandy!**\n\n"
        f"📨 Gowşan sany: **{success}**\n"
        f"❌ Bloklan/Öçüren: **{blocked}**",
        reply_markup=kb.admin_main_keyboard()
    )

@router.callback_query(F.data == "admin_ban")
async def cb_admin_ban(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "🚫 **ULANYJYNY BLOKLAMAK (BAN)**\n\n"
        "Bloklamak isleýän ulanyjyňyzyň **Telegram ID**-sini ýazyň:",
        reply_markup=kb.admin_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_ban_id)
    await call.answer()

@router.message(AdminStates.waiting_for_ban_id)
async def process_ban_user(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        return await message.answer("Diňe san bilen ID ýazyň (mysal: 12345678):")
    uid = int(message.text)
    await db.ban_user(uid, True)
    await state.clear()
    await message.answer(f"🚫 Ulanyjy (ID: {uid}) üstünlikli bloklandy!", reply_markup=kb.admin_main_keyboard())

@router.callback_query(F.data == "admin_vip")
async def cb_admin_vip(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "⭐ **VIP STATUS BERMEK**\n\n"
        "VIP status bermek isleýän ulanyjyňyzyň **Telegram ID**-sini ýazyň:\n"
        "(VIP ulanyjylaryň anketasy beýlekilerden iň birinji bolup çykar)",
        reply_markup=kb.admin_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_vip_id)
    await call.answer()

@router.message(AdminStates.waiting_for_vip_id)
async def process_vip_user(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        return await message.answer("Diňe san bilen ID ýazyň:")
    uid = int(message.text)
    await db.set_user_vip(uid, True)
    await state.clear()
    await message.answer(f"⭐ Ulanyja (ID: {uid}) VIP status berildi!", reply_markup=kb.admin_main_keyboard())

@router.callback_query(F.data == "admin_cancel")
async def cb_admin_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Hereket ýatyryldy.", reply_markup=kb.admin_main_keyboard())
    await call.answer()

# ==================== DAIVINCHIK ESASY LOGIKASY ====================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if user and user.get('is_banned'):
        return await message.answer("🚫 Siziň anketaňyz düzgün bozandygyňyz sebäpli admin tarapyndan bloklandy.")

    if user:
        await message.answer(
            f"Salam ýene-de, {user['name']}! Anketalary görmek üçin düwmelerden birini saýlaň:",
            reply_markup=kb.feed_keyboard()
        )
        await state.set_state(FeedState.browsing)
        await show_next_profile(message, state, message.from_user.id)
    else:
        await message.answer(
            "Salam! 👋 Tanyşlyk botyna hoş geldiňiz!\n"
            "Özüňize täze dostlar we tanyşlar tapmak üçin gysgaça anketa dolduralyň.\n\n"
            "Ilki bilen, **ýaşyňyz näçe?** (San bilen ýazyň, meselem: 20):",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Registration.age)

@router.message(Registration.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        return await message.answer("Haýyş, ýaşyňyzy diňe san bilen ýazyň (meselem: 21):")
    age = int(message.text)
    if age < 14 or age > 90:
        return await message.answer("Ýaşyňyz 14 bilen 90 aralygynda bolmaly:")
    
    await state.update_data(age=age)
    await message.answer("Jynsyňyz nähili?", reply_markup=kb.gender_keyboard())
    await state.set_state(Registration.gender)

@router.message(Registration.gender)
async def process_gender(message: Message, state: FSMContext):
    text = message.text or ""
    gender = "male" if "Oglan" in text else "female"
    await state.update_data(gender=gender)
    await message.answer("Siz kimi gözleýärsiňiz?", reply_markup=kb.target_gender_keyboard())
    await state.set_state(Registration.target_gender)

@router.message(Registration.target_gender)
async def process_target_gender(message: Message, state: FSMContext):
    text = message.text or ""
    if "Gyzlar" in text:
        target = "female"
    elif "Oglanlar" in text:
        target = "male"
    else:
        target = "all"
    
    await state.update_data(target_gender=target)
    await message.answer("Haýsy şäherde ýaşaýarsyňyz?", reply_markup=kb.city_keyboard())
    await state.set_state(Registration.city)

@router.message(Registration.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text or "Aşgabat"
    await state.update_data(city=city)
    await message.answer(
        "Ajaýyp! Indi bolsa **adyňyz näme?**",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.name)

@router.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    name = (message.text or "Tanyş").strip()
    await state.update_data(name=name)
    await message.answer(
        "Indi bolsa anketanyz üçin **öz suratyňyzy ugradyň** 📸\n"
        "(Gowy düşen surat köp halanmaga kömek eder!)"
    )
    await state.set_state(Registration.photo)

@router.message(Registration.photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo_file_id=photo_file_id)
    await message.answer(
        "Ajaýyp surat! Indi özüňiz barada gysgaça maglumat (bio) ýazyň ✍️\n"
        "(Gyzyklanmalaryňyz, näme bilen meşgullanýarsyňyz?)"
    )
    await state.set_state(Registration.bio)

@router.message(Registration.bio)
async def process_bio(message: Message, state: FSMContext):
    bio = message.text or ""
    data = await state.get_data()
    username = message.from_user.username or ""

    await db.save_user(
        telegram_id=message.from_user.id,
        username=username,
        name=data['name'],
        age=data['age'],
        gender=data['gender'],
        target_gender=data['target_gender'],
        city=data['city'],
        bio=bio,
        photo_file_id=data['photo_file_id']
    )

    await message.answer("🎉 Anketanyz üstünlikli döredildi! Ine siziň anketanyz:")
    caption = f"👤 {data['name']}, {data['age']}, {data['city']}\n\n{bio}"
    await message.answer_photo(
        photo=data['photo_file_id'],
        caption=caption,
        reply_markup=kb.feed_keyboard()
    )

    await state.set_state(FeedState.browsing)
    await message.answer("Indi bolsa tanyşmaga başlalyň! Ine ilkinji anketa:")
    await show_next_profile(message, state, message.from_user.id)

async def show_next_profile(message: Message, state: FSMContext, user_id: int):
    user = await db.get_user(user_id)
    if not user:
        return
    candidate = await db.get_next_candidate(user)
    if not candidate:
        await message.answer(
            "Häzirlikçe siziň kriteriýalaryňyza gabat gelýän täze anketalar gutardy 😴\n"
            "Täze adamlar goşulanda hökman görüp bilersiňiz!",
            reply_markup=kb.sleep_keyboard()
        )
        return

    await state.update_data(current_candidate_id=candidate['telegram_id'])
    vip_badge = "⭐ [VIP] " if candidate.get('is_vip') else ""
    caption = f"{vip_badge}👤 {candidate['name']}, {candidate['age']}, {candidate['city']}\n\n{candidate['bio']}"
    await message.answer_photo(
        photo=candidate['photo_file_id'],
        caption=caption,
        reply_markup=kb.feed_keyboard()
    )

@router.message(FeedState.browsing, F.text.in_(["❤️", "👎", "💤", "💌"]))
async def handle_feed_action(message: Message, state: FSMContext, bot: Bot):
    action = message.text
    data = await state.get_data()
    candidate_id = data.get("current_candidate_id")

    if not candidate_id:
        return await show_next_profile(message, state, message.from_user.id)

    if action == "❤️":
        is_match = await db.add_like(message.from_user.id, candidate_id)
        if is_match:
            candidate = await db.get_user(candidate_id)
            current_user = await db.get_user(message.from_user.id)
            
            cand_handle = f"@{candidate['username']}" if candidate.get('username') else "Ulanyjy username goýmandyr"
            await message.answer(
                f"🎉 **Gabat gelme boldy (Özara Like!)**\n\n"
                f"{candidate['name']} hem sizi halady!\n"
                f"Onuň bilen göni söhbetdeşlige başlamak üçin: {cand_handle}"
            )
            
            try:
                curr_handle = f"@{current_user['username']}" if current_user.get('username') else "Ulanyjy username goýmandyr"
                await bot.send_message(
                    candidate_id,
                    f"🎉 **Gabat gelme boldy!**\n\n"
                    f"{current_user['name']} hem sizi halady!\n"
                    f"Onuň bilen göni söhbetdeşlige başlamak üçin: {curr_handle}"
                )
            except Exception:
                pass
        await show_next_profile(message, state, message.from_user.id)

    elif action == "👎":
        await show_next_profile(message, state, message.from_user.id)

    elif action == "💌":
        await message.answer("Bu ulanyja ugratmak isleýän hatyňyzy ýazyň (meselem: 'Salam, suratyňyz owadan eken'):")
        await state.set_state(FeedState.send_comment)

    elif action == "💤":
        await db.set_user_active(message.from_user.id, False)
        await message.answer(
            "Anketaňyz arakesmä goýuldy 😴 (beýlekiler sizi görmez).\nTäzeden başlamak üçin aşakdaky düwmä basyň:",
            reply_markup=kb.sleep_keyboard()
        )

@router.message(FeedState.send_comment)
async def handle_comment_sent(message: Message, state: FSMContext):
    comment_text = message.text or ""
    data = await state.get_data()
    candidate_id = data.get("current_candidate_id")

    if candidate_id:
        await db.add_like(message.from_user.id, candidate_id, comment=comment_text)
        await message.answer("Hatyňyz we halamaňyz ugradyldy! 💌", reply_markup=kb.feed_keyboard())
    
    await state.set_state(FeedState.browsing)
    await show_next_profile(message, state, message.from_user.id)

@router.message(F.text == "▶️ Täzeden gözleg")
async def resume_feed(message: Message, state: FSMContext):
    await db.set_user_active(message.from_user.id, True)
    await message.answer("Gözleg täzeden başlandy!", reply_markup=kb.feed_keyboard())
    await state.set_state(FeedState.browsing)
    await show_next_profile(message, state, message.from_user.id)
