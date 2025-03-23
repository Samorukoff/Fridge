from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)

start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='📜 Просмотреть ленту товаров'), 
                                          KeyboardButton(text='🛒 Просмотреть корзину')],
                                         [KeyboardButton(text='🔄 Перезапуск')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

feed_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🔽 Показать еще')],
                                        [KeyboardButton(text='🛒 Просмотреть корзину'), 
                                          KeyboardButton(text='🚪 Выйти')]],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

cancel_feed_pick_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')

cart_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🗑 Очистить корзину')],
                                        [KeyboardButton(text='📜 Просмотреть ленту товаров'), 
                                          KeyboardButton(text='🚪 Выйти')]],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите действие ⬇️')