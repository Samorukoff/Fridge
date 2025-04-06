from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.settings import settings
from ..google_sheets import seller_sheet

#Меню выбора единицы товара при создании карточки продавцов
choose_prod_unit_kb = InlineKeyboardMarkup(inline_keyboard=
                                     [[InlineKeyboardButton(text='Килограмм', callback_data='unit:кг')],
                                      [InlineKeyboardButton(text='Литр', callback_data='unit:л')],
                                      [InlineKeyboardButton(text='Штука', callback_data='unit:шт.')],
                                      [InlineKeyboardButton(text='Упаковка', callback_data='unit:уп.')]])

#Меню выбора адресатов для рассылки от администратора
choose_adressees_kb = InlineKeyboardMarkup(inline_keyboard=
                                     [[InlineKeyboardButton(text='Покупатели', callback_data='adr:customer')],
                                      [InlineKeyboardButton(text='Продавцы', callback_data='adr:seller')],
                                      [InlineKeyboardButton(text='Все пользователи', callback_data='adr:all')]])

#Кнопки карточек в ленте товаров
def add_to_cart_kb(user_id, product_id, availability, price):
    #Если пользователь админ либо продавец заместо добавления в корзину даем возможность удалить карточку
    if user_id == settings.bots.admin_id or str(user_id) in seller_sheet.col_values(1):
        customer_feed_inline_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Удалить товар',
                                                callback_data=f"del_from_feed:{product_id}")]])
        return customer_feed_inline_kb
    else: 
        customer_feed_inline_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🛒 Добавить в корзину',
                                                callback_data=f"add_to_cart:{product_id},{availability},{price}")]])
        return customer_feed_inline_kb

#Кнопки карточек в корзине
def edit_cart_kb(product_id, availability, price):
    customer_cart_inline_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✏️ Изменить кол-во',
                                            callback_data=f"edit_cart:{product_id},{availability},{price}")],
                                                        [InlineKeyboardButton(text='🗑 Удалить товар',
                                            callback_data=f"del_cart:{product_id}")]])
    return customer_cart_inline_kb

#Кнопки под заявками для продавца
def approve_request(customer_id, product_id):
    approve_request_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Одобрить заявку',
                                            callback_data=f"request:apply:{customer_id},{product_id}")],
                                                        [InlineKeyboardButton(text='❌ Отклонить заявку',
                                            callback_data=f"request:deny:{customer_id},{product_id}")]])
    return approve_request_kb