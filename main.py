from aiogram import Bot, Dispatcher, F
import logging
import asyncio
from aiogram.filters import Command, StateFilter

from core.micro_services.product_feed import *
from core.micro_services.cart import *
from core.handlers import starting_work
from core.settings import settings

async def start():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.bots.bot_token)
    dp = Dispatcher()

    #Общие
    dp.message.register(starting_work, Command("start"))
    dp.message.register(starting_work, F.text=='🔄 Перезапуск')

    #Лента товаров
    dp.message.register(show_feed, F.text=='📜 Просмотреть ленту товаров')
    dp.message.register(show_feed, F.text=='🔽 Показать еще',
                        StateFilter(ProductFeed.product_feed))
    dp.message.register(close_feed, F.text=='🚪 Выйти',
                        StateFilter(ProductFeed.product_feed))
    dp.callback_query.register(write_to_cart, lambda c: c.data.startswith("add_to_cart:"),
                        StateFilter(ProductFeed.product_feed))
    dp.message.register(back_to_feed, F.text=='❌ Отмена',
                        StateFilter(ProductFeed.choose_quantity))
    dp.message.register(add_to_cart, ProductFeed.choose_quantity)

    #Корзина    
    dp.message.register(show_cart, F.text=='🛒 Просмотреть корзину')
    dp.callback_query.register(edit_cart_item_quantity, lambda c: c.data.startswith("edit_cart:"),
                        StateFilter(Cart.cart))
    dp.callback_query.register(delete_cart_item, lambda c: c.data.startswith("del_cart:"),
                        StateFilter(Cart.cart)) 
    

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())