import aioredis
import random

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext

from data.manage import UserDatabase, LikesDatabase, RecommendationSystem
from bot.keyboards.keyboard_tg.button import main_menu_button
from bot.keyboards.inline.button import get_message_button
from bot.utils.user import User_Like_Message  # State

router = Router()

# Асинхронная инициализация Redis-пула
async def get_redis_pool():
    return await aioredis.create_redis_pool("redis://localhost:6379")

redis = None

# Отправка любовного письма
@router.message(F.text, User_Like_Message.user_id_to)
async def send_love_message(message: Message, state: FSMContext, bot: Bot):
    global redis #! I don't shure about it 
    if redis is None:
        redis = await get_redis_pool()
        
    letter_user_id = await redis.get(f'loveleter_{message.from_user.id}')
    if message.text:
        if letter_user_id:
            await bot.send_message(
                chat_id=int(letter_user_id),
                text='Пользователь отправил вам сообщение',
                reply_markup=get_message_button(sender_id=message.from_user.id, message=message.text)
            )
            await message.answer(
                text="Ваше сообщение успешно отправлен"
            )
            await state.clear()
            
            with UserDatabase() as db, LikesDatabase() as likes_db:
                recommender = RecommendationSystem(db, likes_db)
                recommendations = recommender.get_recommendations(message.from_user.id)
                if recommendations:
                    user = recommendations[0]
                    await bot.send_photo(
                        chat_id=message.from_user.id,
                        photo=user[6],
                        caption=f'''<b>{user[3]}</b>, {user[10]} - {user[7]}''',
                        parse_mode=ParseMode.HTML,
                        reply_markup=main_menu_button()
                    )
                await redis.set(message.from_user.id, user[1])

@router.message(F.text)
async def get_user_for_like(message: Message, bot: Bot, state: FSMContext):
    global redis
    if redis is None:
        redis = await get_redis_pool()

    love_user_id = await redis.get(message.from_user.id)
    if message.text in ['♥️', '👎']:
        if love_user_id:
            with LikesDatabase() as like_db:
                # Добавление записей
                like_db.add_like(message.from_user.id, love_user_id)
                # Отправка сообщения
                await bot.send_message(
                    chat_id=int(love_user_id),
                    text="Вы понравились одному человеку 🥰",
                )
                
                with UserDatabase() as db, LikesDatabase() as likes_db:
                    recommender = RecommendationSystem(db, likes_db)
                    recommendations = recommender.get_recommendations(user_id=message.from_user.id, limit=1)
                    if recommendations:
                        user = random.choice(recommendations)
                        await bot.send_photo(
                            chat_id=message.from_user.id,
                            photo=user[6],
                            caption=f'''<b>{user[3]}</b>, {user[10]} - {user[7]}''',
                            parse_mode=ParseMode.HTML,
                            reply_markup=main_menu_button()
                        )
                        await redis.set(message.from_user.id, user[1])  # Обновление кеша
    elif message.text == '💌':
        if love_user_id:
            with LikesDatabase() as like_db:
                await message.answer('Напишите ваше сообщение')
                like_db.add_like(message.from_user.id, love_user_id)
                
                await redis.set(key=f"loveleter_{message.from_user.id}",
                                value=love_user_id)
                
                #? Bilmiman logikani almashtirayabman 
                await state.set_state(User_Like_Message.user_id_to)

    elif message.text == 'Начать поиск !':
        with UserDatabase() as db, LikesDatabase() as likes_db:
            recommender = RecommendationSystem(db, likes_db)
            recommendations = recommender.get_recommendations(message.from_user.id)
            if recommendations:
                user = recommendations[0]
                await bot.send_photo(
                    chat_id=message.from_user.id,
                    photo=user[6],
                    caption=f'''<b>{user[3]}</b>, {user[10]} - {user[7]}''',
                    parse_mode=ParseMode.HTML,
                    reply_markup=main_menu_button()
                )
                await redis.set(message.from_user.id, user[1])

#* This is callback quvery for get_message !
@router.callback_query(F.data.startswith('letter_'))
async def get_love_letter(call: CallbackQuery, bot: Bot):
    global redis
    if redis is None:
        redis = await get_redis_pool()

    data = call.data.split('_')
    sender_id = int(data[1])
    message = data[2]
    
    with UserDatabase() as user_db:
        user = user_db.get_user_by_telegram_id(int(sender_id))
        if user:
            await bot.send_photo(
                chat_id=call.message.chat.id,
                photo=user[6],
                caption=f'''<b>{user[3]}</b>, {user[10]} - {user[7]}

<b>Сообщение</b>
{message}
''',
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu_button()
            )
            await redis.set(call.message.chat.id, sender_id)

if __name__ == '__main__':
    import asyncio
    from aiogram import executor

    async def on_startup(_):
        global redis
        redis = await get_redis_pool()

    executor.start_polling(router, skip_updates=True, on_startup=on_startup)
