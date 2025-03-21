import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from core.keyboards.reply import start_kb


async def starting_work(message: Message):
    await message.answer(f"Добро пожаловать в магазин!\
                         \nПожалуйста, выберите пункт меню", reply_markup=start_kb)