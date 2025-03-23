import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from ..google_sheets import feed_sheet, cart_sheet
from ..keyboards.inline import *
from ..keyboards.reply import *

class Cart(StatesGroup):
    cart = State()

#Вывод всех карточек товаров, находящихся в корзине
async def show_cart(message: Message, state: FSMContext):

    #Удаление ленты товаров
    data = await state.get_data()
    product_cards = data.get('product_cards',[])[::-1]
    for card in product_cards:
        await card.delete()
    await state.clear()

    await state.set_state(Cart.cart)

    user_id = message.from_user.id

    feed_data = feed_sheet.get_all_records()
    cart_data = cart_sheet.get_all_records()[::-1]

    #Создание корзины, вывод карточек твоаров по порядку
    order_cards = []
    for cart_row in cart_data:
        if str(cart_row.get("customer_id")) == str(user_id):
            product_id = cart_row.get("product_id")
            quantity = cart_row.get("quantity")
            total_price = float(cart_row.get("total_price"))
            for feed_row in feed_data:
                if str(feed_row.get("product_id")) == str(product_id):
                    name = feed_row.get("name")
                    description = feed_row.get("description")
                    photo_id = feed_row.get("photo_id")
                    delivery_time = feed_row.get("delivery_time")
                    product_unit = feed_row.get("product_unit")
                    price = feed_row.get("price")
        
                    caption = (
                        f"<b>Наименование:</b> {name}\n"
                        f"<b>Описание:</b> {description}\n"
                        f"<b>Срок поставки:</b> {delivery_time}\n"
                        f"<b>Объем заказа:</b> {quantity} {product_unit}\n"
                        f"<b>Итоговая цена:</b> {total_price}"
                    )

                    order_card = await message.answer_photo(photo=photo_id, caption=caption,
                                            reply_markup=edit_cart_kb(product_id, quantity, price),
                                            parse_mode="HTML")
                    
                    order_cards.append(order_card)
                    break
    await state.update_data(order_cards=order_cards)
    await message.answer('🛒 Добро пожаловать в вашу корзину!', reply_markup=cart_kb)

#Выход из корзины
async def close_feed(message: Message, state: FSMContext):
    data = await state.get_data()
    order_cards = data.get('order_cards', [])[::-1]
    await message.answer('Выберите пункт меню', reply_markup=start_kb)
    for card in order_cards:
        await card.delete()
    await state.clear()

async def edit_cart_item_quantity(callback: CallbackQuery, state: FSMContext):
    await callback.answer

    work_piece = callback.data.split(":")[1]
    product_id, quantity, price = work_piece.split(",")
    user_id = callback.from_user.id

async def delete_cart_item():
