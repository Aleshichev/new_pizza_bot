from aiogram import F, Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard
from kbds.inline import get_callback_btns

from database.orm_query.product import (
    orm_add_product,
    orm_update_product,
    orm_get_products,
    orm_get_product,
)
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

#--------------- Main menu --------------- #

@admin_router.message(Command("admin"))
async def admin_features(message: types.Message, state: FSMContext):
    await state.set_state(None)
    await message.answer("Hi! What do you want to do?", reply_markup=ADMIN_KB)
    
    
@admin_router.message(F.text == 'Assortment')
async def admin_features(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category.name : f'category_{category.id}' for category in categories}
    await message.answer("Select category", reply_markup=get_callback_btns(btns=btns))


@admin_router.callback_query(F.data.startswith('category_'))
async def starting_at_product(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split('_')[-1]
    products = await orm_get_products(session, int(category_id))
    
    if not products:
        await callback.message.answer("The list of products is empty. No products.")
    else:
        for product in products:
            await callback.message.answer_photo(
                product.image,
                caption=f"<strong>{product.name}</strong>\n{product.description}\nPrice: {round(product.price, 2)}",
                reply_markup=get_callback_btns(
                    btns={
                        "Delete": f"delete_{product.id}",
                        "Edit": f"edit_{product.id}",
                    },
                    sizes=(2,)
                ),
            )
    await callback.answer()
    await callback.message.answer("The list of products ⏫")
    

### -----------------  FSM  add/edit product ----------------- ###

class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    product_for_change = None
    
@admin_router.callback_query(StateFilter(None), F.data.startswith("edit_"))
async def change_product_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]

    product_for_change = await orm_get_product(session, int(product_id))

    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        "Enter product name.\nPress . to skip changing the name. ", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter(None), F.text == "Add product")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Enter product name",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AddProduct.name)


@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        if len(message.text) <= 3 or len(message.text) >= 150:
            await message.answer(
                "The product name must not exceed 150 characters or be less than 3 characters.\nPlease enter it again."
            )
            return
        await state.update_data(name=message.text)
    await message.answer(
        "Enter description.\nPress . to skip changing the description."
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
        if len(message.text) <= 5 or len(message.text) >= 1500:
            await message.answer(
                "The description must not exceed 1500 characters or be less than 5 characters.\nPlease enter it again."
            )
            return
        await state.update_data(description=message.text)

    categories = await orm_get_categories(session)
    btns = {category.name: str(category.id) for category in categories}
    await message.answer("Select a category", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddProduct.category)


@admin_router.message(AddProduct.description)
async def add_description2(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await message.answer(
        "You entered invalid data, please enter the product description text"
    )

@admin_router.callback_query(AddProduct.category)
async def category_choice(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    if int(callback.data) in [
        category.id for category in await orm_get_categories(session)
    ]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer("Enter product price.\nPress . to skip changing the price.")
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer("Select a category from buttons 1")
        await callback.answer()


@admin_router.message(AddProduct.category, F.text)
async def category_choice2(
    message: types.Message,
    state: FSMContext,
):
    await message.answer("Select a category from buttons 2")
    

@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Enter the correct price value")
            return

        await state.update_data(price=message.text)
    await message.answer("Upload a product image.\nPress . to skip changing the image.")
    await state.set_state(AddProduct.image)

@admin_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer("You have entered invalid data, please enter the cost of the product.")

@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == "." and AddProduct.product_for_change:
        await state.update_data(image=AddProduct.product_for_change.image)

    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer("Send a photo of the product")
        return
    data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(session, data)
        await message.answer("Product added/changed", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(
            f"Error: \n{str(e)}\nContact the programmer",
            reply_markup=ADMIN_KB,
        )
        await state.clear()

    AddProduct.product_for_change = None

@admin_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer("Send a photo of the product")