from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession


from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard
from kbds.inline import get_callback_btns


from database.orm_query.category import (
    orm_get_categories,
)


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


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


### -----------------  FSM  add/edit product ----------------- ###
class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()

    product_for_change = None


@admin_router.message(StateFilter(None), F.text == "Add product")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Enter product name.\nPress . to skip changing the name.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AddProduct.name)


@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        if 3 >= len(message.text) >= 150:
            await message.answer(
                "The product name must not exceed 150 characters or be less than 5 characters.\nPlease enter it again."
            )
            return
        await state.update_data(name=message.text)
    await message.answer(
        "Enter description.\n Press . to skip changing the description."
    )
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer("You entered invalid data, please enter the product name text")


@admin_router.message(AddProduct.description, F.text)
async def add_description(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        if 5 >= len(message.text) >= 1500:
            await message.answer(
                "The description must not exceed 1500 characters or be less than 5 characters.\nPlease enter it again."
            )
            return
        await state.update_data(description=message.text)

    categories = await orm_get_categories(session)
    btns = {category.name: str(category.id) for category in categories}
    await message.answer("Select a category", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddProduct.category)
