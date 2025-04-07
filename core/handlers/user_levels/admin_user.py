import uuid

from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from ...google_sheets import link_sheet, customer_sheet, seller_sheet
from ...keyboards.inline import *
from ...keyboards.reply import *

from core.settings import settings

class Admin(StatesGroup):
    admin_start = State()
    admin_mailing = State()
    admin_mailing_choose = State()

BOT_USERNAME = 'Fridge_Nil_Bot'

async def instruction(message: Message):
    await message.answer('Инструкция')

async def invite_link(message: Message):
    token = str(uuid.uuid4())
    link = f"https://t.me/{BOT_USERNAME}?start={token}"

    link_sheet.append_row([token, "unused"])
    await message.answer(f'Одноразовая ссылка готова:\n{link}')

async def give_google_sheets_link (message:Message):
    await message.answer (f'Ссылка на базу данных чат бота в Google Sheets:\n{settings.bots.gs_link}')

async def mailing (message:Message, state: FSMContext):
    await state.set_state(Admin.admin_mailing)
    await message.answer ('✍️ Пожалуйста, введите сообщение для рассылки.', reply_markup=step_kb)

async def choose_adressees (message:Message, state: FSMContext):
    mailing_message = message.text
    await state.update_data(mailing_message=mailing_message)
    await state.set_state(Admin.admin_mailing_choose)
    await message.answer('📩 Пожалуйста, выберите адресатов:\
                          \n⚠️ Внимание, после выбора адресатов сообщение сразу отправится в рассылку!',
                           reply_markup=choose_adressees_kb)
    
async def send_adressees (callback:CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    mailing_message = data.get('mailing_message')
    adressees = callback.data.split(':')[1]
    if adressees == 'customer' or adressees == 'all':
        for user in customer_sheet.col_values(1)[1:]:
            await bot.send_message(int(user), mailing_message)
    if adressees == 'seller' or adressees == 'all':
        for user in seller_sheet.col_values(1)[1:]:
            await bot.send_message(int(user), mailing_message)
    await callback.message.answer('✅ Рассылка успешно отправлена!', reply_markup=admin_start_kb)
    await state.clear()
    await state.set_state(Admin.admin_start)
