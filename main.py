from aiogram import Bot, Dispatcher, F
import logging
import asyncio
from aiogram.filters import Command, StateFilter

from core.handlers.micro_services.product_feed import *
from core.handlers.micro_services.cart import *

from core.handlers.user_levels.admin_user import *
from core.handlers.user_levels.seller_user import *
from core.handlers.user_levels.customer_user import *

from core.handlers.general_handlers import starting_work

from core.settings import settings

async def start():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.bots.bot_token)
    dp = Dispatcher()

    #Общие
    dp.message.register(starting_work, Command("start"))
    dp.message.register(starting_work, F.text=='🔄 Перезапуск')

    #Покупатель
    dp.message.register(show_feed, F.text=='📜 Просмотреть ленту товаров',
                        StateFilter(Customer.customer_start))
    dp.message.register(show_cart, F.text=='🛒 Просмотреть корзину',
                        StateFilter(Customer.customer_start))
    dp.message.register(instruction, F.text=='📘 Инструкция',
                        StateFilter(Customer.customer_start))
    #Продавец
    dp.message.register(instruction, F.text=='📘 Инструкция',
                        StateFilter(Seller.seller_start))
    dp.message.register(show_feed, F.text=='📜 Просмотреть ленту товаров',
                        StateFilter(Seller.seller_start))
    dp.callback_query.register(write_prod_name, F.text=='📦 Разместить товар',
                        StateFilter(Seller.seller_start))
    dp.callback_query.register(Seller.prod_name_st)
    dp.callback_query.register(Seller.prod_desc_st)
    dp.callback_query.register(Seller.prod_photo_st)
    dp.callback_query.register(Seller.prod_name_st, F.data.startswith('unit:'))
    
    #Админ
    dp.message.register(instruction, F.text=='📘 Инструкция',
                        StateFilter(Admin.admin_start))
    dp.message.register(invite_link, F.text=='🔑 Создать ссылку-приглашение',
                        StateFilter(Admin.admin_start))
    dp.message.register(show_feed, F.text=='📜 Просмотреть ленту товаров',
                        StateFilter(Admin.admin_start))

    #Лента товаров
    dp.message.register(show_feed, F.text=='🔽 Показать еще',
                        StateFilter(ProductFeed.product_feed))
    dp.message.register(close_feed, F.text=='🚪 Выйти',
                        StateFilter(ProductFeed.product_feed))
    dp.callback_query.register(write_to_cart, F.data.startswith("add_to_cart:"),
                        StateFilter(ProductFeed.product_feed))
    dp.callback_query.register(delete_feed_item, F.data.startswith("del_from_feed:"),
                        StateFilter(ProductFeed.product_feed))
    dp.message.register(back_to_feed, F.text=='❌ Отмена',
                        StateFilter(ProductFeed.choose_quantity))
    dp.message.register(add_to_cart, ProductFeed.choose_quantity)

    #Корзина    
    dp.callback_query.register(edit_cart_item_quantity, F.data.startswith("edit_cart:"),
                        StateFilter(Cart.cart))
    dp.message.register(back_to_cart, F.text=='❌ Отмена',
                        StateFilter(Cart.choose_quantity))
    dp.message.register(write_new_quantity, Cart.choose_quantity)
    dp.callback_query.register(delete_cart_item, F.data.startswith("del_cart:"),
                        StateFilter(Cart.cart))
    dp.message.register(purchase, F.text == '✅ Оформить заказ',
                               StateFilter(Cart.cart))
    dp.message.register(close_cart, F.text == '🚪 Выйти',
                               StateFilter(Cart.cart)) 
    

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())