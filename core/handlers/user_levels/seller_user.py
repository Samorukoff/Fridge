import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from ...google_sheets import feed_sheet, cart_sheet
from ...keyboards.inline import *
from ...keyboards.reply import *

class Seller(StatesGroup):
    seller_start = State()

async def instruction(message: Message, state: FSMContext):
    await message.answer('Инструкция')
