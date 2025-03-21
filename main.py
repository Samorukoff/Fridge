from aiogram import Bot, Dispatcher, F
import logging
import asyncio
from aiogram.filters import Command, StateFilter

from core.micro_services.product_feed import *
from core.handlers import starting_work
from core.settings import settings

async def start():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.bots.bot_token)
    dp = Dispatcher()
    dp.message.register(starting_work, Command("start"))
    dp.message.register(show_feed, F.text=='Просмотреть ленту товаров')
    dp.callback_query.register(write_to_cart,lambda c: c.data.startswith("add_to_cart:"),
                               StateFilter(ProductFeed.product_feed))

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())