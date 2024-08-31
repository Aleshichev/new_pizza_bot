from aiogram import F, Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard
from kbds.inline import get_callback_btns
from database.orm_query.banner import (
    orm_get_info_pages,
    orm_change_banner_image,
)
from database.orm_query.product import (
    orm_add_product,
    orm_update_product,
    orm_get_products,
    orm_get_product,
    orm_delete_product,
)
from database.orm_query.category import (
    orm_get_categories,
)
from language.admin_handler import *


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    ADD_PRODUCT,
    ASSORTMENT,
    EDIT_BANNER,
    placeholder=ACTION,
    sizes=(2,),
)

# --------------- Main menu --------------- #


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message, state: FSMContext):
    await state.set_state(None)
    await message.answer(WELCOME, reply_markup=ADMIN_KB)


@admin_router.message(F.text == ASSORTMENT)
async def admin_features(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    await message.answer(SELECT_CATEGORY, reply_markup=get_callback_btns(btns=btns))


@admin_router.callback_query(F.data.startswith("category_"))
async def starting_at_product(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split("_")[-1]
    products = await orm_get_products(session, int(category_id))

    if not products:
        await callback.message.answer(EMPTY_LIST)
    else:
        for product in products:
            await callback.message.answer_photo(
                product.image,
                caption=f"<strong>{product.name}</strong>\n{product.description}\nPrice: {round(product.price, 2)}",
                reply_markup=get_callback_btns(
                    btns={
                        DELETE: f"delete_{product.id}",
                        EDIT: f"edit_{product.id}",
                    },
                    sizes=(2,),
                ),
            )
    await callback.answer()
    await callback.message.answer(LIST)


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))

    await callback.answer(DELETE_PROD)
    await callback.message.answer(DELETE_PROD)


# ---------- Micro FSM for Uploading/Modifying Banners -------------------#


class AddBanner(StatesGroup):
    image = State()


@admin_router.message(StateFilter(None), F.text == EDIT_BANNER)
async def add_image2(message: types.Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(
        f"Надішліть фото банера.\nУ підписі вкажіть сторінку:\n{', '.join(pages_names)}"
    )
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(
            f"Введіть дійсну назву сторінки, наприклад:\n{', '.join(pages_names)}"
        )
        return
    await orm_change_banner_image(
        session,
        for_page,
        image_id,
    )
    await message.answer(ADDED_BANNER)
    await state.clear()


@admin_router.message(AddBanner.image)
async def add_banner2(message: types.Message, state: FSMContext):
    if message.text.casefold() == "cancel":
        await state.clear()
        await message.answer(ACTION_CANCELED, reply_markup=ADMIN_KB)
    else:
        await message.answer(SEND_PHOTO_OR_CANCEL)


### -----------------  FSM  add/edit product ----------------- ###


class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    product_for_change = None

    texts = TEXT


@admin_router.callback_query(StateFilter(None), F.data.startswith("edit_"))
async def change_product_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]

    product_for_change = await orm_get_product(session, int(product_id))

    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        ENTER_PROD_NAME_OR,
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter(None), F.text == ADD_PRODUCT)
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        ENTER_PROD_NAME,
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter("*"), Command("cancel"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "cancel")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await state.clear()
    await message.answer(CANCELED, reply_markup=ADMIN_KB)


@admin_router.message(StateFilter("*"), Command("back"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "back")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await message.answer(
            PREVIOUS_STEP
        )
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Гаразд, ви повернулися до попереднього кроку \n {AddProduct.texts[previous.state]}"
            )
            return
        previous = step


@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        if len(message.text) <= 3 or len(message.text) >= 150:
            await message.answer(
                VALUE_PRODUCT_NAME
                )
            return
        await state.update_data(name=message.text)
    await message.answer(
        DESCRIPTION
    )
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer(INVALID_DATA)


@admin_router.message(AddProduct.description, F.text)
async def add_description(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        if len(message.text) <= 5 or len(message.text) >= 1500:
            await message.answer(
                VALID_DESCRIPTION
            )
            return
        await state.update_data(description=message.text)

    categories = await orm_get_categories(session)
    btns = {category.name: str(category.id) for category in categories}
    await message.answer(SELECT_CATEGORY, reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddProduct.category)


@admin_router.message(AddProduct.description)
async def add_description2(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await message.answer(
        INVALID_DESCRIPTION
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
        await callback.message.answer(
            PRODUCT_PRICE
        )
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer(SELECT_BUTTON_1)
        await callback.answer()


@admin_router.message(AddProduct.category, F.text)
async def category_choice2(
    message: types.Message,
    state: FSMContext,
):
    await message.answer(SELECT_BUTTON_2)


@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer(CORRECT_PRICE)
            return

        await state.update_data(price=message.text)
    await message.answer(UPLOAD_IMAGE)
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer(
        INVALID_DATA
    )


@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == "." and AddProduct.product_for_change:
        await state.update_data(image=AddProduct.product_for_change.image)

    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer(SEND_PHOTO)
        return
    data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(session, data)
        await message.answer(ADDED_PRODUCT, reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(
            f"Помилка: \n{str(e)}\nЗверніться до розробника"
        )
        await state.clear()

    AddProduct.product_for_change = None


@admin_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer(SEND_PHOTO)
