import asyncio
from datetime import datetime

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from ...google_sheets import feed_sheet, cart_sheet, request_sheet

from ..user_levels.customer_user import Customer

from ...keyboards.inline import *
from ...keyboards.reply import *

class Cart(StatesGroup):
    cart = State()
    choose_quantity = State()

#Вывод всех карточек товаров, находящихся в корзине
async def show_cart(message: Message, state: FSMContext):

    user_id = message.from_user.id
    await state.update_data(user_id = user_id)
    feed_data = feed_sheet.get_all_records()
    cart_data = cart_sheet.get_all_records()[::-1]

    row = next((r for r in cart_data if str(r.get("customer_id")) == str(user_id)), None)
    if row:
        await state.set_state(Cart.cart)
    else:
        await message.answer('❌ Корзина пуста', reply_markup=customer_start_kb)
        return

    #Создание корзины, вывод карточек твоаров по порядку
    order_cards = []
    for cart_row in cart_data:
        if str(cart_row.get("customer_id")) == str(user_id):
            product_id = cart_row.get("product_id")
            quantity = cart_row.get("quantity")
            total_price = float(cart_row.get("total_price"))
            order_pick_date = cart_row.get("order_pick_date")
            for feed_row in feed_data:
                if str(feed_row.get("product_id")) == str(product_id):
                    name = feed_row.get("name")
                    description = feed_row.get("description")
                    photo_id = feed_row.get("photo_id")
                    product_unit = feed_row.get("product_unit")
                    price = feed_row.get("price")
                    availability = feed_row.get("availability")
        
                    caption = (
                        f"<b>Наименование:</b> {name}\n"
                        f"<b>Описание:</b> {description}\n"
                        f"<b>Дата получения:</b> {order_pick_date}\n"
                        f"<b>Объем заказа:</b> {quantity} {product_unit}\n"
                        f"<b>Итоговая цена:</b> {total_price:.2f}₽"
                    )

                    order_card = await message.answer_photo(photo=photo_id, caption=caption,
                                            reply_markup=edit_cart_kb(product_id, availability, price),
                                            parse_mode="HTML")
                    
                    order_cards.append(order_card)
                    break
    await state.update_data(order_cards=order_cards)
    await message.answer('🛒 Добро пожаловать в вашу корзину!', reply_markup=customer_cart_kb)

#Выход из корзины
async def close_cart(message: Message, state: FSMContext):
    data = await state.get_data()
    order_cards = data.get('order_cards', [])[::-1]
    await message.answer('🚪 Вы вышли из корзины', reply_markup=customer_start_kb)
    for card in order_cards:
        await card.delete()
    await state.clear()
    await state.set_state(Customer.customer_start)

#Достаем и записываем переменные ID, кол-ва единиц товара в наличии и цены,
#запрашиваем ввод нового кол-ва единиц товара
async def edit_cart_item_quantity(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    work_piece = callback.data.split(":")[1]
    product_id, availability, price = work_piece.split(",")

    await state.set_state(Cart.choose_quantity)
    tech_msg = await callback.message.answer ('✍️ Введите количество единиц товара.',
                                                     reply_markup=cancel_kb)
    await state.update_data(tech_msg=tech_msg, product_id=product_id,
                            availability=availability, price=price)
    
#Отмена редактирования кол-ва выбранного товара
async def back_to_cart(message: Message, state:FSMContext):
    await state.set_state(Cart.cart)
    data = await state.get_data()
    tech_msg = data.get('tech_msg')
    await message.delete()
    await tech_msg.delete()
    
#Проверяем введенное пользователем значение, вводим его в таблицу
async def write_new_quantity(message: Message, state: FSMContext):

    #Достаем все необходимые переменные
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

    cart_data = cart_sheet.get_all_records()

    #Ищем соответствующую строку, и вписываем туда новые значения
    row = next((r for r in cart_data if str(r.get("customer_id")) == str(user_id)
                and str(r.get("product_id")) == str(product_id)), None)
    if row:
        total_price = float(price) * float(quantity)
        total_price = "{:.2f}".format(total_price)

        old_quantity = row.get("quantity")

        #Найдем индекс строки в GoogleSheets
        row_index = cart_data.index(row) + 2  #+2, потому что get_all_records() возвращает список без заголовка

        #Обновляем ячейки в Google Sheets
        cart_sheet.update_cell(row_index, 3, quantity)
        cart_sheet.update_cell(row_index, 4, total_price)

        #Корректируем кол-во в ленте товаров
        feed_data = feed_sheet.get_all_records()
        availability_row_index = next(
            (i + 2 for i, r in enumerate(feed_data) if str(r.get("product_id")) == str(product_id)),
            None
        )
        feed_sheet.update_cell(availability_row_index, 7, availability - (quantity - old_quantity))
    
    else:
        msg = await message.answer('⚠️ Ошибка: товар не найден в корзине!')
        await asyncio.sleep(3)
        await msg.delete()
        return

    #Удаляем старую корзину
    order_cards = data.get('order_cards', [])[::-1]
    await message.answer('✅ Ваш заказ отредактирован\nПроверьте вашу корзину', reply_markup=customer_start_kb)
    for card in order_cards:
        await card.delete()
    await state.clear()
    await state.set_state(Customer.customer_start)

#Удаление товара из корзины
async def delete_cart_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    product_id = callback.data.split(":")[1]
    user_id = callback.from_user.id

    cart_data = cart_sheet.get_all_records()

    #Ищем выбранную запись и удаляем ее
    row = next((r for r in cart_data if str(r.get("customer_id")) == str(user_id)
                and str(r.get("product_id")) == str(product_id)), None)
    if row:
        row_index = cart_data.index(row) + 2
        cart_sheet.delete_rows(row_index)
        await callback.message.delete()
        data = await state.get_data()
        order_cards = data.get('order_cards')
        order_cards = [
            msg for msg in order_cards if msg.message_id != callback.message.message_id
        ]
        await state.update_data(order_cards=order_cards)

        #Корректируем кол-во в ленте товаров
        feed_data = feed_sheet.get_all_records()
        availability_row_index = next(
            (i + 2 for i, r in enumerate(feed_data) if str(r.get("product_id")) == str(product_id)),
            None
        )
        quantity = row.get("quantity")
        availability = feed_sheet.cell(availability_row_index, 7).value
        feed_sheet.update_cell(availability_row_index, 7, int(availability) + int(quantity))

        msg = await callback.message.answer('✅ Товар успешно удален из корзины!', reply_markup=customer_start_kb)
        await asyncio.sleep(3)
        await msg.delete()
    else:
        msg = await callback.message.answer('⚠️ Ошибка: товар не найден в корзине!')
        await asyncio.sleep(3)
        await msg.delete()
        return

#Оформление заказа
async def purchase(message: Message, state: FSMContext):
    user_id = message.from_user.id

    cart_data = cart_sheet.get_all_records()

    #Находим все строки, которые нужно удалить
    rows_to_delete = [
        i + 2
        for i, row in enumerate(cart_data)
        if str(row.get("customer_id")) == str(user_id)
    ]

    #Если корзина пустая — показываем ошибку и выходим
    if not rows_to_delete:
        msg = await message.answer('⚠️ Ошибка: в корзине отсутствуют товары!')
        await asyncio.sleep(3)
        await msg.delete()
        return

    #Перенос всех данных из таблицы корзины в таблицу заявок
    user_cart_rows = [
        row for row in cart_data
        if str(row.get("customer_id")) == str(user_id)
    ]
    
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    for row in user_cart_rows:
        row["product_name"] = next(str(r.get("name")) for r in feed_sheet.get_all_records()
                           if str(r.get("product_id")) == str(row.get("product_id")))
        row["order_time"] = now
        request_sheet.append_row(list(row.values()))

    #Удаляем строки в обратном порядке
    for row_index in sorted(rows_to_delete, reverse=True):
        cart_sheet.delete_rows(row_index)

    #Удаляем старую корзину
    data = await state.get_data()
    order_cards = data.get('order_cards', [])[::-1]
    await message.answer('✅ Ваш заказ принят в обработку', reply_markup=customer_start_kb)
    for card in order_cards:
        await card.delete()
    await state.clear()
    await state.set_state(Customer.customer_start)