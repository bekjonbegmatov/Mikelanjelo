# Системные Импорт
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import ReplyKeyboardRemove

#  Кастомные импорты

from data.manage import UserDatabase
from bot.keyboards.inline.button import anketa_button
from bot.keyboards.keyboard_tg.button import gender_button, user_name_button, main_menu_button
from bot.utils.user import User_Registration as UState

# Import Other routers
from bot.heandlers.anketa import router as anketa_router

router = Router()

@router.message(Command('start'))
async def start_message(message:Message, state:FSMContext):
    with UserDatabase() as db:
        user = db.get_user_by_telegram_id(telegram_id=message.from_user.id)
        if user :
            text = f'''Привет {user[3]}  
            '''
            # await message.answer(
            #     text='Привет чтобы начать пользоваться ботом нужно заполнить небольшую анкету\n<b>Давай сначала определимся с полом </b>',
            #     parse_mode=ParseMode.HTML,
            #     reply_markup=gender_button()
            #     )
            await message.answer(text=text, reply_markup=main_menu_button())

        else:   
            db.add_user(
                telegram_id = message.from_user.id, 
                username    = message.from_user.username,
                first_name  = message.from_user.first_name,
                last_name   = message.from_user.last_name, 
                )
            await message.answer_sticker('CAACAgIAAxkBAAEKPlZk-eLKS3tUCG_aRGY1wZjJY8tnxAACxgEAAhZCawpKI9T0ydt5RzAE')
            await message.answer('''Уже <b>тисячы</b> людей знакомиться в Микеланджело 😍
                                 
Я могу найти тебя пару или друзей 👫
                                 ''',
                                 parse_mode=ParseMode.HTML
                                )
            await message.answer(
                text='Сначала определимся полом',
                parse_mode=ParseMode.HTML,
                reply_markup=gender_button()
                )
            await state.set_state(UState.gender)
# Get IMG
@router.message(UState.gender)
async def handle_photo(message: Message, state:FSMContext):
    name = message.from_user.first_name
    if message.text == "Я девушка":
        await state.update_data(gender=message.text)
        await state.set_state(UState.first_name)
        await message.answer('Как я тебе могу обращаться ?', reply_markup=user_name_button(name))
    elif message.text == "Я парень":
        await state.update_data(gender=message.text)
        await state.set_state(UState.first_name)
        await message.answer('Как я тебе могу обращаться ?', reply_markup=user_name_button(name))
    else:
        await message.answer('Пожалуйста выбери один из вариантов из списка')

# CallBack 

@router.callback_query(F.data == 'get_ankete')
async def create_ankete(call:CallbackQuery, state:FSMContext):
    await state.set_state(UState.gender)
    await call.message.answer('Выберите ваш пол :', reply_markup=gender_button())
    # continus in anketa.py
    

@router.message(Command('clear'))
async def clear_db(message:Message):
    with UserDatabase() as db:
        db.drop_table()
        await message.answer('TABLE DROPED !!!')
    
# TEST COMMANDS 

router.include_router(anketa_router)