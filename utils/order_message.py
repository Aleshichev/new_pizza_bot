from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query.cart import orm_get_user_carts
from database.orm_query.user import orm_get_user


async def order_message(session: AsyncSession, user_id: int, order_time: str):
    carts = await orm_get_user_carts(session, user_id)
    if carts:
        user = await orm_get_user(session, user_id)

        last_name_display = f"{user.last_name}" if user.last_name else ""
        user_message = f"Имя: <strong>{user.user_name} </strong>.\
                            \nВремя: <strong>{order_time}</strong>\
                            \nТелефон: <strong>{user.phone}</strong>\
                            \nНик в телеграмме: <strong>{user.first_name} {last_name_display.strip()}</strong>\
                            \n\n------------------- Заказ: -------------------"
        cart_messages = []
        if carts:
            total_price = 0
            for cart in carts:
                cart_price = round(cart.quantity * cart.product.price, 2)
                total_price += cart_price
                cart_message = (
                    f"Товар: <strong>{cart.product.name}</strong>"
                    f"\nЦена: <strong>{cart.product.price}</strong> грн"
                    f"\nКоличество: <strong>{cart.quantity}</strong> ед."
                )
                cart_messages.append(cart_message)

            cart_messages.append(
                f"------------------- Корзина ---------------------"
                f"\n\nВ заказе <strong>{len(carts)}</strong> товаров"
                f"\nСтоимость всего заказа <strong>{total_price}</strong> грн"
            )
        # full_message = user_message + "\n\n" + "\n\n".join(cart_messages)

        return user_message + "\n\n" + "\n\n".join(cart_messages)

    return None
