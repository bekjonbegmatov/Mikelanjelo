from aiogram import Dispatcher , Bot
import asyncio
import config

from bot.heandlers.main import router

async def main():
    bot = Bot(token=config.TELEGRAM_API_KEY)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())