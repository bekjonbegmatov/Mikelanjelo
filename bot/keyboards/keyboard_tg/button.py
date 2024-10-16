from aiogram.utils.keyboard import KeyboardBuilder
from aiogram.types import KeyboardButton , ReplyKeyboardMarkup

def user_name_button(name):
    kb = [
        [
            KeyboardButton(text=name)
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите ваш пол"
    )
    return keyboard

def gender_button():
    kb = [
        [
            KeyboardButton(text="Я девушка"),
            KeyboardButton(text="Я парень")
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите ваш пол"
    )
    return keyboard

def who_interested_button():
    kb = [
        [
            KeyboardButton(text='Девушки'),
            KeyboardButton(text='Парни'),
            KeyboardButton(text='Без разницы')
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите кто вам интересно"
    )
    return keyboard

def get_location_button():
    kb = [
        [
            KeyboardButton(
                text='Отправить геолокацию 📍',
                request_location=True
                )
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите ваш пол"
    )
    return keyboard

def continum_button():
    kb = [
        [
            KeyboardButton(
                text='Пропустить'
                )
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите ваш пол"
    )
    return keyboard

# def pognali_button()

def main_menu_button():
    kb = [
        [
            KeyboardButton(text="♥️"),
            KeyboardButton(text="💌"),
            KeyboardButton(text="👎"),
            KeyboardButton(text="💤")
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите ваш пол"
    )
    return keyboard

def go_button():
    kb = [
        [
            KeyboardButton(
                text='Начать поиск !'
                )
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Start !"
    )
    return keyboard