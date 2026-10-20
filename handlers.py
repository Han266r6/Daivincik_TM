"""
Botyn hemme esasy logikasy we FSM (Anketa doldurmak, Lenka gormek, Match bildirisler)
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb

router = Router()

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

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if user:
        await message.answer(
            f"Salam yene-de, {user['name']}! Anketalary gormek ucin duwmelerden birini saylan:",
            reply_markup=kb.feed_keyboard()
        )
        await state.set_state(FeedState.browsing)
        await show_next_profile(message, state, message.from_user.id)
    else:
        await message.answer(
            "Salam! 👋 Tanyşlyk botyna hoş geldiňiz!\n"
            "Özüňize täze dostlar we tanyşlar tapmak üçin gysgaça anketa dolduralyň.\n\n"
            "Ilki bilen, **ýaşyňyz näçe?** (San bilen ýazyň, meselem: 20)",
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
        "Gaty gowy! Indi bolsa **adyňyz näme?**",
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
        "(Gyzyklanmalaryňyz, näme bilen meşgullanýarsyňyz we kimi gözleýärsiňiz?)"
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
    caption = f"{data['name']}, {data['age']}, {data['city']}\n\n{bio}"
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
    caption = f"{candidate['name']}, {candidate['age']}, {candidate['city']}\n\n{candidate['bio']}"
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
            
            # 1. Halamagy basan ulanyja hat ugratmak
            cand_handle = f"@{candidate['username']}" if candidate.get('username') else "Ulanyjy username goymandyr"
            await message.answer(f"🎉 **Gabat gelme (Match)!**\n{candidate['name']} hem sizi halady!\nOnuň Telegramy: {cand_handle}")
            
            # 2. Beýleki tarapa hem habar ugratmak
            try:
                curr_handle = f"@{current_user['username']}" if current_user.get('username') else "Ulanyjy username goymandyr"
                await bot.send_message(
                    candidate_id,
                    f"🎉 **Gabat gelme boldy!**\n{current_user['name']} hem sizi halady!\nOnuň Telegramy: {curr_handle}"
                )
            except Exception:
                pass
        await show_next_profile(message, state, message.from_user.id)

    elif action == "👎":
        # Dislike: Diňe indiki anketany görkezýäris
        await show_next_profile(message, state, message.from_user.id)

    elif action == "💌":
        await message.answer("Bu ulanyja ugratmak isleýän hatyňyzy ýazyň (meselem: 'Salam, gowy düşüpsiňiz'):")
        await state.set_state(FeedState.send_comment)

    elif action == "💤":
        await db.set_user_active(message.from_user.id, False)
        await message.answer(
            "Anketaňyz arakesmä goýuldy (beýlekiler sizi görmez). Täzeden başlamak üçin aşakdaky düwmä basyň:",
            reply_markup=kb.sleep_keyboard()
        )

@router.message(FeedState.send_comment)
async def handle_comment_sent(message: Message, state: FSMContext):
    comment_text = message.text or ""
    data = await state.get_data()
    candidate_id = data.get("current_candidate_id")

    if candidate_id:
        await db.add_like(message.from_user.id, candidate_id, comment=comment_text)
        await message.answer("Hatyňyz we halamaňyz ugradyldy! 👍", reply_markup=kb.feed_keyboard())
    
    await state.set_state(FeedState.browsing)
    await show_next_profile(message, state, message.from_user.id)

@router.message(F.text == "▶️ Täzeden gözleg")
async def resume_feed(message: Message, state: FSMContext):
    await db.set_user_active(message.from_user.id, True)
    await message.answer("Gözleg täzeden başlandy!", reply_markup=kb.feed_keyboard())
    await state.set_state(FeedState.browsing)
    await show_next_profile(message, state, message.from_user.id)
