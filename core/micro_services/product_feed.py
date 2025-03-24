import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from ..google_sheets import feed_sheet, cart_sheet
from ..keyboards.inline import *
from ..keyboards.reply import *

class ProductFeed(StatesGroup):
    product_feed = State()
    choose_quantity = State()

#Число товаров, выводимых за один раз
ITEMS_PER_PAGE = 7

#Вывод всех карточек товаров
async def show_feed (message: Message, state: FSMContext):

    #Лента открыта с нуля, или мы догружаем товары?
    if message.text == '📜 Просмотреть ленту товаров':
        #Выход из корзины
        data = await state.get_data()
        order_cards = data.get('order_cards', [])[::-1]
        for card in order_cards:
            await card.delete()
            await state.clear()
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
    items = feed_data[offset:offset + ITEMS_PER_PAGE]

    #Товаров больше нет - завершаем функцию
    if not items:
        msg = await message.answer("⚠️ Товаров больше нет")
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()
        return
    
    #Создание ленты товаров, вывод карточек по порядку
    for row in items:
            product_id = row.get("product_id")
            name = row.get("name")
            description = row.get("description")
            photo_id = row.get("photo_id")
            date_placement = row.get("date_placement")
            delivery_time = row.get("delivery_time")
            product_unit = row.get("product_unit")
            availability = row.get("availability")
            price = row.get("price")

            caption = (
                f"<b>Наименование:</b> {name}\n"
                f"<b>Описание:</b> {description}\n"
                f"<b>Дата размещения:</b> {date_placement}\n"
                f"<b>Срок поставки:</b> {delivery_time}\n"
                f"<b>Единица товара:</b> {product_unit}\n"
                f"<b>Наличие:</b> {availability}\n"
                f"<b>Цена:</b> {price}"
            )

            product_card = await message.answer_photo(photo=photo_id, caption=caption,
                                    reply_markup=add_to_cart_kb(product_id, availability, price),
                                    parse_mode="HTML")
            
            product_cards.append(product_card)
    await state.update_data(product_cards=product_cards)

    #Фиксируем факт выгрузки для последующего вывода
    new_offset = offset + ITEMS_PER_PAGE
    await state.update_data(offset=new_offset)

    # Показываем кнопку "Еще", если есть товары
    if new_offset < len(feed_data):
        await message.answer("🔽 Загрузить еще товары?", reply_markup=feed_kb)
    elif new_offset >= len(feed_data):
        await message.answer("⚠️ Товаров больше нет", reply_markup=feed_kb)

#Выход из ленты товаров
async def close_feed(message: Message, state: FSMContext):
    data = await state.get_data()
    product_cards = data.get('product_cards',[])[::-1]
    await message.answer('Выберите пункт меню', reply_markup=start_kb)
    for card in product_cards:
        await card.delete()
    await state.clear()

#Достаем и записываем переменные ID, кол-ва единиц товара в наличии и цены,
#запрашиваем ввод необходимого кол-ва единиц товара
async def write_to_cart(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    work_piece = callback.data.split(":")[1]
    product_id, availability, price = work_piece.split(",")
    user_id = callback.from_user.id

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
                                                     reply_markup=cancel_pick_kb)
    await state.update_data(tech_msg=tech_msg, product_id=product_id,
                            availability=availability, price=price, user_id=user_id)

#Отмена добавления в корзину выбранного товара
async def back_to_feed(message: Message, state:FSMContext):
    await state.set_state(ProductFeed.product_feed)
    data = await state.get_data()
    tech_msg = data.get('tech_msg')
    await message.delete()
    await tech_msg.delete()

#Проверка запрошенного количества и запись данных в таблицу (корзину)
async def add_to_cart(message: Message, state:FSMContext):

    #Достаем необходимые переменные
    data = await state.get_data()
    user_id = data.get('user_id')
    product_id = data.get('product_id')
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

    #Запись в таблицу (корзину)
    cart_sheet.append_row([user_id, product_id, quantity, total_price])
    await message.answer('✅ Товар успешно добавлен в корзину!\nВыберите еще', reply_markup=feed_kb)
    await state.set_state(ProductFeed.product_feed)