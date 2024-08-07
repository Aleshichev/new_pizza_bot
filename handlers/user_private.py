from aiogram import F, types, Router
from aiogram.filters import CommandStart
from filters.chat_types import ChatTypeFilter


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))



@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Hello!')
    