from aiogram import F, Router, types
from aiogram.filters import Command


from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())


ADMIN_KB = get_keyboard(
    "Add product",
    "Assortment",
    "Add / edit banner",
    placeholder="Choose an action",
    sizes=(2,),
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Hi! What do you want to do?", reply_markup=ADMIN_KB)