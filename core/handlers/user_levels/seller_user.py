import asyncio

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
    prod_card_complete = State()

async def instruction(message: Message, state: FSMContext):
    await message.answer('Инструкция')

async def write_prod_name (message: Message, state: FSMContext):
    await state.set_state(Seller.prod_name_st)
    await message.answer ('Введите наименование товара')

async def write_prod_desc(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(Seller.prod_name_st)
        await message.answer('Введите название товара')
        return

    prod_card_name = message.text
    await state.update_data(prod_card_name=prod_card_name)
    await state.set_state(Seller.prod_desc_st)
    await message.answer('Введите описание товара')

async def download_prod_photo(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(Seller.prod_desc_st)
        await message.answer('Введите описание товара')
        return

    prod_card_desc = message.text
    await state.update_data(prod_card_desc=prod_card_desc)
    await state.set_state(Seller.prod_photo_st)
    await message.answer('Отправьте фото карточки товара')

async def choose_prod_unit (message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(Seller.prod_unit_st)
        await message.answer ('Выберите единицу измерения кол-ва товара', reply_markup=choose_prod_unit_kb)
        return
    
    if message.photo:   
        prod_card_photo = message.photo[-1].file_id
        await state.update_data(prod_card_photo = prod_card_photo)
        await state.set_state(Seller.prod_unit_st)
        await message.answer ('Выберите единицу измерения кол-ва товара', reply_markup=choose_prod_unit_kb)
    else:
        await message.answer('Не подходящий формат сообщения, попробуйте еще раз')

async def write_prod_availability(callback: CallbackQuery, state: FSMContext):
    prod_card_availability = callback.data.split(':')[1]
    await state.update_data(prod_card_availability = prod_card_availability)
    await state.set_state(Seller.prod_availability_st)
    await callback.message.answer('Введите количество товара в наличии')

async def write_prod_availability_back(message: Message, state: FSMContext):
    await state.set_state(Seller.prod_availability_st)
    await message.answer('Введите количество товара в наличии')

async def write_prod_price(message: Message, state: FSMContext):

    if message.text == 'Назад':
        await state.set_state(Seller.prod_availability_st)
        await message.answer('Введите цену за единицу товара')
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

    await state.set_state(Seller.prod_card_complete)
    prod_card_availability = float(price)
    await state.update_data(prod_card_availability = prod_card_availability)
    await message.answer ('Ваша карточка товара готова, сейчас покажем...')
    await asyncio.sleep(2)
    data = await state.get_data()
    await message.answer('aboba')