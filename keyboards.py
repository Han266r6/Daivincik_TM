"""
Telegram duwmeleri (ReplyKeyboardMarkup we InlineKeyboardMarkup)
Daivinchik stilindaki 1, 2, 3, 4 duwmeler
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🙋‍♂️ Men Oglan"), KeyboardButton(text="🙋‍♀️ Men Gyz")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def target_gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌸 Gyzlar"), KeyboardButton(text="💪 Oglanlar")],
            [KeyboardButton(text="👥 Hemmesi bilesigeliji")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def city_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Aşgabat"), KeyboardButton(text="Mary")],
            [KeyboardButton(text="Türkmenabat"), KeyboardButton(text="Daşoguz")],
            [KeyboardButton(text="Balkanabat"), KeyboardButton(text="Türkmenbaşy")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def feed_keyboard():
    """
    Daivinchik klassik duwmeleri:
    1 = ❤️ (Like)
    2 = 💌 (Hat ugratmak)
    3 = 👎 (Dislike / Indiki)
    4 = 💤 (Yatmak / Arakesme)
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❤️"), KeyboardButton(text="💌"), KeyboardButton(text="👎"), KeyboardButton(text="💤")]
        ],
        resize_keyboard=True
    )

def sleep_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="▶️ Täzeden gözleg")]
        ],
        resize_keyboard=True
    )
