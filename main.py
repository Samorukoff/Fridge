from aiogram import Bot, Dispatcher, F
import logging
import asyncio
from aiogram.filters import Command, StateFilter
from aiogram_calendar.simple_calendar import SimpleCalendarCallback

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
    dp.message.register(starting_work, F.text=='◀️ Назад',
                        StateFilter(Seller.prod_name_st))
    dp.message.register(starting_work, F.text=='◀️ Назад',
                        StateFilter(Admin.admin_mailing))

    #Продавец
    dp.message.register(instruction, F.text=='📘 Инструкция',
                        StateFilter(Seller.seller_start))
    dp.message.register(show_feed, F.text=='📜 Просмотреть ленту моих товаров',
                        StateFilter(Seller.seller_start))
    
    dp.message.register(check_requests, F.text=='📝 Заявки',
                        StateFilter(Seller.seller_start))
    dp.message.register(leave_requests, F.text=='🚪 Выйти',
                        StateFilter(Seller.check_requests_st))
    dp.callback_query.register(apply_requests,
                        Seller.check_requests_st, F.data.startswith('request:'))
    #Продавец, процесс создания карточки товара
    dp.message.register(write_prod_name, F.text=='📦 Разместить товар',
                        StateFilter(Seller.seller_start))
    dp.message.register(write_prod_name, F.text=='◀️ Назад',
                        StateFilter(Seller.prod_desc_st))
    dp.message.register(write_prod_name, F.text=='❌ Переделать полностью',
                        StateFilter(Seller.prod_card_complete_st))

    dp.message.register(write_prod_desc, F.text,
                        StateFilter(Seller.prod_name_st))
    dp.message.register(write_prod_desc, F.text=='◀️ Назад',
                        StateFilter(Seller.prod_photo_st))

    dp.message.register(download_prod_photo, F.text,
                        StateFilter(Seller.prod_desc_st))
    dp.message.register(download_prod_photo, F.text=='◀️ Назад',
                        StateFilter(Seller.prod_unit_st))

    dp.message.register(choose_prod_unit, F.photo,
                        StateFilter(Seller.prod_photo_st))
    dp.message.register(choose_prod_unit, F.text=='◀️ Назад',
                        StateFilter(Seller.prod_availability_st))

    dp.callback_query.register(write_prod_availability,
                        Seller.prod_unit_st, F.data.startswith('unit:'))
    dp.message.register(write_prod_availability, F.text=='◀️ Назад',
                        StateFilter(Seller.prod_price_st))
    
    dp.message.register(write_prod_price, F.text,
                        StateFilter(Seller.prod_availability_st))
    dp.message.register(write_prod_price, F.text=='◀️ Назад',
                        StateFilter(Seller.prod_card_complete_st))
    
    dp.message.register(product_card_complete, F.text,
                        StateFilter(Seller.prod_price_st))

    dp.message.register(product_card_write, F.text=='✅ Завершить создание',
                        StateFilter(Seller.prod_card_complete_st))
    
    #Админ
    dp.message.register(instruction, F.text=='📘 Инструкция',
                        StateFilter(Admin.admin_start))
    dp.message.register(invite_link, F.text=='🔑 Создать ссылку-приглашение',
                        StateFilter(Admin.admin_start))
    dp.message.register(show_feed, F.text=='📜 Просмотреть ленту товаров',
                        StateFilter(Admin.admin_start))
    dp.message.register(give_google_sheets_link, F.text=='🔗 Ссылка на GoogleSheets',
                        StateFilter(Admin.admin_start))
    
    dp.message.register(mailing, F.text=='📤 Рассылка',
                        StateFilter(Admin.admin_start))
    dp.message.register(mailing, F.text=='◀️ Назад',
                        StateFilter(Admin.admin_mailing_choose))
    dp.message.register(choose_adressees, F.text, StateFilter(Admin.admin_mailing))
    dp.callback_query.register(send_adressees, Admin.admin_mailing_choose,
                               F.data.startswith("adr:"))
    
     #Покупатель
    dp.message.register(show_feed, F.text=='📜 Просмотреть ленту товаров',
                        StateFilter(Customer.customer_start))
    dp.message.register(show_cart, F.text=='🛒 Просмотреть корзину',
                        StateFilter(Customer.customer_start))
    dp.message.register(instruction, F.text=='📘 Инструкция',
                        StateFilter(Customer.customer_start))

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
    dp.message.register(check_and_choose_date, ProductFeed.choose_quantity)
    dp.callback_query.register(add_to_cart, SimpleCalendarCallback.filter(),
                               StateFilter(ProductFeed.choosing_date))

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