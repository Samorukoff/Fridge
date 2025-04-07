import asyncio
import datetime
import random

from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from ...google_sheets import feed_sheet, request_sheet
from ...keyboards.inline import *
from ...keyboards.reply import *

class Seller(StatesGroup):
    seller_start = State()
    check_requests_st = State()
    prod_name_st = State()
    prod_desc_st = State()
    prod_photo_st = State()
    prod_unit_st = State()
    prod_availability_st = State()
    prod_price_st = State()
    prod_card_complete_st = State()

#Вывод инструкции
async def instruction(message: Message):
    await message.answer('Инструкция')

#Вывод заявок
async def check_requests(message: Message, state: FSMContext, bot: Bot):

    feed_data = feed_sheet.get_all_records()
    request_data = request_sheet.get_all_records()

    our_products = [
        str(row.get("product_id"))
        for row in feed_data if str(row.get("seller_id")) == str(message.from_user.id)
    ]
    
    our_requests = [
        row for row in request_data if str(row.get("product_id")) in our_products 
    ]
    req_cards = []
    if our_requests:
        await state.set_state(Seller.check_requests_st)
        await message.answer ('📋 Актуальные заявки:', reply_markup=leave_requests_kb)
        for row in our_requests:
            customer_id = row.get("customer_id")
            product_id = row.get("product_id")
            customer = await bot.get_chat(customer_id)
            product_name = row.get("product_name")
            quantity = row.get("quantity")
            total_price = float(row.get("total_price"))
            total_price = "{:.2f}".format(total_price)
            order_time = row.get("order_time")
            order_pick_date = row.get("order_pick_date")

            caption = (
                f"<b>Профиль заказчика:</b> @{customer.username}\n"
                f"<b>Имя заказчика:</b> {customer.first_name} {customer.last_name}\n"
                f"<b>Наименование товара:</b> {product_name}\n"
                f"<b>Дата:</b> {order_time.split(' ')[0]}\n"
                f"<b>Время:</b> {order_time.split(' ')[1]}\n"
                f"<b>Кол-во позиций:</b> {quantity}\n"
                f"<b>Стоимость заказа:</b> {total_price}₽\n"
                f"<b>Дата выдачи:</b> {order_pick_date}"
            )
            request_card = await message.answer(caption, parse_mode='HTML',
                                                reply_markup=approve_request(customer_id, product_id))
            req_cards.append(request_card)
            await state.update_data(req_cards=req_cards)
    else:
        await message.answer('⚠️ Заявок не найдено.')

#Выход из меню заявок
async def leave_requests(message: Message, state: FSMContext):
    data = await state.get_data()
    req_cards = data.get('req_cards', [])[::-1]
    if req_cards:
        for card in req_cards:
            await card.delete()
    await state.clear()
    await state.set_state(Seller.seller_start)
    await message.answer('🚪 Вы вышли из меню запросов', reply_markup=seller_start_kb)

#Одобрение/Отклонение заявки
async def apply_requests(callback: CallbackQuery, state: FSMContext, bot: Bot):
    status, work_piece = callback.data.split(':')[1:]
    customer_id, product_id = work_piece.split(',')
    customer = await bot.get_chat(customer_id)
    request_data = request_sheet.get_all_records()

    #Поиск доп. значений о позиции
    req = next(
        (row for row in request_data if str(row.get('customer_id')) == customer_id
         and str(row.get('product_id')) == product_id),
         None
    )
    
    product_name = req.get('product_name')
    quantity = req.get('quantity')
    total_price = float(str(req.get('total_price')).replace(',', '.'))
    total_price = "{:.2f}".format(total_price)
    order_time = req.get('order_time')
    order_pick_date = req.get('order_pick_date')

    #Очистка заявки
    rows_to_delete = [i + 2 for i, row in enumerate(request_data)
                        if str(row.get('customer_id')) == customer_id
                        and str(row.get('product_id')) == product_id]

    for row_index in sorted(rows_to_delete, reverse=True):
        request_sheet.delete_rows(row_index)
    
    await callback.message.delete()
    data = await state.get_data()
    req_cards = data.get('req_cards')
    req_cards = [
        msg for msg in req_cards if msg.message_id != callback.message.message_id
    ]
    await state.update_data(req_cards=req_cards)

    #Рассылка
    if status == 'apply':
        await bot.send_message(int(customer_id),
                               f'✅ Ваш заказ от {order_time.split(" ")[0]} '
                               f'на {quantity} единиц позиции "{product_name}" '
                               f'на сумму {total_price}₽ был одобрен!\n'
                               f'Дата получения: {order_pick_date}\n'
                               f'Ваш код: {random.randint(100000, 999999)}')
        await callback.message.answer(f'✅ Заказ пользователя @{customer.username} от {order_time.split(" ")[0]} '
                                      f'на {quantity} единиц позиции "{product_name}" '
                                      f'на сумму {total_price}₽ был одобрен!\n'
                                      f'Дата выдачи: {order_pick_date}')
    if status == 'deny':
        #Корректируем кол-во в ленте товаров
        feed_data = feed_sheet.get_all_records()
        availability_row_index = next(
            (i + 2 for i, r in enumerate(feed_data) if str(r.get("product_id")) == str(product_id)),
            None
        )
        availability = feed_sheet.cell(availability_row_index, 7).value
        feed_sheet.update_cell(availability_row_index, 7, int(availability) + int(quantity))

        await bot.send_message(int(customer_id),
                                f'❌ Ваш заказ от {order_time.split(" ")[0]} '
                                f'на {quantity} единиц позиции "{product_name}" '
                                f'на сумму {total_price}₽ был отклонен.')
        await callback.message.answer(f'❌ Заказ пользователя @{customer.username} от {order_time.split(" ")[0]} '
                                      f'на {quantity} единиц позиции "{product_name}" '
                                      f'на сумму {total_price}₽ был отклонен.')

#Конструктор карточки товара
async def write_prod_name (message: Message, state: FSMContext):
    await state.set_state(Seller.prod_name_st)
    await message.answer ('✍️ Введите наименование товара.', reply_markup=step_kb)

async def write_prod_desc(message: Message, state: FSMContext):
    if message.text == '◀️ Назад':
        await state.set_state(Seller.prod_desc_st)
        await message.answer('✍️ Введите описание товара.')
        return

    prod_card_name = message.text
    await state.update_data(prod_card_name=prod_card_name)
    await state.set_state(Seller.prod_desc_st)
    await message.answer('✍️ Введите описание товара.')

async def download_prod_photo(message: Message, state: FSMContext):
    if message.text == '◀️ Назад':
        await state.set_state(Seller.prod_photo_st)
        await message.answer('📷 Отправьте фото товара.')
        return

    prod_card_desc = message.text
    await state.update_data(prod_card_desc=prod_card_desc)
    await state.set_state(Seller.prod_photo_st)
    await message.answer('📷 Отправьте фото товара.')

async def choose_prod_unit (message: Message, state: FSMContext):
    if message.text == '◀️ Назад':
        await state.set_state(Seller.prod_unit_st)
        await message.answer ('⚖️ Выберите ед. измерения:', reply_markup=choose_prod_unit_kb)
        return
     
    prod_card_photo = message.photo[-1].file_id
    await state.update_data(prod_card_photo = prod_card_photo)
    await state.set_state(Seller.prod_unit_st)
    await message.answer ('⚖️ Выберите единицу измерения:', reply_markup=choose_prod_unit_kb)


async def write_prod_availability(callback: CallbackQuery, state: FSMContext):
    prod_card_unit = callback.data.split(':')[1]
    await state.update_data(prod_card_unit = prod_card_unit)
    await state.set_state(Seller.prod_availability_st)
    await callback.message.answer('🔢 Введите количество товара в наличии.')

async def write_prod_availability_back(message: Message, state: FSMContext):
    await state.set_state(Seller.prod_availability_st)
    await message.answer('🔢 Введите количество товара в наличии.')

async def write_prod_price(message: Message, state: FSMContext):

    if message.text == '◀️ Назад':
        await state.set_state(Seller.prod_price_st)
        await message.answer('💸 Введите цену за единицу товара в рублях.', reply_markup=step_kb)
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
    await message.answer('💸 Введите цену за единицу товара в рублях.')

async def product_card_complete (message: Message, state: FSMContext):
    price_text = message.text.replace(',', '.')

    try:
        price = float(price_text)
    except ValueError:
        msg = await message.answer('❌ Введите корректное число (например: 99.99)')
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()
        return

    await state.set_state(Seller.prod_card_complete_st)
    prod_card_price = float(price)
    await state.update_data(prod_card_price = prod_card_price)
    await message.answer ('✅ Ваша карточка товара готова, сейчас покажем...')
    data = await state.get_data()
    prod_card_name = data.get('prod_card_name')
    prod_card_desc = data.get('prod_card_desc')
    prod_card_photo = data.get('prod_card_photo')
    prod_card_unit = data.get('prod_card_unit')
    prod_card_availability = data.get('prod_card_availability')
    prod_card_price = data.get('prod_card_price')
    today = datetime.date.today()
    date_placement = (today.strftime("%d.%m.%Y"))
    caption = (
            f"<b>Наименование:</b> {prod_card_name}\n"
            f"<b>Описание:</b> {prod_card_desc}\n"
            f"<b>Дата размещения:</b> {date_placement}\n"
            f"<b>Наличие:</b> {prod_card_availability} {prod_card_unit}\n"
            f"<b>Цена за {prod_card_unit}:</b> {prod_card_price:.2f}₽"
        )
    await message.answer_photo(photo=prod_card_photo, caption=caption,
                               reply_markup=seller_confirm_card_kb,
                               parse_mode="HTML")

async def product_card_write (message: Message, state: FSMContext):
    data = await state.get_data()
    prod_card_name = data.get('prod_card_name')
    prod_card_desc = data.get('prod_card_desc')
    prod_card_photo = data.get('prod_card_photo')
    prod_card_unit = data.get('prod_card_unit')
    prod_card_availability = data.get('prod_card_availability')
    prod_card_price = data.get('prod_card_price')
    user_id = message.from_user.id
    today = datetime.date.today()
    date_placement = (today.strftime("%d.%m.%Y"))

    while True:
        prod_card_id = str(random.randint(100, 999))  # Генерация 3-значного ID
        if prod_card_id not in feed_sheet.col_values(1):
            break

    feed_sheet.append_row([prod_card_id, prod_card_name, prod_card_desc,
                           prod_card_photo, date_placement, prod_card_unit,
                           prod_card_availability, prod_card_price, user_id])
    
    await message.answer('✅ Поздравляем, ваша карточка успешно загружена в ленту товаров!',
                         reply_markup=seller_start_kb)
    await state.clear()
    await state.set_state(Seller.seller_start)