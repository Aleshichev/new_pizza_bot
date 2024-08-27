import asyncio

from aiogram import F, types, Router
from aiogram.filters import CommandStart
from filters.chat_types import ChatTypeFilter
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from database.models import User
from kbds.inline import MenuCallBack, get_callback_btns
from handlers.menu_processing import get_menu_content
from database.orm_query.cart import orm_add_to_cart
from database.orm_query.user import orm_add_user, orm_get_user
from kbds.reply import get_phone_kb

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


# Определяем состояния
class UserState(StatesGroup):
    name = State()
    phone = State()


# Обработчик команды /start
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession, state: FSMContext):

    user = await orm_get_user(session, user_id=message.from_user.id)

    if user:
        # Пользователь найден, пропускаем регистрацию и переходим к меню
        media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
        return await message.answer_photo(
            media.media, caption=media.caption, reply_markup=reply_markup
        )
    bot_message = await message.answer(
        "Привет! Давай начнём регистрацию.\nКак к вам обращаться?"
    )
    await state.update_data(bot_message_id=bot_message.message_id)
    await state.set_state(UserState.name)
    await message.delete()


@user_private_router.message(UserState.name)
async def process_name(message: types.Message, state: FSMContext):
    # Получаем сохранённое сообщение бота
    user_data = await state.get_data()
    bot_message_id = user_data.get("bot_message_id")

    # Сохраняем имя
    await state.update_data(name=message.text)

    await message.bot.delete_message(chat_id=message.chat.id, message_id=bot_message_id)
    await message.delete()

    # Запрашиваем телефон
    phone_kb = get_phone_kb()

    phone_message = await message.answer("Поделится номером телефона:", reply_markup=phone_kb)
    
    await state.update_data(phone_message_id=phone_message.message_id)  # Сохраняем ID сообщения с запросом телефона
    await state.set_state(UserState.phone)


@user_private_router.message(UserState.phone)
async def process_phone(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    # Проверяем, что контакт получен
    if message.contact is None or message.contact.user_id != message.from_user.id:
        await message.answer(
            "Пожалуйста, используйте кнопку для отправки своего номера телефона."
        )
        return

    # Получаем данные
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
    # Очищаем состояние
    await state.clear()

    # Удаляем клавиатуру
    sent_message = await message.answer("Спасибо за регистрацию!", reply_markup=types.ReplyKeyboardRemove())
    # await message.edit_reply_markup(reply_markup=None)
    await message.delete()
    phone_message_id = user_data.get("phone_message_id")
    if phone_message_id:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=phone_message_id)
        
    await asyncio.sleep(2)

    # Удаление сообщения
    await sent_message.delete()
    

    # Запускаем следующий хендлер для отображения меню
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    await message.answer_photo(
        media.media, caption=media.caption, reply_markup=reply_markup
    )


# @user_private_router.message(CommandStart())
# async def start_cmd(message: types.Message, session: AsyncSession):

#     media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
#     await message.answer_photo(
#         media.media, caption=media.caption, reply_markup=reply_markup
#     )


async def add_to_cart(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):
    user = callback.from_user
    # await orm_add_user(
    #     session,
    #     user_id=user.id,
    #     first_name=user.first_name,
    #     last_name=user.last_name,
    #     phone=None,
    # )
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer("Товар добавлен в корзину.", show_alert=True)


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
