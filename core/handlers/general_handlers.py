from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..google_sheets import customer_sheet, seller_sheet, link_sheet

from ..keyboards.inline import *
from ..keyboards.reply import *

from core.handlers.user_levels.admin_user import Admin
from core.handlers.user_levels.seller_user import Seller
from core.handlers.user_levels.customer_user import Customer

from core.settings import settings

#Проверка токена на актуальность (Токен одноразовый)
def check_and_activate_token(token):
    records = link_sheet.get_all_records()
    for i, row in enumerate(records):
        if row["link_id"] == token and row["status"] == "unused":
            link_sheet.update_cell(i + 2, 2, "used")
            return True
    return False

#Определение уровня пользователя
async def starting_work(message: Message, state: FSMContext):
    #Админ
    if message.from_user.id == settings.bots.admin_id:
        await state.set_state(Admin.admin_start)
        await message.answer(f"🔧 Приветствуем вас, администратор!\
                         \nПожалуйста, выберите пункт меню", reply_markup=admin_start_kb)
    #Продавец уже есть в таблице (Повторная авторизация)
    elif str(message.from_user.id) in seller_sheet.col_values(1):
        await state.set_state(Seller.seller_start)
        await message.answer(f"💼 Приветствуем вас, продавец!\
                         \nПожалуйста, выберите пункт меню", reply_markup=seller_start_kb)
    else:
        #Проверка на наличие параметра в комманде /start (проверка на особую ссылку)
        args = message.text.split(maxsplit=1)
        if len(args) > 1 and message.text != '🔄 Перезапуск':
            token = args[1]
            #Проверка токена на актуальность
            if check_and_activate_token(token):
                seller_sheet.append_row([message.from_user.id])
                await state.set_state(Seller.seller_start)
                await message.answer(f"💼 Приветствуем вас, продавец!\
                         \nПожалуйста, выберите пункт меню", reply_markup=seller_start_kb)
            #Токен неактуален
            else:
                await message.answer("⚠️ Эта ссылка уже была использована или некорректна.")
        #Простой покупатель
        else:
            await state.set_state(Customer.customer_start)   
            if str(message.from_user.id) not in customer_sheet.col_values(1):
                customer_sheet.append_row([message.from_user.id])
            await message.answer(f"✨ Добро пожаловать в магазин!\
                         \nПожалуйста, выберите пункт меню", reply_markup=customer_start_kb)
    