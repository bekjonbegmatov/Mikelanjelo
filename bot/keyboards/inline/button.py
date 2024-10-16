from aiogram.utils.keyboard import InlineKeyboardBuilder

def anketa_button():
    bulder = InlineKeyboardBuilder()
    bulder.button(text='Создать профиль 🌟' , callback_data="get_ankete")
    return bulder.as_markup()

def get_message_button(sender_id:int, message:str):
    bulder = InlineKeyboardBuilder()
    bulder.button(text='Посмотреть 💌' , callback_data=f"letter_{sender_id}_{message}")
    return bulder.as_markup()