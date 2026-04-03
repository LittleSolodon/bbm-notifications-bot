from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Уведомления")],
                  [KeyboardButton(text="Управление аккаунтом")]],
        resize_keyboard=True,
    )

def turn_on() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Включить уведомления")],
         [KeyboardButton(text="🌟 Избранное")],
         [KeyboardButton(text="Фильтры")],
         [KeyboardButton(text="⬅️ Назад")]],
         resize_keyboard=True
    )

def turn_off() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Выключить уведомления")],
         [KeyboardButton(text="🌟 Избранное")],
         [KeyboardButton(text="Фильтры")],
         [KeyboardButton(text="⬅️ Назад")]],
         resize_keyboard=True
    )

def back() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
     keyboard=[[KeyboardButton(text="⬅️ Назад")]],
     resize_keyboard=True
    )

def fav_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Добавить предметы в избранное")],
                  [KeyboardButton(text="Удалить из избранного")],
                  [KeyboardButton(text="⬅️ Назад")]],
                  resize_keyboard=True
    )