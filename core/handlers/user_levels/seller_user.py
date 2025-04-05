import asyncio
import datetime

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from ...google_sheets import feed_sheet, cart_sheet
from ...keyboards.inline import *
from ...keyboards.reply import *

class Seller(StatesGroup):
    seller_start = State()
    prod_name_st = State()
    prod_desc_st = State()
    prod_photo_st = State()
    prod_unit_st = State()
    prod_availability_st = State()
    prod_price_st = State()
    prod_card_complete_st = State()

async def instruction(message: Message, state: FSMContext):
    await message.answer('Инструкция')

async def write_prod_name (message: Message, state: FSMContext):
    await state.set_state(Seller.prod_name_st)
    await message.answer ('Введите наименование товара', reply_markup=seller_create_card_kb)

async def write_prod_desc(message: Message, state: FSMContext):
    if message.text == '◀️ Назад':
        await state.set_state(Seller.prod_desc_st)
        await message.answer('Введите описание товара')
        return

    prod_card_name = message.text
    await state.update_data(prod_card_name=prod_card_name)
    await state.set_state(Seller.prod_desc_st)
    await message.answer('Введите описание товара')

async def download_prod_photo(message: Message, state: FSMContext):
    if message.text == '◀️ Назад':
        await state.set_state(Seller.prod_photo_st)
        await message.answer('Отправьте фото товара')
        return

    prod_card_desc = message.text
    await state.update_data(prod_card_desc=prod_card_desc)
    await state.set_state(Seller.prod_photo_st)
    await message.answer('Отправьте фото товара')

async def choose_prod_unit (message: Message, state: FSMContext):
    if message.text == '◀️ Назад':
        await state.set_state(Seller.prod_unit_st)
        await message.answer ('Выберите ед. измерения', reply_markup=choose_prod_unit_kb)
        return
     
    prod_card_photo = message.photo[-1].file_id
    await state.update_data(prod_card_photo = prod_card_photo)
    await state.set_state(Seller.prod_unit_st)
    await message.answer ('Выберите единицу измерения кол-ва товара', reply_markup=choose_prod_unit_kb)


async def write_prod_availability(callback: CallbackQuery, state: FSMContext):
    prod_card_unit = callback.data.split(':')[1]
    await state.update_data(prod_card_unit = prod_card_unit)
    await state.set_state(Seller.prod_availability_st)
    await callback.message.answer('Введите количество товара в наличии')

async def write_prod_availability_back(message: Message, state: FSMContext):
    await state.set_state(Seller.prod_availability_st)
    await message.answer('Введите количество товара в наличии')

async def write_prod_price(message: Message, state: FSMContext):

    if message.text == '◀️ Назад':
        await state.set_state(Seller.prod_availability_st)
        await message.answer('Введите цену за единицу товара', reply_markup=seller_create_card_kb)
        return
    
    if not message.text.isdigit():
        msg = await message.answer('❌ Введите целое число')
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()
        return
    
    prod_card_availability = int(message.text)
    await state.update_data(prod_card_availability=prod_card_availability)
    await state.set_state(Seller.prod_price_st)
    await message.answer('Введите цену за единицу товара')

async def product_card_complete (message: Message, state: FSMContext):
    price = message.text.replace(',', '.')
    if not price.isdigit():
        msg = await message.answer('❌ Введите число')
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()
        return

    await state.set_state(Seller.prod_card_complete_st)
    prod_card_price = float(price)
    await state.update_data(prod_card_price = prod_card_price)
    await message.answer ('Ваша карточка товара готова, сейчас покажем...')
    await asyncio.sleep(2)
    data = await state.get_data()
    prod_card_name = data.get_data('prod_card_name')
    prod_card_desc = data.get_data('prod_card_desc')
    prod_card_photo = data.get_data('prod_card_photo')
    prod_card_unit = data.get_data('prod_card_unit')
    prod_availability_st = data.get_data('prod_card_availability')
    prod_card_price = data.get_data('prod_card_price')
    today = datetime.date.today()
    date_placement = (today.strftime("%d.%m.%Y"))
    caption = (
            f"<b>Наименование:</b> {prod_card_name}\n"
            f"<b>Описание:</b> {prod_card_desc}\n"
            f"<b>Дата размещения:</b> {date_placement}\n"
            f"<b>Наличие:</b> {availability} {prod_card_unit}\n"
            f"<b>Цена:</b> {price}"
        )
    await message.answer_photo(photo=prod_card_photo, caption=caption,
                               reply_markup=seller_confirm_card_kb,
                               parse_mode="HTML")

async def product_card_write (message: Message, state: FSMContext):
    data = await state.get_data()
    prod_card_name = data.get_data('prod_card_name')
    prod_card_desc = data.get_data('prod_card_desc')
    prod_card_photo = data.get_data('prod_card_photo')
    prod_card_unit = data.get_data('prod_card_unit')
    prod_card_availability = data.get_data('prod_card_availability')
    prod_card_price = data.get_data('prod_card_price')
    user_id = await message.from_user_id()
    today = datetime.date.today()
    date_placement = (today.strftime("%d.%m.%Y"))

    while True:
        prod_card_id = str(random.randint(100, 999))  # Генерация 3-значного ID
        if prod_card_id not in feed_sheet.col_values(1):
            return prod_card_id

    feed_sheet.append_row([prod_card_id, prod_card_name, prod_card_desc,
                           prod_card_photo, date_placement, prod_card_unit,
                           prod_card_availability, prod_card_price])