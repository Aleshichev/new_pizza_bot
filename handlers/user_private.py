import asyncio
import os
from aiogram.exceptions import TelegramBadRequest
from aiogram import F, types, Router
from aiogram.filters import CommandStart
from filters.chat_types import ChatTypeFilter
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

from kbds.inline import MenuCallBack
from handlers.menu_processing import get_menu_content
from database.orm_query.cart import orm_add_to_cart, orm_delete_from_carts
from database.orm_query.user import orm_add_user, orm_get_user
from kbds.reply import get_phone_kb
from utils.order_message import order_message
from language.user_private_handler import (
    ACQUANTANCE,
    SHARE_PHONE,
    TAP_BUTTON,
    REGISTRATION,
    TIME_ORDER,
    EMPTY_ORDER,
    ERROR_TIME,
    ADDED_GOODS,
)

load_dotenv()

CHAT_GROUP_ID = os.getenv("CHAT_GROUP_ID")

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


class UserState(StatesGroup):
    name = State()
    phone = State()
    order_time = State()


# ----------------- Start / FSM Registration ----------------- #
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession, state: FSMContext):

    user = await orm_get_user(session, user_id=message.from_user.id)
    await message.delete()

    if user:
        media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
        return await message.answer_photo(
            media.media, caption=media.caption, reply_markup=reply_markup
        )
    bot_message = await message.answer(
        ACQUANTANCE
    )
    await state.update_data(bot_message_id=bot_message.message_id)
    await state.set_state(UserState.name)
    await message.delete()


@user_private_router.message(UserState.name)
async def process_name(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    bot_message_id = user_data.get("bot_message_id")

    await state.update_data(name=message.text)

    await message.bot.delete_message(chat_id=message.chat.id, message_id=bot_message_id)
    await message.delete()

    phone_kb = get_phone_kb()

    phone_message = await message.answer(
        SHARE_PHONE,
        reply_markup=phone_kb,
    )

    await state.update_data(phone_message_id=phone_message.message_id)
    await state.set_state(UserState.phone)


@user_private_router.message(UserState.phone)
async def process_phone(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.contact is None or message.contact.user_id != message.from_user.id:
        await message.answer(
            TAP_BUTTON
        )
        return

    user_data = await state.get_data()
    name = user_data.get("name")
    phone_number = message.contact.phone_number

    await orm_add_user(
        session,
        user_id=message.from_user.id,
        user_name=name,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        phone=phone_number,
    )
    await state.clear()

    sent_message = await message.answer(
        REGISTRATION, reply_markup=types.ReplyKeyboardRemove()
    )
    await message.delete()
    phone_message_id = user_data.get("phone_message_id")
    if phone_message_id:
        await message.bot.delete_message(
            chat_id=message.chat.id, message_id=phone_message_id
        )

    await asyncio.sleep(2)

    await sent_message.delete()

    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    await message.answer_photo(
        media.media, caption=media.caption, reply_markup=reply_markup
    )


#################################################################################

#### ------------------ FSM order -------------------------------###########


@user_private_router.callback_query(MenuCallBack.filter(F.menu_name == "order"))
async def process_order(callback: types.CallbackQuery, state: FSMContext):
    time_question = await callback.message.answer(
        TIME_ORDER
    )
    await state.update_data(bot_message_id=time_question.message_id)

    await state.set_state(UserState.order_time)
    await callback.answer()


@user_private_router.message(UserState.order_time)
async def process_order_time(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    order_time = message.text
    user_data = await state.get_data()
    bot_message_id = user_data.get("bot_message_id")
    error_message_id = user_data.get("error_message_id")
    if error_message_id:
        await message.bot.delete_message(
            chat_id=message.chat.id, message_id=error_message_id
        )
    if bot_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=bot_message_id
            )
        except TelegramBadRequest:
            pass
    if (
        len(order_time) == 5
        and order_time[2] == ":"
        and order_time[:2].isdigit()
        and order_time[3:].isdigit()
    ):
        await state.update_data(order_time=order_time)
        await state.clear()
        
        
        user_id = message.from_user.id  
        
        full_message = await order_message(session, user_id, order_time)
        
        if full_message is None:
            main_page_message = await message.answer(
            EMPTY_ORDER)
            await message.delete()
            await asyncio.sleep(15)
            await main_page_message.delete()
        else:
            await message.bot.send_message(CHAT_GROUP_ID, full_message)

            confirm_message = await message.answer(
                f"Ваше замовлення буде готове о {order_time}. Дякуємо!\nГарного дня!"
            )

            await state.clear()
            await asyncio.sleep(5)
            await message.delete()
            await confirm_message.delete()
            await orm_delete_from_carts(session, user_id)


    else:
        await message.delete()
        error_message = await message.answer(
            ERROR_TIME
        )
        await state.update_data(error_message_id=error_message.message_id)


###############################################################################


async def add_to_cart(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):
    user = callback.from_user
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer(ADDED_GOODS, show_alert=True)


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(
    callback: types.CallbackQuery,
    callback_data: MenuCallBack,
    session: AsyncSession,
    state: FSMContext,
):
    if callback_data.menu_name == "add_to_cart":
        await add_to_cart(callback, callback_data, session)
        return

    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()
