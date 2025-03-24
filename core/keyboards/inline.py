from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#Кнопки карточек в ленте товаров
def add_to_cart_kb(product_id, availability, price):
    feed_inline_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🛒 Добавить в корзину',
                                            callback_data=f"add_to_cart:{product_id},{availability},{price}")]])
    return feed_inline_kb

#Кнопки карточек в корзине
def edit_cart_kb(product_id, availability, price):
    cart_inline_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✏️ Изменить кол-во',
                                            callback_data=f"edit_cart:{product_id},{availability},{price}")],
                                                        [InlineKeyboardButton(text='🗑 Удалить товар',
                                            callback_data=f"del_cart:{product_id}")]])
    return cart_inline_kb