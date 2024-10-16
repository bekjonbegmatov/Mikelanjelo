# Aiogram imports
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.enums import ParseMode 

# Out Moduls Import 
import requests 
import random

# Custom Moduls Import
from data.manage import UserDatabase, LikesDatabase, RecommendationSystem
from bot.utils.user import User_Registration
from bot.keyboards.keyboard_tg.button import ( 
                                              who_interested_button,
                                              get_location_button,
                                              continum_button,
                                              main_menu_button,
                                              go_button
                                              )

#* Import Router From likes
from bot.heandlers.likes_alg import router as Like_Router

# ! Config geo and bot api key
from config import GEO_API_KEY

router = Router()

@router.message(User_Registration.first_name)
async def get_user_name(message:Message, state:FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(User_Registration.age)
    await message.answer(
        f'Хорошо {message.text}.\nСколько тебе лет ?\n<code>Например 18</code>',
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML
    )
    
@router.message(User_Registration.age)
async def get_user_age(message:Message, state:FSMContext):
    try :
        age = int(message.text)
        await state.update_data(age=message.text)
        await state.set_state(User_Registration.who_interested)
        await message.answer('Кто тебе интересен ?', reply_markup=who_interested_button())
    except:
        await message.answer('Напишите сколько вам лет цифрами !!!')
    
@router.message(User_Registration.who_interested)
async def get_user_interest(message:Message, state:FSMContext):
    if message.text == "Девушки":
        await state.update_data(who_interested=message.text)
        await state.set_state(User_Registration.description)
        await message.answer(
            text="Расскажи о себе и кого хочешь найти, чем предлагаешь заняться. Это поможет лучше подобрать тебе компанию.",
            reply_markup=continum_button())
    elif message.text == "Парни":
        await state.update_data(who_interested=message.text)
        await state.set_state(User_Registration.description)
        await message.answer(
            text="Расскажи о себе и кого хочешь найти, чем предлагаешь заняться. Это поможет лучше подобрать тебе компанию.",
            reply_markup=continum_button())
    elif message.text == "Без разницы":
        await state.update_data(who_interested=message.text)
        await state.set_state(User_Registration.description)
        await message.answer(
            text="Расскажи о себе и кого хочешь найти, чем предлагаешь заняться. Это поможет лучше подобрать тебе компанию.",
            reply_markup=continum_button())
    else:
        await message.reply("Пожалуйста выберите из вариантов")
        
@router.message(User_Registration.description)
async def get_user_description(message:Message, state:FSMContext):
    if message.text == "Пропустить":
        await state.update_data(description='')
    else:
        await state.update_data(description=message.text)
    await message.answer('Пожалуйста отправьте свою геолокацию чтобы мы определили в каком городе вы находитесь', reply_markup=get_location_button())
    await state.set_state(User_Registration.city)
    
@router.message(F.location, User_Registration.city)
async def get_user_location(message:Message, state:FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    try:
        response = requests.get(
            f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={GEO_API_KEY}"
        )
        
        if response.status_code == 200:
            data = response.json()
            city = data['features'][0]['properties'].get('city')  #  Измените это, если структура ответа другая
            
            if city:
                await message.answer('И последняя пожалуйста отправьте свою фотографию ✨', reply_markup=ReplyKeyboardRemove())
                await state.update_data(city=city)
                await state.set_state(User_Registration.photo)
            else:
                await message.answer("Не удалось определить город, попробуйте снова.")
        else:
            await message.answer(f"Ошибка при получении данных: {response.status_code}") # ! ERROR !
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")

@router.message(F.photo)
async def get_user_photo(message:Message, state:FSMContext, bot:Bot):
    data = await state.get_data()
    file_id = message.photo[-1].file_id
    caption = f'''<b>{data['first_name']}, {data['age']}, {data['city']} - {data['description']} </b>
    '''
    await message.answer_photo(photo=file_id, caption=caption, parse_mode=ParseMode.HTML)
    
    with UserDatabase() as db:
        db.update_user(
            telegram_id  = message.from_user.id,
            first_name   = data['first_name'],
            photo_id     = file_id,
            description  = data['description'],
            city         = data['city'],
            age          = data['age'],
            gender       = data['gender'],
            who_interest = data['who_interested']
            )
    
    await message.answer('✨🔍', reply_markup=go_button())
    await state.clear()
        

@router.message(Command('users'))
async def get_users(message:Message):
    with UserDatabase() as db:
        users = db.get_all_users()
        bot = message.bot
        for user in users:
            await bot.send_photo(
                chat_id = 5163141099,
                photo   = user[6], 
                caption = f'''@{user[2]}, <b>{user[3]}</b>, {user[10]} - {user[7]}''',
                parse_mode=ParseMode.HTML
                )

#! Include the router 
router.include_router(Like_Router)
