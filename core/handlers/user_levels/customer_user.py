from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from ...keyboards.inline import *
from ...keyboards.reply import *

class Customer(StatesGroup):
    customer_start = State()

async def test(message: Message, state: FSMContext):
    await message.answer('Инструкция')