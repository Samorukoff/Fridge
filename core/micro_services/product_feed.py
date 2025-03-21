import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from ..google_sheets import feed_sheet
from ..keyboards.inline import add_to_cart_button

class ProductFeed(StatesGroup):
    product_feed = State()
    choose_quantity = State()

async def show_feed (message: Message, state: FSMContext):
    await state.set_state(ProductFeed.product_feed)
    feed_data = feed_sheet.get_all_records()
    for row in feed_data:
            product_id = row["product_id"]
            name = row["name"]
            description = row["description"]
            photo_id = row["photo_id"]
            date_placement = row["date_placement"]
            delivery_time = row["delivery_time"]
            product_unit = row["product_unit"]
            availability = row["availability"]
            price = row["price"]

            caption = (
                f"<b>Наименование:</b> {name}\n"
                f"<b>Описание:</b> {description}\n"
                f"<b>Дата размещения:</b> {date_placement}\n"
                f"<b>Срок поставки:</b> {delivery_time}\n"
                f"<b>Единица товара:</b> {product_unit}\n"
                f"<b>Наличие:</b> {availability}\n"
                f"<b>Цена:</b> {price}"
            )

            await message.answer_photo(photo=photo_id, caption=caption,
                                    reply_markup=add_to_cart_button(product_id),
                                    parse_mode="HTML")

async def write_to_cart(callback: CallbackQuery, state: FSMContext):
    await state.update_data(product_id = callback.data.split(":")[1])
    await state.set_state(ProductFeed.choose_quantity)
    await callback.message.answer('✍️ Введите количество единиц товара.')
