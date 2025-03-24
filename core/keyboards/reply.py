from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)

#Начальная клавиатура
start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='📜 Просмотреть ленту товаров'), 
                                          KeyboardButton(text='🛒 Просмотреть корзину')],
                                         [KeyboardButton(text='🔄 Перезапуск')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

#Клавиатура ленты товаров
feed_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🔽 Показать еще')],
                                        [KeyboardButton(text='🛒 Просмотреть корзину'), 
                                          KeyboardButton(text='🚪 Выйти')]],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

#Клавиатура отмены выбора
cancel_pick_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

#Клавиатура корзины
cart_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='✅ Оформить заказ')],
                                        [KeyboardButton(text='📜 Просмотреть ленту товаров'), 
                                          KeyboardButton(text='🚪 Выйти')]],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')