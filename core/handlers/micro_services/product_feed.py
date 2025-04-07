import asyncio
from datetime import datetime, timedelta

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram_calendar.simple_calendar import SimpleCalendar, SimpleCalendarCallback

from ...google_sheets import feed_sheet, cart_sheet

from ...keyboards.inline import *
from ...keyboards.reply import *

class ProductFeed(StatesGroup):
    product_feed = State()
    choose_quantity = State()
    choosing_date = State()

#Число товаров, выводимых за один раз
ITEMS_PER_PAGE = 7

#Вывод всех карточек товаров
async def show_feed (message: Message, state: FSMContext):

    #Лента открыта с нуля, или мы догружаем товары?
    if message.text == '📜 Просмотреть ленту товаров':
        previous_state = await state.get_state()
        await state.update_data(previous_state = previous_state)
        await state.set_state(ProductFeed.product_feed)
        is_new_request = True
    elif message.text == '🔽 Показать еще':
        is_new_request = False
    else:
         return
    
    #Список для дальнейшего удаления всех карточек
    data = await state.get_data()
    product_cards = data.get('product_cards', [])

    #Если мы догружаем товары, то продолжаем там, где закончили
    feed_data = feed_sheet.get_all_records()[::-1]
    data = await state.get_data()
    offset = 0 if is_new_request else data.get('offset', 0)
    user_id = message.from_user.id
    await state.update_data(user_id = user_id)
    
    # Фильтрация товаров, если продавец
    seller_id_data = seller_sheet.col_values(1) 
    is_seller = str(user_id) in seller_id_data

    filtered_feed_data = [r for r in feed_data if not is_seller or str(r.get("seller_id")) == str(user_id)]

    items = filtered_feed_data[offset:offset + ITEMS_PER_PAGE]

    #Товаров больше нет - завершаем функцию
    if not items:
        msg = await message.answer("⚠️ Товаров больше нет")
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()
        return
    
    #Создание ленты товаров, вывод карточек по порядку
    seller_id_data = seller_sheet.col_values(1) 
    is_seller = str(user_id) in seller_id_data and user_id != settings.bots.admin_id

    for row in items:

        product_id = row.get("product_id")
        name = row.get("name")
        description = row.get("description")
        photo_id = row.get("photo_id")
        date_placement = row.get("date_placement")
        product_unit = row.get("product_unit")
        availability = row.get("availability")
        price = row.get("price")

        caption = (
            f"<b>Наименование:</b> {name}\n"
            f"<b>Описание:</b> {description}\n"
            f"<b>Дата размещения:</b> {date_placement}\n"
            f"<b>Наличие:</b> {availability} {product_unit}\n"
            f"<b>Цена за {product_unit}:</b> {price:.2f}₽"
        )

        product_card = await message.answer_photo(photo=photo_id, caption=caption,
                                reply_markup=add_to_cart_kb(user_id, product_id, availability, price),
                                parse_mode="HTML")
        
        product_cards.append(product_card)
    await state.update_data(product_cards=product_cards)

    #Фиксируем факт выгрузки для последующего вывода
    new_offset = offset + ITEMS_PER_PAGE
    await state.update_data(offset=new_offset)

    # Показываем кнопку "Еще", если есть товары
    if new_offset < len(filtered_feed_data):
        await message.answer("🔽 Загрузить еще товары?", reply_markup=feed_kb)
    elif new_offset >= len(filtered_feed_data):
        await message.answer("⚠️ Товаров больше нет", reply_markup=feed_kb)

#Выход из ленты товаров
async def close_feed(message: Message, state: FSMContext):
    data = await state.get_data()
    previous_state = data.get('previous_state')
    product_cards = data.get('product_cards',[])[::-1]
    user_id = data.get('user_id')
    await message.answer('🚪 Вы вышли из ленты товаров', reply_markup=main_kb(user_id))
    for card in product_cards:
        await card.delete()
    await state.clear()
    await state.set_state(previous_state)

#Достаем и записываем переменные ID, кол-ва единиц товара в наличии и цены,
#запрашиваем ввод необходимого кол-ва единиц товара
async def write_to_cart(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    work_piece = callback.data.split(":")[1]
    product_id, availability, price = work_piece.split(",")
    data = await state.get_data()
    user_id = data.get('user_id')

    cart_data = cart_sheet.get_all_records()
    row = next((r for r in cart_data if str(r.get("customer_id")) == str(user_id)
                and str(r.get("product_id")) == str(product_id)), None)
    if row:
        msg = await callback.message.answer('❌ Товар уже находится в корзине!')
        await asyncio.sleep(3)
        await msg.delete()
        return

    await state.set_state(ProductFeed.choose_quantity)
    tech_msg = await callback.message.answer('✍️ Введите количество единиц товара.',
                                                     reply_markup=cancel_kb)
    await state.update_data(tech_msg=tech_msg, product_id=product_id,
                            availability=availability, price=price)

#Отмена добавления в корзину выбранного товара
async def back_to_feed(message: Message, state:FSMContext):
    await state.set_state(ProductFeed.product_feed)
    data = await state.get_data()
    tech_msg = data.get('tech_msg')
    await message.delete()
    await tech_msg.delete()

#Проверка запрошенного количества и запись данных в таблицу (корзину)
async def check_and_choose_date(message: Message, state:FSMContext):

    #Достаем необходимые переменные
    data = await state.get_data()
    availability = int(data.get('availability'))
    price = float(data.get('price'))

    #Проверка
    if not message.text.isdigit():
        msg = await message.answer('❌ Введите целое число')
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()
        return
    
    quantity = int(message.text)
    if quantity < 1 or quantity > availability:
        msg = await message.answer (f'❌ В наличии только {availability} ед. товара')
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()
        return
    
    total_price = float(price) * float(quantity)
    total_price = "{:.2f}".format(total_price)
    await state.update_data(total_price=total_price)
    await state.update_data(quantity=quantity)

    await message.answer("📅 Пожалуйста, выберите дату получения заказа:",
                         reply_markup=await SimpleCalendar().start_calendar())
    await state.set_state(ProductFeed.choosing_date)

async def add_to_cart(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    availability = data.get('availability')
    quantity = data.get('quantity')
    total_price = data.get('total_price')

    #Обработка выбранной с календаря даты
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)

    if selected:
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        max_date = now + timedelta(days=90)

        if date > max_date:
            await callback_query.message.answer(
                "📅 Дата получения не может быть позже 90 дней от сегодняшнего дня.\n"
                "Пожалуйста, выберите другую дату:",
                reply_markup=await SimpleCalendar().start_calendar()
            )
            return

        elif date < tomorrow:
            await callback_query.message.answer(
                "📅 Заказ можно оформить только на завтра или позже.\n"
                "Пожалуйста, выберите другую дату:",
                reply_markup=await SimpleCalendar().start_calendar()
            )
            return
        
        order_pick_date = date.strftime('%d.%m.%Y')

        #Запись в таблицу (корзину)
        cart_sheet.append_row([user_id, product_id, quantity, total_price, order_pick_date])

        # #Корректируем кол-во в ленте товаров
        feed_data = feed_sheet.get_all_records()
        availability_row_index = next(
            (i + 2 for i, row in enumerate(feed_data) if str(row.get("product_id")) == str(product_id)),
            None
        )
        feed_sheet.update_cell(availability_row_index, 7, int(availability) - int(quantity))

        await callback_query.message.answer('✅ Товар успешно добавлен в корзину!\nВыберите еще', reply_markup=feed_kb)
        await state.set_state(ProductFeed.product_feed)

#Удаление товара из ленты
async def delete_feed_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    product_id = callback.data.split(":")[1]

    feed_data = feed_sheet.get_all_records()
    #Ищем выбранную запись и удаляем ее
    row = next((r for r in feed_data if str(r.get("product_id")) == str(product_id)), None)
    if row:
        row_index = feed_data.index(row) + 2
        feed_sheet.delete_rows(row_index)
        await callback.message.delete()
        data = await state.get_data()
        product_cards = data.get('product_cards')
        product_cards = [
            msg for msg in product_cards if msg.message_id != callback.message.message_id
        ]
        await state.update_data(product_cards=product_cards)
        msg = await callback.message.answer('✅ Карточка товара успешно удалена')
        await asyncio.sleep(3)
        await msg.delete()
    else:
        msg = await callback.message.answer('⚠️ Ошибка: товар не найден в ленте товаров!')
        await asyncio.sleep(3)
        await msg.delete()
        return