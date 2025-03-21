from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def add_to_cart_button(product_id):
    cart_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🛒 Добавить в корзину',
                                                                    callback_data=f"add_to_cart:{product_id}")]])
    return cart_button