from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType
def get_keyboard(
    *btns: str,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: tuple[int] = (2, ),
    ):
    
    keyboard = ReplyKeyboardBuilder()
    
    
    for index, text in enumerate(btns, start=0):
        
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
            resize_keyboard=True, input_field_placeholder=placeholder, one_time_keyboard=True)
    
    
def get_phone_kb() -> ReplyKeyboardMarkup:

    builder = ReplyKeyboardBuilder()
    builder.button(
        text="☎️ Поделиться телефоном",
        request_contact=True,
    )
    builder.adjust(1)
    return builder.as_markup(
        input_field_placeholder="Нажмите на кнопку",
        resize_keyboard=True,
    )