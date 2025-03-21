from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)

start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Просмотреть ленту товаров'), 
                                          KeyboardButton(text='Просмотреть корзину')],
                                         [KeyboardButton(text='Перезапуск')]],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите действие...')