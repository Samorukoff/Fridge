import asyncio
import uuid

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from ...google_sheets import link_sheet
from ...keyboards.inline import *
from ...keyboards.reply import *

class Admin(StatesGroup):
    admin_start = State()
    admin_link = State()

BOT_USERNAME = 'Fridge_Nil_Bot'

async def instruction(message: Message, state: FSMContext):
    await message.answer('Инструкция')

async def invite_link(message: Message, state: FSMContext):
    token = str(uuid.uuid4())
    link = f"https://t.me/{BOT_USERNAME}?start={token}"

    link_sheet.append_row([token, "unused"])
    await message.answer(f'Одноразовая ссылка готова:\n{link}')
