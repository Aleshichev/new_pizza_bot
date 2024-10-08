from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from language.kbds import CATALOG, CART, ABOUT, PAYMENT, HISTORY, MAIN, BUY, DELETE, ORDER

class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None


def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        CATALOG: "catalog",
        CART: "cart",
        ABOUT: "about",
        PAYMENT: "payment",
        HISTORY: "history",
    }
    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == 'cart':
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=3, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()))
            
    return keyboard.adjust(*sizes).as_markup()


def get_user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                callback_data=MenuCallBack(level=level+1, menu_name=c.name, category=c.id).pack()))
        
    keyboard.add(InlineKeyboardButton(text=MAIN,
                callback_data=MenuCallBack(level=level-1, menu_name='main').pack()))
    keyboard.add(InlineKeyboardButton(text=CART,
                callback_data=MenuCallBack(level=3, menu_name='cart').pack()))
    

    return keyboard.adjust(*sizes).as_markup()

def get_products_btns(
    *,
    level: int,
    category: int,
    page: int,
    pagination_btns: dict,
    product_id: int,
    sizes: tuple[int] = (2, 2, 1)
):
    keyboard = InlineKeyboardBuilder()

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        category=category,
                        page=page + 1).pack()))
        
        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        category=category,
                        page=page - 1).pack()))
    keyboard.row(*row)
    
    if len(pagination_btns) == 1:
        sizes = (1, 2)
        
    # if len(pagination_btns) > 2:
    #     sizes = (2, 2, 1)

            
    keyboard.add(InlineKeyboardButton(text=CATALOG,
                callback_data=MenuCallBack(level=level-1, menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text=BUY,
                callback_data=MenuCallBack(level=level, menu_name='add_to_cart', product_id=product_id).pack()))
    keyboard.add(InlineKeyboardButton(text=CART,
                callback_data=MenuCallBack(level=3, menu_name='cart').pack()))

    keyboard.adjust(*sizes)


    return keyboard.as_markup()

def get_user_cart(
    *,
    level: int,
    page: int | None,
    pagination_btns: dict | None,
    product_id: int | None,
    sizes: tuple[int] = (2, 2, 2, 1, 1)
):
    keyboard = InlineKeyboardBuilder()
    if page:
        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == "next":
                row.append(InlineKeyboardButton(text=text,
                        callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page + 1).pack()))
            elif menu_name == "previous":
                row.append(InlineKeyboardButton(text=text,
                        callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page - 1).pack()))

        keyboard.row(*row)
        
        if not pagination_btns:
            sizes = (2, 2, 1, 1)
            
        if len(pagination_btns) == 1:
            sizes = (1, 2, 2, 1, 1)
            
        keyboard.add(InlineKeyboardButton(text=MAIN,
                     callback_data=MenuCallBack(level=0, menu_name='main').pack()))
        keyboard.add(InlineKeyboardButton(text=DELETE,
                    callback_data=MenuCallBack(level=level, menu_name='delete', product_id=product_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='-1',
                    callback_data=MenuCallBack(level=level, menu_name='decrement', product_id=product_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='+1',
                    callback_data=MenuCallBack(level=level, menu_name='increment', product_id=product_id, page=page).pack()))

        keyboard.add(InlineKeyboardButton(text=CATALOG,
                callback_data=MenuCallBack(level=1, menu_name='catalog').pack()))
        
        keyboard.add(InlineKeyboardButton(text=ORDER,
                    callback_data=MenuCallBack(level=4, menu_name='order').pack()))
        # row2 = [
        # # InlineKeyboardButton(text='На главную 🏠',
        # #             callback_data=MenuCallBack(level=0, menu_name='main').pack()),
        # InlineKeyboardButton(text='Категории',
        #         callback_data=MenuCallBack(level=1, menu_name='catalog').pack()),
        # InlineKeyboardButton(text='Оформить Заказ 📝',
        #             callback_data=MenuCallBack(level=4, menu_name='order').pack()),
        # ]
        
        keyboard.adjust(*sizes)
        
        return keyboard.as_markup()
    else:
        keyboard.add(
            InlineKeyboardButton(text=MAIN,
                    callback_data=MenuCallBack(level=0, menu_name='main').pack()))
        
        return keyboard.adjust(*sizes).as_markup()


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()