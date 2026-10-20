"""
Telegram duwmeleri: Leonardo Daivinchik + Modern Admin Paneli
"""

from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

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

# ==================== MODERN ADMIN PANEL DÜWMELERI ====================

def admin_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Canly Statistika", callback_data="admin_stats"),
                InlineKeyboardButton(text="📢 Hemmelere Hat (Rassylka)", callback_data="admin_broadcast"),
            ],
            [
                InlineKeyboardButton(text="👥 Soňky Anketalar (Moderasiýa)", callback_data="admin_recent"),
                InlineKeyboardButton(text="🚫 Ulanyjyny Banlamak", callback_data="admin_ban"),
            ],
            [
                InlineKeyboardButton(text="⭐ VIP Status Bermek", callback_data="admin_vip"),
                InlineKeyboardButton(text="🔄 Täzelemek", callback_data="admin_refresh"),
            ]
        ]
    )

def admin_cancel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Ýatyrmak", callback_data="admin_cancel")]
        ]
    )
