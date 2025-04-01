from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)

from core.settings import settings
from ..google_sheets import seller_sheet

################################################ ПОКУПАТЕЛЬ ##################################################

#Начальная клавиатура покупателя
customer_start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='📜 Просмотреть ленту товаров'), 
                                          KeyboardButton(text='🛒 Просмотреть корзину')],
                                         [KeyboardButton(text='📘 Инструкция')],
                                         [KeyboardButton(text='🔄 Перезапуск')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

#Клавиатура корзины
customer_cart_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='✅ Оформить заказ')],
                                                 [KeyboardButton(text='🚪 Выйти')],
                                                 [KeyboardButton(text='🔄 Перезапуск')]],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

################################################ ПРОДАВЕЦ ##################################################

#Начальная клавиатура продавца
seller_start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='📘 Инструкция'), 
                                                 KeyboardButton(text='📝 Заявки')],
                                                [KeyboardButton(text='📦 Разместить товар'), 
                                                 KeyboardButton(text='📜 Просмотреть ленту товаров')],
                                                [KeyboardButton(text='🔄 Перезапуск')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

################################################ АДМИНИСТРАТОР ##################################################

#Начальная клавиатура администратора
admin_start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='📘 Инструкция'), 
                                                KeyboardButton(text='📤 Рассылка')],
                                               [KeyboardButton(text='🔗 Ссылка на GoogleSheets'), 
                                                KeyboardButton(text='📜 Просмотреть ленту товаров')],
                                               [KeyboardButton(text='🔑 Создать ссылку-приглашение')],
                                               [KeyboardButton(text='🔄 Перезапуск')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

################################################ ОБЩИЕ ##################################################

#Клавиатура ленты товаров
feed_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🔽 Показать еще')],
                                                 [KeyboardButton(text='🚪 Выйти')],
                                                 [KeyboardButton(text='🔄 Перезапуск')]],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

#Клавиатура отмены выбора
cancel_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')],
                                          [KeyboardButton(text='🔄 Перезапуск')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

#Поиск главной клавиатуры
def main_kb(user_id):
    if user_id == settings.bots.admin_id:
        return admin_start_kb
    elif str(user_id) in seller_sheet.col_values(1):
        return seller_start_kb
    else:
        return customer_start_kb